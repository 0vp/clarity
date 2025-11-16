import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { BrandData } from '@/lib/api'
import { getSentimentLabel, getSentimentColor, formatScore } from '../lib/chart-utils'
import { ExternalLink } from 'lucide-react'

interface RecentMentionsProps {
  data: BrandData[]
}

export function RecentMentions({ data }: RecentMentionsProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  const getSourceIcon = (source: string) => {
    const icons: Record<string, string> = {
      trustpilot: '⭐',
      yelp: '🍽️',
      google_reviews: '🔍',
      news: '📰',
      blog: '📝',
      forum: '💬',
      website: '🌐',
    }
    return icons[source] || '📄'
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Mentions</CardTitle>
        <CardDescription>Latest reputation entries</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {data.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No recent mentions available
            </p>
          ) : (
            data.map((entry, index) => (
              <div
                key={index}
                className="flex items-start gap-4 rounded-lg border p-4 hover:bg-accent transition-colors"
              >
                <div className="text-2xl">{getSourceIcon(entry.source_type)}</div>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="capitalize">
                      {entry.source_type.replace(/_/g, ' ')}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {formatDate(entry.date)}
                    </span>
                    <Badge
                      variant="secondary"
                      className={getSentimentColor(entry.reputation_score)}
                    >
                      {getSentimentLabel(entry.reputation_score)} ({formatScore(entry.reputation_score)})
                    </Badge>
                  </div>
                  <p className="text-sm">{entry.summary}</p>
                  {entry.source_url && entry.source_url !== '' && (
                    <a
                      href={entry.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
                    >
                      View Source <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}
