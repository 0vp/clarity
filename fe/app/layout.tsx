import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Claro - Find Your Calm in the Complexity',
  description: 'Our platform handles the intricate data and workflows so you can stop firefighting and start focusing on what matters.',
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

