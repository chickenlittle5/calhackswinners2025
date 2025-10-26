import type { Metadata } from "next";
import { JetBrains_Mono, Crimson_Pro } from "next/font/google";
import "./globals.css";

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  weight: ["400", "600", "700"],
});

const crimsonPro = Crimson_Pro({
  subsets: ["latin"],
  variable: "--font-crimson",
  weight: ["400", "600", "700"],
});

export const metadata: Metadata = {
  title: "TrialSync - Clinical Trial Recruitment Platform",
  description: "AI-powered clinical trial matching and recruitment management system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${jetbrainsMono.variable} ${crimsonPro.variable}`}>
      <body className="min-h-screen antialiased">
        <div className="bg-pattern" />
        <div className="relative z-10">
          {children}
        </div>
      </body>
    </html>
  );
}