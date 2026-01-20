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
  title: "Glass Box Portfolio",
  description:
    "A production-grade demonstration of explainable, agentic systems. Toggle between polished UX and transparent engineering view.",
  openGraph: {
    title: "Glass Box Portfolio",
    description:
      "Explore how modern AI systems actually behave in production with transparent visibility into agent decisions.",
    type: "website",
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
