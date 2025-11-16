'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ArrowLeft, Activity, MessageSquare, TrendingUp, Database } from 'lucide-react'
import { 
  fetchBrandStats, 
  fetchBrandDataRange, 
  fetchBrandLatestData,
  BrandData,
  BrandStats 
} from '@/lib/api'
import { 
  processTimeSeriesData, 
  calculateSentimentDistribution, 
  processSourceBreakdown,
  formatScore 
} from './lib/chart-utils'
import { StatCard } from './components/stat-card'
import { ReputationTrend } from './components/reputation-trend'
import { SourceBreakdown } from './components/source-breakdown'
import { SentimentChart } from './components/sentiment-chart'
import { SourceRadar } from './components/source-radar'
import { RecentMentions } from './components/recent-mentions'
import { Skeleton } from '@/components/ui/skeleton'

export const dynamic = 'force-dynamic'

type TimeRange = '7' | '30' | '90' | 'all'

export default function BrandPage() {
  const params = useParams()
  const brandName = decodeURIComponent(params.brand_name as string)
  
  const [timeRange, setTimeRange] = useState<TimeRange>('30')
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<BrandStats | null>(null)
  const [historicalData, setHistoricalData] = useState<BrandData[]>([])
  const [recentMentions, setRecentMentions] = useState<BrandData[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadData() {
      if (typeof window === 'undefined') return
      
      try {
        setLoading(true)
        setError(null)

        const days = timeRange === 'all' ? 365 : parseInt(timeRange)
        
        const [statsData, historicalDataResult, recentData] = await Promise.all([
          fetchBrandStats(brandName),
          fetchBrandDataRange(brandName, days),
          fetchBrandLatestData(brandName, 10)
        ])

        setStats(statsData)
        setHistoricalData(historicalDataResult)
        setRecentMentions(recentData)
      } catch (err) {
        console.error('Error loading brand data:', err)
        setError(err instanceof Error ? err.message : 'Failed to load data')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [brandName, timeRange])

  const timeSeriesData = historicalData.length > 0 ? processTimeSeriesData(historicalData) : []
  const sentimentDistribution = historicalData.length > 0 ? calculateSentimentDistribution(historicalData) : { positive: 0, neutral: 0, negative: 0 }
  const sourceBreakdown = stats ? processSourceBreakdown(stats) : []

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

        {/* Page Header with Time Range Selector */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">{brandName}</h1>
            <p className="text-muted-foreground">Brand reputation data and analytics</p>
          </div>
          <Tabs value={timeRange} onValueChange={(v) => setTimeRange(v as TimeRange)}>
            <TabsList>
              <TabsTrigger value="7">7 days</TabsTrigger>
              <TabsTrigger value="30">30 days</TabsTrigger>
              <TabsTrigger value="90">90 days</TabsTrigger>
              <TabsTrigger value="all">All time</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {error ? (
          <div className="text-center py-12">
            <p className="text-destructive mb-4">{error}</p>
            <Button onClick={() => window.location.reload()}>Retry</Button>
          </div>
        ) : loading ? (
          <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {[1, 2, 3, 4].map(i => (
                <Skeleton key={i} className="h-[120px]" />
              ))}
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              {[1, 2].map(i => (
                <Skeleton key={i} className="h-[400px]" />
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Overview Stats */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <StatCard
                title="Overall Score"
                value={stats ? formatScore(stats.average_score) : 'N/A'}
                icon={Activity}
                description={stats ? `${stats.total_entries} total entries` : ''}
              />
              <StatCard
                title="Total Mentions"
                value={stats?.total_entries || 0}
                icon={MessageSquare}
                description="Across all sources"
              />
              <StatCard
                title="Positive Sentiment"
                value={`${sentimentDistribution.positive}`}
                icon={TrendingUp}
                description={`${((sentimentDistribution.positive / (stats?.total_entries || 1)) * 100).toFixed(1)}% of total`}
              />
              <StatCard
                title="Active Sources"
                value={stats ? Object.keys(stats.by_source || {}).length : 0}
                icon={Database}
                description="Data sources tracking"
              />
            </div>

            {/* Primary Charts */}
            <div className="grid gap-4 md:grid-cols-2">
              <ReputationTrend data={timeSeriesData} />
              <SourceBreakdown data={sourceBreakdown} />
            </div>

            {/* Detailed Analysis */}
            <div className="grid gap-4 md:grid-cols-2">
              <SentimentChart distribution={sentimentDistribution} />
              <SourceRadar data={sourceBreakdown} />
            </div>

            {/* Recent Mentions */}
            <RecentMentions data={recentMentions} />
          </div>
        )}
      </main>
    </div>
  )
}
