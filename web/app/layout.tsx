import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Glass Box Portfolio',
  description: 'A production-grade demonstration of explainable, agentic systems',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
