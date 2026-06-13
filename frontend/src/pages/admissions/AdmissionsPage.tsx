import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { CheckCircle, XCircle } from 'lucide-react'
import api from '@/lib/api'
import { formatDate } from '@/lib/utils'
import type { PaginatedResponse, AdmissionApplication } from '@/types'
import { PageHeader } from '@/components/layout/PageHeader'
import { DataTable, type Column } from '@/components/ui/data-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Loading } from '@/components/ui/loading'

const statusBadge: Record<string, 'secondary' | 'success' | 'destructive' | 'warning'> = {
  submitted: 'secondary',
  under_review: 'secondary',
  approved: 'success',
  rejected: 'destructive',
  waitlisted: 'warning',
  enrolled: 'success',
  fee_pending: 'warning',
  withdrawn: 'destructive',
}

export default function AdmissionsPage() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['admissions', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<AdmissionApplication>>('/admissions/applications/', { params })
      return data
    },
  })

  const actionMutation = useMutation({
    mutationFn: ({ id, action }: { id: string; action: 'approve' | 'reject' }) =>
      api.post(`/admissions/applications/${id}/${action}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admissions'] })
    },
  })

  const columns: Column<AdmissionApplication>[] = [
    { key: 'application_number', header: 'Application #', sortable: true },
    {
      key: 'first_name',
      header: 'Applicant',
      render: (a) => `${a.first_name} ${a.last_name}`,
    },
    { key: 'email', header: 'Email' },
    { key: 'class_name', header: 'Class' },
    {
      key: 'status',
      header: 'Status',
      render: (a) => (
        <Badge variant={statusBadge[a.status] ?? 'secondary'}>
          {a.status.replace(/_/g, ' ')}
        </Badge>
      ),
    },
    {
      key: 'merit_score',
      header: 'Merit',
      render: (a) => (a.merit_score != null ? a.merit_score : '—'),
    },
    {
      key: 'created_at',
      header: 'Applied',
      render: (a) => formatDate(a.created_at),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (a) =>
        a.status === 'submitted' || a.status === 'under_review' ? (
          <div className="flex items-center gap-1">
            <Button
              size="sm"
              variant="ghost"
              className="text-green-600 hover:text-green-700"
              onClick={() => actionMutation.mutate({ id: a.id, action: 'approve' })}
              disabled={actionMutation.isPending}
            >
              <CheckCircle className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="text-red-600 hover:text-red-700"
              onClick={() => actionMutation.mutate({ id: a.id, action: 'reject' })}
              disabled={actionMutation.isPending}
            >
              <XCircle className="h-4 w-4" />
            </Button>
          </div>
        ) : null,
    },
  ]

  if (isLoading) return <Loading className="h-64" />

  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <div>
      <PageHeader title="Admissions" description="Review and manage admission applications" />

      <DataTable
        data={(data?.results ?? []) as (AdmissionApplication & Record<string, unknown>)[]}
        columns={columns}
        searchPlaceholder="Search by name or application number…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No applications found."
      />
    </div>
  )
}
