import type { Metadata } from 'next'
import { Noto_Serif_Display } from 'next/font/google'
import './globals.css'

const notoSerif = Noto_Serif_Display({
  subsets: ['latin'],
  style: ['italic'],
  weight: ['400', '600'],
  variable: '--font-noto-serif',
})

export const metadata: Metadata = {
  title: 'Clarity - Brand Reputation Tracker',
  description: 'Where visibility becomes brand intelligence. Transform scattered mentions into actionable reputation insights.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${notoSerif.variable} dark`}>
      <body>{children}</body>
    </html>
  )
}

