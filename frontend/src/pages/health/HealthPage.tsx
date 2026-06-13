import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
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
interface MedicalRecord {
  id: string
  student: string
  student_name: string
  blood_group: string
  allergies: string
  chronic_conditions: string
  [key: string]: unknown
}

interface HealthVisit {
  id: string
  student: string
  student_name: string
  visit_date: string
  reason: string
  diagnosis: string
  follow_up_required: boolean
  [key: string]: unknown
}

interface HealthIncident {
  id: string
  student: string
  student_name: string
  incident_type: string
  incident_date: string
  severity: string
  description: string
  [key: string]: unknown
}

// ─── Medical Records Tab ─────────────────────
const medicalColumns: Column<MedicalRecord>[] = [
  { key: 'student_name', header: 'Student', sortable: true },
  { key: 'blood_group', header: 'Blood Group' },
  {
    key: 'allergies',
    header: 'Allergies',
    render: (r) => <>{r.allergies ? truncate(r.allergies, 40) : '—'}</>,
  },
  {
    key: 'chronic_conditions',
    header: 'Chronic Conditions',
    render: (r) => <>{r.chronic_conditions ? truncate(r.chronic_conditions, 40) : '—'}</>,
  },
]

function MedicalRecordsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ student: '', blood_group: '', allergies: '', chronic_conditions: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['medical-records', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<MedicalRecord>>('/health/medical-records/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/health/medical-records/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medical-records'] })
      setDialogOpen(false)
      setForm({ student: '', blood_group: '', allergies: '', chronic_conditions: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Record</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add Medical Record</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="med-student">Student ID</Label>
                  <Input id="med-student" value={form.student} onChange={(e) => setForm({ ...form, student: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="med-blood">Blood Group</Label>
                  <Input id="med-blood" value={form.blood_group} onChange={(e) => setForm({ ...form, blood_group: e.target.value })} />
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="med-allergies">Allergies</Label>
                <Textarea id="med-allergies" rows={2} value={form.allergies} onChange={(e) => setForm({ ...form, allergies: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="med-chronic">Chronic Conditions</Label>
                <Textarea id="med-chronic" rows={2} value={form.chronic_conditions} onChange={(e) => setForm({ ...form, chronic_conditions: e.target.value })} />
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
        data={(data?.results ?? []) as MedicalRecord[]}
        columns={medicalColumns}
        searchPlaceholder="Search medical records…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No medical records found."
      />
    </>
  )
}

// ─── Health Visits Tab ───────────────────────
const visitColumns: Column<HealthVisit>[] = [
  { key: 'student_name', header: 'Student', sortable: true },
  { key: 'visit_date', header: 'Visit Date', sortable: true, render: (v) => <>{formatDate(v.visit_date)}</> },
  { key: 'reason', header: 'Reason' },
  { key: 'diagnosis', header: 'Diagnosis' },
  {
    key: 'follow_up_required',
    header: 'Follow-up',
    render: (v) => (
      <Badge variant={v.follow_up_required ? 'warning' : 'secondary'}>
        {v.follow_up_required ? 'Required' : 'None'}
      </Badge>
    ),
  },
]

function HealthVisitsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ student: '', visit_date: '', reason: '', diagnosis: '', follow_up_required: false })

  const { data, isLoading } = useQuery({
    queryKey: ['health-visits', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<HealthVisit>>('/health/health-visits/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/health/health-visits/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['health-visits'] })
      setDialogOpen(false)
      setForm({ student: '', visit_date: '', reason: '', diagnosis: '', follow_up_required: false })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Visit</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add Health Visit</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="vis-student">Student ID</Label>
                  <Input id="vis-student" value={form.student} onChange={(e) => setForm({ ...form, student: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="vis-date">Visit Date</Label>
                  <Input id="vis-date" type="date" value={form.visit_date} onChange={(e) => setForm({ ...form, visit_date: e.target.value })} />
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="vis-reason">Reason</Label>
                <Input id="vis-reason" value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="vis-diag">Diagnosis</Label>
                <Input id="vis-diag" value={form.diagnosis} onChange={(e) => setForm({ ...form, diagnosis: e.target.value })} />
              </div>
              <div className="flex items-center gap-2">
                <input
                  id="vis-followup"
                  type="checkbox"
                  checked={form.follow_up_required}
                  onChange={(e) => setForm({ ...form, follow_up_required: e.target.checked })}
                  className="h-4 w-4 rounded border-gray-300"
                />
                <Label htmlFor="vis-followup">Follow-up required</Label>
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
        data={(data?.results ?? []) as HealthVisit[]}
        columns={visitColumns}
        searchPlaceholder="Search health visits…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No health visits found."
      />
    </>
  )
}

// ─── Health Incidents Tab ────────────────────
const severityBadge: Record<string, 'secondary' | 'warning' | 'destructive'> = {
  minor: 'secondary',
  moderate: 'warning',
  severe: 'destructive',
  critical: 'destructive',
}

const incidentColumns: Column<HealthIncident>[] = [
  { key: 'student_name', header: 'Student', sortable: true },
  {
    key: 'incident_type',
    header: 'Type',
    render: (i) => <Badge variant="secondary">{i.incident_type}</Badge>,
  },
  { key: 'incident_date', header: 'Date', sortable: true, render: (i) => <>{formatDate(i.incident_date)}</> },
  {
    key: 'severity',
    header: 'Severity',
    render: (i) => (
      <Badge variant={severityBadge[i.severity] ?? 'secondary'}>
        {i.severity}
      </Badge>
    ),
  },
  {
    key: 'description',
    header: 'Description',
    render: (i) => <>{truncate(i.description, 50)}</>,
  },
]

function IncidentsTab() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['health-incidents', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<HealthIncident>>('/health/health-incidents/', { params })
      return data
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <DataTable
      data={(data?.results ?? []) as HealthIncident[]}
      columns={incidentColumns}
      searchPlaceholder="Search incidents…"
      onSearch={(q) => { setSearch(q); setPage(1) }}
      isLoading={isLoading}
      pagination={{ page, totalPages, onPageChange: setPage }}
      emptyMessage="No health incidents found."
    />
  )
}

// ─── Main Page ───────────────────────────────
export default function HealthPage() {
  return (
    <div>
      <PageHeader title="Health" description="Medical records, health visits, and incidents" />
      <Tabs defaultValue="records">
        <TabsList>
          <TabsTrigger value="records">Medical Records</TabsTrigger>
          <TabsTrigger value="visits">Health Visits</TabsTrigger>
          <TabsTrigger value="incidents">Incidents</TabsTrigger>
        </TabsList>
        <TabsContent value="records"><MedicalRecordsTab /></TabsContent>
        <TabsContent value="visits"><HealthVisitsTab /></TabsContent>
        <TabsContent value="incidents"><IncidentsTab /></TabsContent>
      </Tabs>
    </div>
  )
}
