import logging

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
)
from livekit.plugins import noise_cancellation, silero, hume
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents import AgentTask, function_tool
from livekit.agents import get_job_context
from transcribe import get_transcript_manager

logger = logging.getLogger("agent")

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful voice AI assistant. 
            The patient is interacting with you via voice, even if you perceive the conversation as text.
            Your purpose is to determine the eligbility of patients for clinical trials. 
            You will ask questions to the user for the following information: First Name, Last Name, Date of Birth, Gender, Age, Contact Email, Phone Number, Location, currently diagnosed conditions, current medications, and a summary of their current condition
            Ask questions for one field at a time. If the user's response is incomprehensible or doesn't make sense for the question (e.g. "I'm Asian" for "What is your name?" or a 20 digit phone number or an email without a domain), then repeat the question again until you receive a reasonable response.
            For emails, assume "at" is equivalent to "@".
            After this, please repeat what you think they said and have them confirm.
            However, be patient towards patients and don't rush or be rude towards them.
            Your responses are concise, to the point, and without any complex formatting or punctuation including emojis, asterisks, or other symbols.
            You are friendly but to the point.""",
        )

    async def on_enter(self) -> None:
        if await CollectConsent(chat_ctx=self.chat_ctx):
            await self.session.generate_reply(instructions="Offer your assistance to the user.")
        else:
            await self.session.generate_reply(instructions="Inform the user that you are unable to proceed and will end the call.")
            # Wait for the goodbye message to finish playing before disconnecting
            # await asyncio.sleep(3)
            job_ctx = get_job_context()
            # Disconnect from the room to end the call
            await job_ctx.room.disconnect()

    # To add tools, use the @function_tool decorator.
    # Here's an example that adds a simple weather tool.
    # You also have to add `from livekit.agents import function_tool, RunContext` to the top of this file
    # @function_tool
    # async def lookup_weather(self, context: RunContext, location: str):
    #     """Use this tool to look up current weather information in the given location.
    #
    #     If the location is not supported by the weather service, the tool will indicate this. You must tell the user the location's weather is unavailable.
    #
    #     Args:
    #         location: The location to look up weather information for (e.g. city name)
    #     """
    #
    #     logger.info(f"Looking up weather for {location}")
    #
    #     return "sunny with a temperature of 70 degrees."


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt="assemblyai/universal-streaming:en",
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm="openai/gpt-4.1-mini",
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts="cartesia/sonic-2:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        # tts=hume.TTS(
        #     voice=hume.VoiceByName(name="Colton Rivers", provider=hume.VoiceProvider.hume),
        #     description="The voice exudes calm, serene, and peaceful qualities, like a gentle stream flowing through a quiet forest.",
        # ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    # Get transcript manager and set metadata
    transcript_mgr = get_transcript_manager()
    transcript_mgr.set_metadata(room_name=ctx.room.name)

    # Capture both user and agent messages when added to chat history
    @session.on("conversation_item_added")
    def _on_conversation_item_added(ev):
        logger.info(f"Event fired! Event: {ev}")
        logger.info(f"Item: {ev.item}")
        logger.info(f"Item role: {ev.item.role}")
        logger.info(f"Item content: {ev.item.content}")

        # Extract text content from the chat message
        message_text = ""
        for content in ev.item.content:
            logger.info(f"Content item: {content}, Type: {type(content)}")
            if hasattr(content, 'text'):
                message_text += content.text
            # Also try alternative attribute names
            elif hasattr(content, 'content'):
                message_text += str(content.content)
            elif isinstance(content, str):
                message_text += content

        role = ev.item.role
        logger.info(f"Extracted message_text: '{message_text}', role: '{role}'")

        if message_text:
            logger.info(f"{role} said: {message_text}")
            transcript_mgr.add_message(role=role, content=message_text)
        else:
            logger.warning(f"No text extracted from conversation item!")

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    # Save conversation transcript when session ends
    async def save_transcript():
        # Step 1: Save transcript to JSON file
        filepath = transcript_mgr.save_to_file()
        logger.info(f"Transcript saved to {filepath} with {len(transcript_mgr.transcript)} messages")

        # Step 2: Parse transcript and save to Supabase database
        try:
            logger.info("Starting transcript parsing and database save...")
            result = transcript_mgr.parse_and_save_to_db(filepath)

            if result and result.get("success"):
                patient_id = result.get("patient_id")
                logger.info(f"✅ Successfully parsed and saved patient data. Patient ID: {patient_id}")
            else:
                error = result.get("error", "Unknown error") if result else "No result returned"
                logger.error(f"❌ Failed to parse and save: {error}")
        except Exception as e:
            logger.error(f"❌ Error during parse_and_save_to_db: {e}", exc_info=True)

    ctx.add_shutdown_callback(log_usage)
    ctx.add_shutdown_callback(save_transcript)

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()

class CollectConsent(AgentTask[bool]):
    def __init__(self, chat_ctx=None):
        super().__init__(
            instructions="""
            Ask for recording consent and get a clear yes or no answer.
            Be polite and professional.
            """,
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        await self.session.say("Hello! Can you hear me?")
        await self.session.generate_reply(
            instructions="""
            Briefly introduce yourself, then ask for permission to record the call for quality assurance and training purposes.
            Make it clear that they can decline.
            """
        )

    @function_tool
    async def consent_given(self) -> None:
        """Use this when the user gives consent to record."""
        self.complete(True)

    @function_tool
    async def consent_denied(self) -> None:
        """Use this when the user denies consent to record."""
        self.complete(False)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, agent_name="my-telephony-agent", prewarm_fnc=prewarm))
