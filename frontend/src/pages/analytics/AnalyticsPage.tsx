import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Users, BarChart3, GraduationCap, DollarSign } from 'lucide-react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import api from '@/lib/api'
import { formatDate, formatCurrency } from '@/lib/utils'
import type { PaginatedResponse } from '@/types'
import { PageHeader } from '@/components/layout/PageHeader'
import { StatsCard, StatsGrid } from '@/components/layout/StatsCard'
import { DataTable, type Column } from '@/components/ui/data-table'
import { Card, CardContent } from '@/components/ui/card'
import { Loading } from '@/components/ui/loading'

// ─── Types ───────────────────────────────────
interface AnalyticsReport {
  id: string
  title: string
  report_type: string
  created_at: string
  [key: string]: unknown
}

// ─── Sample chart data ───────────────────────
const attendanceData = [
  { month: 'Jan', rate: 92 },
  { month: 'Feb', rate: 94 },
  { month: 'Mar', rate: 91 },
  { month: 'Apr', rate: 89 },
  { month: 'May', rate: 93 },
  { month: 'Jun', rate: 95 },
]

const revenueData = [
  { month: 'Jan', revenue: 125000 },
  { month: 'Feb', revenue: 118000 },
  { month: 'Mar', revenue: 132000 },
  { month: 'Apr', revenue: 141000 },
  { month: 'May', revenue: 128000 },
  { month: 'Jun', revenue: 150000 },
]

// ─── Report columns ─────────────────────────
const reportColumns: Column<AnalyticsReport>[] = [
  { key: 'title', header: 'Title', sortable: true },
  { key: 'report_type', header: 'Type' },
  { key: 'created_at', header: 'Created', sortable: true, render: (r) => <>{formatDate(r.created_at)}</> },
]

export default function AnalyticsPage() {
  const [page, setPage] = useState(1)

  const { data: reportsData, isLoading } = useQuery({
    queryKey: ['analytics-reports', page],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 10 }
      const { data } = await api.get<PaginatedResponse<AnalyticsReport>>('/analytics/reports/', { params })
      return data
    },
  })

  const totalPages = reportsData ? Math.ceil(reportsData.count / 10) : 1

  return (
    <div>
      <PageHeader title="Analytics" description="Dashboard overview and reports" />

      {/* Stats cards */}
      <StatsGrid>
        <StatsCard title="Total Students" value="1,245" icon={Users} />
        <StatsCard title="Avg Attendance" value="92.3%" icon={BarChart3} />
        <StatsCard title="Avg GPA" value="3.45" icon={GraduationCap} />
        <StatsCard title="Revenue" value={formatCurrency(794000)} icon={DollarSign} />
      </StatsGrid>

      {/* Charts */}
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardContent className="p-6">
            <h3 className="mb-4 text-lg font-semibold">Attendance Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={attendanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis domain={[80, 100]} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="rate"
                  stroke="hsl(var(--primary))"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <h3 className="mb-4 text-lg font-semibold">Revenue Overview</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={revenueData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value: number) => formatCurrency(value)} />
                <Bar dataKey="revenue" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent reports */}
      <div className="mt-6">
        <h3 className="mb-4 text-lg font-semibold">Recent Reports</h3>
        {isLoading ? (
          <Loading className="h-32" />
        ) : (
          <DataTable
            data={(reportsData?.results ?? []) as AnalyticsReport[]}
            columns={reportColumns}
            isLoading={isLoading}
            pagination={{ page, totalPages, onPageChange: setPage }}
            emptyMessage="No reports found."
          />
        )}
      </div>
    </div>
  )
}
