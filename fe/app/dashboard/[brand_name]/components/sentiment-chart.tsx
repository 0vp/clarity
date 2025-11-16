'use client'

import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from 'recharts'
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
import { SentimentDistribution } from '../lib/chart-utils'

interface SentimentChartProps {
  distribution: SentimentDistribution
}

const chartConfig = {
  positive: {
    label: 'Positive',
    color: 'hsl(142, 76%, 36%)',
  },
  neutral: {
    label: 'Neutral',
    color: 'hsl(45, 93%, 47%)',
  },
  negative: {
    label: 'Negative',
    color: 'hsl(0, 84%, 60%)',
  },
} satisfies ChartConfig

export function SentimentChart({ distribution }: SentimentChartProps) {
  const data = [
    { sentiment: 'Positive', count: distribution.positive, fill: 'var(--color-positive)' },
    { sentiment: 'Neutral', count: distribution.neutral, fill: 'var(--color-neutral)' },
    { sentiment: 'Negative', count: distribution.negative, fill: 'var(--color-negative)' },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sentiment Distribution</CardTitle>
        <CardDescription>Breakdown of sentiment scores</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="min-h-[300px] w-full">
          <BarChart
            data={data}
            margin={{
              left: 12,
              right: 12,
              top: 12,
              bottom: 12,
            }}
          >
            <CartesianGrid vertical={false} strokeDasharray="3 3" />
            <XAxis
              dataKey="sentiment"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
            />
            <YAxis
              tickLine={false}
              axisLine={false}
              tickMargin={8}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
            />
            <Bar dataKey="count" radius={8} />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
