import { BrandData, BrandStats } from '@/lib/api'

export interface ChartDataPoint {
  date: string
  score: number
  count?: number
}

export interface SentimentDistribution {
  positive: number
  neutral: number
  negative: number
}

export interface SourceChartData {
  source: string
  count: number
  avgScore: number
  fill: string
}

// Process time series data for trend charts
export function processTimeSeriesData(data: BrandData[]): ChartDataPoint[] {
  // Group by date and calculate average score
  const grouped = data.reduce((acc, entry) => {
    const date = entry.date
    if (!acc[date]) {
      acc[date] = { scores: [], count: 0 }
    }
    acc[date].scores.push(entry.reputation_score)
    acc[date].count++
    return acc
  }, {} as Record<string, { scores: number[], count: number }>)

  // Calculate averages and sort by date
  return Object.entries(grouped)
    .map(([date, { scores, count }]) => ({
      date,
      score: scores.reduce((sum, s) => sum + s, 0) / scores.length,
      count
    }))
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
}

// Calculate sentiment distribution
export function calculateSentimentDistribution(data: BrandData[]): SentimentDistribution {
  const distribution = { positive: 0, neutral: 0, negative: 0 }
  
  data.forEach(entry => {
    if (entry.reputation_score >= 0.5) {
      distribution.positive++
    } else if (entry.reputation_score <= -0.5) {
      distribution.negative++
    } else {
      distribution.neutral++
    }
  })
  
  return distribution
}

// Process source breakdown for pie/bar charts
export function processSourceBreakdown(stats: BrandStats): SourceChartData[] {
  const colors = {
    trustpilot: '#3B82F6',
    yelp: '#EC4899',
    google_reviews: '#F59E0B',
    news: '#10B981',
    blog: '#8B5CF6',
    forum: '#EF4444',
    website: '#06B6D4',
    other: '#6366F1'
  }

  return Object.entries(stats.by_source || {}).map(([source, data]) => ({
    source,
    count: data.count,
    avgScore: data.avg_score,
    fill: colors[source as keyof typeof colors] || '#6366F1'
  }))
}

// Calculate trend percentage
export function calculateTrend(currentData: BrandData[], previousData: BrandData[]): number {
  if (previousData.length === 0) return 0
  
  const currentAvg = currentData.reduce((sum, d) => sum + d.reputation_score, 0) / currentData.length
  const previousAvg = previousData.reduce((sum, d) => sum + d.reputation_score, 0) / previousData.length
  
  if (previousAvg === 0) return 0
  
  return ((currentAvg - previousAvg) / Math.abs(previousAvg)) * 100
}

// Format score as percentage
export function formatScore(score: number): string {
  return `${(score * 100).toFixed(1)}%`
}

// Format score with emoji indicator
export function getScoreEmoji(score: number): string {
  if (score >= 0.7) return '🟢'
  if (score >= 0.3) return '🟡'
  if (score >= -0.3) return '🟠'
  return '🔴'
}

// Get sentiment label
export function getSentimentLabel(score: number): string {
  if (score >= 0.5) return 'Positive'
  if (score <= -0.5) return 'Negative'
  return 'Neutral'
}

// Get sentiment color
export function getSentimentColor(score: number): string {
  if (score >= 0.5) return 'text-green-500'
  if (score <= -0.5) return 'text-red-500'
  return 'text-yellow-500'
}
