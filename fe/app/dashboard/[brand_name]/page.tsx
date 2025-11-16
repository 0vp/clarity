'use client'

import { useParams } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowLeft } from 'lucide-react'

export default function BrandPage() {
  const params = useParams()
  const brandName = decodeURIComponent(params.brand_name as string)

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/">
            <Image
              src="/logo.png"
              alt="Clarity"
              width={75}
              height={25}
              priority
              style={{ objectFit: 'contain', objectPosition: '-3px center' }}
            />
          </Link>
          <nav className="flex items-center gap-6">
            <Link href="/dashboard" className="text-sm font-medium text-foreground">
              Dashboard
            </Link>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Back Button */}
        <div className="mb-6">
          <Link href="/dashboard">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>
        </div>

        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">{brandName}</h1>
          <p className="text-muted-foreground">Brand reputation data and analytics</p>
        </div>

        {/* Placeholder Content */}
        <Card>
          <CardHeader>
            <CardTitle>Coming Soon</CardTitle>
            <CardDescription>
              Brand data visualization and detailed analytics will be displayed here.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 text-sm text-muted-foreground">
              <p>This page will include:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Reputation score trends over time</li>
                <li>Source breakdown and analysis</li>
                <li>Recent mentions and reviews</li>
                <li>Sentiment analysis</li>
                <li>Comparison metrics</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
