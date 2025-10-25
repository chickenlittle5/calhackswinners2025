import os
import re
import webbrowser
import time
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def save_html(html_content):
    os.makedirs("html_outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"html_outputs/{timestamp}.html"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    return filepath


def extract_html(text):
    pattern = r"```(?:html)?\s*(.*?)\s*```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[0] if matches else None


def open_in_browser(filepath):
    abs_path = Path(filepath).resolve()
    webbrowser.open(f"file://{abs_path}")
    print(f"🌐 Opened in browser: {filepath}")


def generate_html_with_claude(system_prompt, user_prompt):
    print("🚀 Generating HTML...\n")

    full_response = ""
    start_time = time.time()

    with client.messages.stream(
        model="claude-sonnet-4-5-20250929",
        max_tokens=64000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for text in stream.text_stream:
            full_response += text
            print(text, end="", flush=True)

    elapsed = time.time() - start_time
    print(f"\n\n✅ Complete in {elapsed:.1f}s\n")

    html_content = extract_html(full_response)
    if html_content is None:
        print("❌ Error: Could not extract HTML from response.")
        raise ValueError("Failed to extract HTML from Claude's response.")

    filepath = save_html(html_content)
    print(f"💾 HTML saved to: {filepath}")
    open_in_browser(filepath)

    return filepath

DISTILLED_AESTHETICS_PROMPT = """
<frontend_aesthetics>
You tend to converge toward generic, "on distribution" outputs. In frontend design, this creates what users call the "AI slop" aesthetic. Avoid this: make creative, distinctive frontends that surprise and delight. Focus on:

Typography: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics.

Color & Theme: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes. Draw from IDE themes and cultural aesthetics for inspiration.

Motion: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. 

Backgrounds: Create atmosphere and depth rather than defaulting to solid colors. Layer CSS gradients, use geometric patterns, or add contextual effects that match the overall aesthetic.

Avoid generic AI-generated aesthetics:
- Overused font families (Inter, Roboto, Arial, system fonts)
- Clichéd color schemes (particularly purple gradients on white backgrounds)
- Predictable layouts and component patterns
- Cookie-cutter design that lacks context-specific character

Interpret creatively and make unexpected choices that feel genuinely designed for the context. Vary between light and dark themes, different fonts, different aesthetics. You still tend to converge on common choices (Space Grotesk, for example) across generations. Avoid this: it is critical that you think outside the box!
</frontend_aesthetics>
"""

BASE_SYSTEM_PROMPT = """
You are an expert frontend engineer skilled at crafting beautiful, performant frontend applications.

<tech_stack>
Use vanilla HTML, CSS, & Javascript. Use Tailwind CSS for your CSS variables.
</tech_stack>

<output>
Generate complete, self-contained HTML code for the requested frontend application. Include all CSS and JavaScript inline. 

CRITICAL: You must wrap your HTML code in triple backticks with html language identifier like this:
```html
<!DOCTYPE html>
<html>
...
</html>
```

Our parser depends on this format - do not deviate from it!
</output>
"""

USER_PROMPT = """Create a dashboard for a clinical trial recruiting service that 
stores a table about patients and a table about the trials themselves."""

# Generate with distilled aesthetics prompt
generate_html_with_claude(
    BASE_SYSTEM_PROMPT + "\n\n" + DISTILLED_AESTHETICS_PROMPT,
    USER_PROMPT
)