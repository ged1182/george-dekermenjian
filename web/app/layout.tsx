import type { Metadata } from "next";
import { Geist, Geist_Mono, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { GlassBoxProvider } from "@/components/glass-box";
import { TooltipProvider } from "@/components/ui/tooltip";

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-sans",
});

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Glass Box Portfolio | George Dekermenjian",
  description:
    "A production-grade demonstration of explainable, agentic systems. Toggle between polished UX and transparent engineering view showing real-time agent reasoning.",
  keywords: [
    "AI portfolio",
    "explainable AI",
    "agentic systems",
    "pydantic-ai",
    "Next.js",
    "FastAPI",
    "Gemini",
    "George Dekermenjian",
  ],
  authors: [{ name: "George Dekermenjian" }],
  openGraph: {
    title: "Glass Box Portfolio | Explainable AI Systems",
    description:
      "Explore how modern AI systems actually behave in production. Toggle between polished UX and transparent engineering view showing real-time agent reasoning, tool calls, and performance metrics.",
    type: "website",
    siteName: "Glass Box Portfolio",
  },
  twitter: {
    card: "summary_large_image",
    title: "Glass Box Portfolio | Explainable AI Systems",
    description:
      "See how modern AI agents actually work. Transparent visibility into reasoning, tool selection, and performance.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={jetbrainsMono.variable}>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <TooltipProvider>
          <GlassBoxProvider>{children}</GlassBoxProvider>
        </TooltipProvider>
      </body>
    </html>
  );
}
