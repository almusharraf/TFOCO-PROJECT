import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'TFOCO - Financial Document Reader',
  description: 'AI-powered Named Entity Recognition for financial documents',
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

