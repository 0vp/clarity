'use client'

import { Pie, PieChart, Cell, Legend } from 'recharts'
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

interface SourceBreakdownProps {
  data: SourceChartData[]
}

export function SourceBreakdown({ data }: SourceBreakdownProps) {
  // Build chart config dynamically from data
  const chartConfig = data.reduce((acc, item) => {
    acc[item.source] = {
      label: item.source.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      color: item.fill,
    }
    return acc
  }, {} as ChartConfig)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Source Distribution</CardTitle>
        <CardDescription>Mentions by source</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="min-h-[300px] w-full">
          <PieChart>
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
            />
            <Pie
              data={data}
              dataKey="count"
              nameKey="source"
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={2}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Pie>
            <Legend
              verticalAlign="bottom"
              height={36}
              formatter={(value) => {
                return value.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())
              }}
            />
          </PieChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
