import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Send } from 'lucide-react'
import api from '@/lib/api'
import { formatDate } from '@/lib/utils'
import type { PaginatedResponse, Exam, Grade, ReportCard } from '@/types'
import { PageHeader } from '@/components/layout/PageHeader'
import { DataTable, type Column } from '@/components/ui/data-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loading } from '@/components/ui/loading'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'

// ─── Exams Tab ───────────────────────────────
const examColumns: Column<Exam>[] = [
  { key: 'name', header: 'Name', sortable: true },
  { key: 'exam_type_name', header: 'Type' },
  {
    key: 'start_date',
    header: 'Start Date',
    sortable: true,
    render: (e) => <>{formatDate(e.start_date)}</>,
  },
  {
    key: 'end_date',
    header: 'End Date',
    render: (e) => <>{formatDate(e.end_date)}</>,
  },
  {
    key: 'is_published',
    header: 'Published',
    render: (e) => (
      <Badge variant={e.is_published ? 'success' : 'secondary'}>
        {e.is_published ? 'Published' : 'Draft'}
      </Badge>
    ),
  },
]

function ExamsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ name: '', start_date: '', end_date: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['exams', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Exam>>('/examinations/exams/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/examinations/exams/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['exams'] })
      setDialogOpen(false)
      setForm({ name: '', start_date: '', end_date: '' })
    },
  })

  const publishMutation = useMutation({
    mutationFn: (id: string) => api.patch(`/examinations/exams/${id}/`, { is_published: true }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['exams'] }),
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  const columnsWithAction: Column<Exam>[] = [
    ...examColumns,
    {
      key: 'actions',
      header: 'Actions',
      render: (e) =>
        !e.is_published ? (
          <Button size="sm" variant="outline" onClick={() => publishMutation.mutate(e.id)} disabled={publishMutation.isPending}>
            <Send className="mr-1 h-3 w-3" />Publish
          </Button>
        ) : null,
    },
  ]

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Exam</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Exam</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="exam-name">Name</Label>
                <Input id="exam-name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="exam-start">Start Date</Label>
                  <Input id="exam-start" type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="exam-end">End Date</Label>
                  <Input id="exam-end" type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} />
                </div>
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
        data={(data?.results ?? []) as (Exam & Record<string, unknown>)[]}
        columns={columnsWithAction}
        searchPlaceholder="Search exams…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No exams found."
      />
    </>
  )
}

// ─── Grades Tab ──────────────────────────────
const gradeColumns: Column<Grade>[] = [
  { key: 'student_name', header: 'Student', sortable: true },
  { key: 'subject_name', header: 'Subject', sortable: true },
  { key: 'marks_obtained', header: 'Marks', sortable: true },
  { key: 'grade_letter', header: 'Grade' },
  {
    key: 'percentage',
    header: 'Percentage',
    render: (g) => <>{g.percentage.toFixed(1)}%</>,
  },
  {
    key: 'is_passed',
    header: 'Result',
    render: (g) => (
      <Badge variant={g.is_passed ? 'success' : 'destructive'}>
        {g.is_passed ? 'Pass' : 'Fail'}
      </Badge>
    ),
  },
]

function GradesTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ student: '', exam_schedule: '', marks_obtained: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['grades', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Grade>>('/examinations/grades/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/examinations/grades/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grades'] })
      setDialogOpen(false)
      setForm({ student: '', exam_schedule: '', marks_obtained: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Grade</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Grade</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="grade-student">Student ID</Label>
                  <Input id="grade-student" value={form.student} onChange={(e) => setForm({ ...form, student: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="grade-schedule">Exam Schedule ID</Label>
                  <Input id="grade-schedule" value={form.exam_schedule} onChange={(e) => setForm({ ...form, exam_schedule: e.target.value })} />
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="grade-marks">Marks Obtained</Label>
                <Input id="grade-marks" type="number" value={form.marks_obtained} onChange={(e) => setForm({ ...form, marks_obtained: e.target.value })} />
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
        data={(data?.results ?? []) as (Grade & Record<string, unknown>)[]}
        columns={gradeColumns}
        searchPlaceholder="Search grades…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No grades found."
      />
    </>
  )
}

// ─── Report Cards Tab ────────────────────────
const reportCardColumns: Column<ReportCard>[] = [
  { key: 'student_name', header: 'Student', sortable: true },
  {
    key: 'percentage',
    header: 'Percentage',
    sortable: true,
    render: (r) => <>{r.percentage.toFixed(1)}%</>,
  },
  {
    key: 'gpa',
    header: 'GPA',
    render: (r) => <>{r.gpa?.toFixed(2) ?? '—'}</>,
  },
  {
    key: 'rank',
    header: 'Rank',
    sortable: true,
    render: (r) => <>{r.rank ?? '—'}</>,
  },
  {
    key: 'is_published',
    header: 'Published',
    render: (r) => (
      <Badge variant={r.is_published ? 'success' : 'secondary'}>
        {r.is_published ? 'Published' : 'Draft'}
      </Badge>
    ),
  },
]

function ReportCardsTab() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['report-cards', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<ReportCard>>('/examinations/report-cards/', { params })
      return data
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <DataTable
      data={(data?.results ?? []) as (ReportCard & Record<string, unknown>)[]}
      columns={reportCardColumns}
      searchPlaceholder="Search report cards…"
      onSearch={(q) => { setSearch(q); setPage(1) }}
      isLoading={isLoading}
      pagination={{ page, totalPages, onPageChange: setPage }}
      emptyMessage="No report cards found."
    />
  )
}

// ─── Main Page ───────────────────────────────
export default function ExaminationsPage() {
  return (
    <div>
      <PageHeader title="Examinations" description="Manage exams, grades, and report cards" />
      <Tabs defaultValue="exams">
        <TabsList>
          <TabsTrigger value="exams">Exams</TabsTrigger>
          <TabsTrigger value="grades">Grades</TabsTrigger>
          <TabsTrigger value="report-cards">Report Cards</TabsTrigger>
        </TabsList>
        <TabsContent value="exams"><ExamsTab /></TabsContent>
        <TabsContent value="grades"><GradesTab /></TabsContent>
        <TabsContent value="report-cards"><ReportCardsTab /></TabsContent>
      </Tabs>
    </div>
  )
}
