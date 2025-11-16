'use client'

import { PolarAngleAxis, PolarGrid, Radar, RadarChart, PolarRadiusAxis } from 'recharts'
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

const chartConfig = {
  avgScore: {
    label: 'Average Score',
    color: '#3B82F6',
  },
} satisfies ChartConfig

export function SourceRadar({ data }: SourceRadarProps) {
  const radarData = data.map(item => ({
    source: item.source.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    avgScore: item.avgScore,
  }))

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
              tick={{ fill: '#FFFFFF', fontSize: 12 }}
            />
            <PolarRadiusAxis domain={[-1, 1]} tick={{ fill: '#FFFFFF', fontSize: 10 }} />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="line" />}
            />
            <Radar
              dataKey="avgScore"
              stroke="#3B82F6"
              fill="#3B82F6"
              fillOpacity={0.6}
              strokeWidth={2}
            />
          </RadarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
