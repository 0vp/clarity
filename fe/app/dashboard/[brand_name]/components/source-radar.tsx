'use client'

import { PolarAngleAxis, PolarGrid, Radar, RadarChart, PolarRadiusAxis, Legend } from 'recharts'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart'
import { SourceChartData } from '../lib/chart-utils'

interface SourceRadarProps {
  data: SourceChartData[]
}

const sourceColors = {
  trustpilot: '#3B82F6',
  yelp: '#EC4899',
  google_reviews: '#F59E0B',
  news: '#10B981',
  blog: '#8B5CF6',
  forum: '#EF4444',
  website: '#06B6D4',
  other: '#6366F1'
}

export function SourceRadar({ data }: SourceRadarProps) {
  const radarData = data.map(item => ({
    source: item.source.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    avgScore: item.avgScore,
    fill: sourceColors[item.source as keyof typeof sourceColors] || '#6366F1',
  }))

  const chartConfig = radarData.reduce((acc, item) => {
    acc[item.source] = {
      label: item.source,
      color: item.fill,
    }
    return acc
  }, {} as ChartConfig)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Source Performance</CardTitle>
        <CardDescription>Average reputation score by source</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="min-h-[300px] w-full">
          <RadarChart data={radarData}>
            <PolarGrid />
            <PolarAngleAxis
              dataKey="source"
              tick={{ fill: 'hsl(var(--foreground))', fontSize: 12 }}
            />
            <PolarRadiusAxis domain={[-1, 1]} tick={{ fontSize: 10 }} />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="line" />}
            />
            {data.map((item, index) => (
              <Radar
                key={`radar-${index}`}
                dataKey="avgScore"
                stroke={sourceColors[item.source as keyof typeof sourceColors] || '#6366F1'}
                fill={sourceColors[item.source as keyof typeof sourceColors] || '#6366F1'}
                fillOpacity={0.25}
                strokeWidth={2}
                isAnimationActive={true}
              />
            ))}
            <Legend verticalAlign="bottom" height={36} />
          </RadarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
