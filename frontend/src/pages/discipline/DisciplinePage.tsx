import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, CheckCircle } from 'lucide-react'
import api from '@/lib/api'
import { formatDate, truncate } from '@/lib/utils'
import type { PaginatedResponse } from '@/types'
import { PageHeader } from '@/components/layout/PageHeader'
import { DataTable, type Column } from '@/components/ui/data-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loading } from '@/components/ui/loading'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'

// ─── Types ───────────────────────────────────
interface DisciplineIncident {
  id: string
  student: string
  student_name: string
  category: string
  incident_date: string
  status: string
  action_taken: string
  parent_notified: boolean
  description: string
  [key: string]: unknown
}

interface Detention {
  id: string
  student: string
  student_name: string
  date: string
  start_time: string
  end_time: string
  reason: string
  status: string
  [key: string]: unknown
}

interface Suspension {
  id: string
  student: string
  student_name: string
  start_date: string
  end_date: string
  suspension_type: string
  reason: string
  parent_acknowledged: boolean
  [key: string]: unknown
}

// ─── Incidents Tab ───────────────────────────
const incidentStatusBadge: Record<string, 'secondary' | 'success' | 'warning' | 'destructive'> = {
  reported: 'warning',
  investigating: 'secondary',
  resolved: 'success',
  dismissed: 'secondary',
  escalated: 'destructive',
}

const incidentColumns: Column<DisciplineIncident>[] = [
  { key: 'student_name', header: 'Student', sortable: true },
  { key: 'category', header: 'Category' },
  { key: 'incident_date', header: 'Date', sortable: true, render: (i) => <>{formatDate(i.incident_date)}</> },
  {
    key: 'status',
    header: 'Status',
    render: (i) => (
      <Badge variant={incidentStatusBadge[i.status] ?? 'secondary'}>
        {i.status}
      </Badge>
    ),
  },
  { key: 'action_taken', header: 'Action Taken' },
  {
    key: 'parent_notified',
    header: 'Parent Notified',
    render: (i) => (
      <Badge variant={i.parent_notified ? 'success' : 'secondary'}>
        {i.parent_notified ? 'Yes' : 'No'}
      </Badge>
    ),
  },
]

function IncidentsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ student: '', category: '', incident_date: '', description: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['discipline-incidents', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<DisciplineIncident>>('/discipline/incidents/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/discipline/incidents/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['discipline-incidents'] })
      setDialogOpen(false)
      setForm({ student: '', category: '', incident_date: '', description: '' })
    },
  })

  const resolveMutation = useMutation({
    mutationFn: (id: string) => api.patch(`/discipline/incidents/${id}/`, { status: 'resolved' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['discipline-incidents'] }),
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  const columnsWithAction: Column<DisciplineIncident>[] = [
    ...incidentColumns,
    {
      key: 'actions',
      header: 'Actions',
      render: (i) =>
        i.status !== 'resolved' && i.status !== 'dismissed' ? (
          <Button size="sm" variant="outline" onClick={() => resolveMutation.mutate(i.id)} disabled={resolveMutation.isPending}>
            <CheckCircle className="mr-1 h-3 w-3" />Resolve
          </Button>
        ) : null,
    },
  ]

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Incident</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Report Discipline Incident</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="di-student">Student ID</Label>
                  <Input id="di-student" value={form.student} onChange={(e) => setForm({ ...form, student: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="di-cat">Category</Label>
                  <Input id="di-cat" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="di-date">Incident Date</Label>
                <Input id="di-date" type="date" value={form.incident_date} onChange={(e) => setForm({ ...form, incident_date: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="di-desc">Description</Label>
                <Textarea id="di-desc" rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button onClick={() => createMutation.mutate(form)} disabled={createMutation.isPending}>
                {createMutation.isPending ? 'Saving…' : 'Save'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
      <DataTable
        data={(data?.results ?? []) as DisciplineIncident[]}
        columns={columnsWithAction}
        searchPlaceholder="Search incidents…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No discipline incidents found."
      />
    </>
  )
}

// ─── Detentions Tab ──────────────────────────
const detentionStatusBadge: Record<string, 'secondary' | 'success' | 'warning'> = {
  scheduled: 'warning',
  served: 'success',
  missed: 'secondary',
}

const detentionColumns: Column<Detention>[] = [
  { key: 'student_name', header: 'Student', sortable: true },
  { key: 'date', header: 'Date', sortable: true, render: (d) => <>{formatDate(d.date)}</> },
  { key: 'start_time', header: 'Start Time' },
  { key: 'end_time', header: 'End Time' },
  { key: 'reason', header: 'Reason' },
  {
    key: 'status',
    header: 'Status',
    render: (d) => (
      <Badge variant={detentionStatusBadge[d.status] ?? 'secondary'}>
        {d.status}
      </Badge>
    ),
  },
]

function DetentionsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ student: '', date: '', start_time: '', end_time: '', reason: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['detentions', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Detention>>('/discipline/detentions/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/discipline/detentions/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['detentions'] })
      setDialogOpen(false)
      setForm({ student: '', date: '', start_time: '', end_time: '', reason: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Detention</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add Detention</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="det-student">Student ID</Label>
                  <Input id="det-student" value={form.student} onChange={(e) => setForm({ ...form, student: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="det-date">Date</Label>
                  <Input id="det-date" type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="det-start">Start Time</Label>
                  <Input id="det-start" type="time" value={form.start_time} onChange={(e) => setForm({ ...form, start_time: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="det-end">End Time</Label>
                  <Input id="det-end" type="time" value={form.end_time} onChange={(e) => setForm({ ...form, end_time: e.target.value })} />
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="det-reason">Reason</Label>
                <Input id="det-reason" value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button onClick={() => createMutation.mutate(form)} disabled={createMutation.isPending}>
                {createMutation.isPending ? 'Saving…' : 'Save'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
      <DataTable
        data={(data?.results ?? []) as Detention[]}
        columns={detentionColumns}
        searchPlaceholder="Search detentions…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No detentions found."
      />
    </>
  )
}

// ─── Suspensions Tab ─────────────────────────
const suspensionTypeBadge: Record<string, 'secondary' | 'warning' | 'destructive'> = {
  in_school: 'warning',
  out_of_school: 'destructive',
  temporary: 'secondary',
  permanent: 'destructive',
}

const suspensionColumns: Column<Suspension>[] = [
  { key: 'student_name', header: 'Student', sortable: true },
  { key: 'start_date', header: 'Start', sortable: true, render: (s) => <>{formatDate(s.start_date)}</> },
  { key: 'end_date', header: 'End', render: (s) => <>{formatDate(s.end_date)}</> },
  {
    key: 'suspension_type',
    header: 'Type',
    render: (s) => (
      <Badge variant={suspensionTypeBadge[s.suspension_type] ?? 'secondary'}>
        {s.suspension_type.replace(/_/g, ' ')}
      </Badge>
    ),
  },
  {
    key: 'reason',
    header: 'Reason',
    render: (s) => <>{truncate(s.reason, 50)}</>,
  },
  {
    key: 'parent_acknowledged',
    header: 'Parent Ack.',
    render: (s) => (
      <Badge variant={s.parent_acknowledged ? 'success' : 'secondary'}>
        {s.parent_acknowledged ? 'Yes' : 'No'}
      </Badge>
    ),
  },
]

function SuspensionsTab() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['suspensions', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Suspension>>('/discipline/suspensions/', { params })
      return data
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <DataTable
      data={(data?.results ?? []) as Suspension[]}
      columns={suspensionColumns}
      searchPlaceholder="Search suspensions…"
      onSearch={(q) => { setSearch(q); setPage(1) }}
      isLoading={isLoading}
      pagination={{ page, totalPages, onPageChange: setPage }}
      emptyMessage="No suspensions found."
    />
  )
}

// ─── Main Page ───────────────────────────────
export default function DisciplinePage() {
  return (
    <div>
      <PageHeader title="Discipline" description="Manage incidents, detentions, and suspensions" />
      <Tabs defaultValue="incidents">
        <TabsList>
          <TabsTrigger value="incidents">Incidents</TabsTrigger>
          <TabsTrigger value="detentions">Detentions</TabsTrigger>
          <TabsTrigger value="suspensions">Suspensions</TabsTrigger>
        </TabsList>
        <TabsContent value="incidents"><IncidentsTab /></TabsContent>
        <TabsContent value="detentions"><DetentionsTab /></TabsContent>
        <TabsContent value="suspensions"><SuspensionsTab /></TabsContent>
      </Tabs>
    </div>
  )
}
