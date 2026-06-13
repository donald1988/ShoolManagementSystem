import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, BookOpen, Video } from 'lucide-react'
import api from '@/lib/api'
import { formatDate } from '@/lib/utils'
import type { PaginatedResponse, Course, Assignment } from '@/types'
import { PageHeader } from '@/components/layout/PageHeader'
import { DataTable, type Column } from '@/components/ui/data-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loading } from '@/components/ui/loading'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

// ─── Types ───────────────────────────────────
interface LiveClass {
  id: string
  title: string
  teacher: string
  teacher_name: string
  platform: string
  scheduled_at: string
  duration_minutes: number
}

// ─── Courses Tab (Grid View) ─────────────────
function CoursesTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ title: '', description: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['courses', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 12 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Course>>('/lms/courses/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/lms/courses/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] })
      setDialogOpen(false)
      setForm({ title: '', description: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 12) : 1

  return (
    <>
      <div className="mb-4 flex items-center justify-between">
        <Input
          placeholder="Search courses…"
          className="max-w-sm"
          onChange={(e) => { setSearch(e.target.value); setPage(1) }}
        />
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Course</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Course</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="course-title">Title</Label>
                <Input id="course-title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="course-desc">Description</Label>
                <Textarea id="course-desc" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
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

      {data?.results.length === 0 ? (
        <p className="py-12 text-center text-muted-foreground">No courses found.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {data?.results.map((course) => (
            <Card key={course.id} className="overflow-hidden">
              {course.thumbnail ? (
                <img src={course.thumbnail} alt={course.title} className="h-40 w-full object-cover" />
              ) : (
                <div className="flex h-40 items-center justify-center bg-muted">
                  <BookOpen className="h-12 w-12 text-muted-foreground" />
                </div>
              )}
              <CardContent className="p-4">
                <h3 className="font-semibold leading-tight">{course.title}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{course.instructor_name}</p>
                <div className="mt-3 flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">{course.module_count} modules</span>
                  <Badge variant={course.is_published ? 'success' : 'secondary'}>
                    {course.is_published ? 'Published' : 'Draft'}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-center gap-2">
          <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}>
            Next
          </Button>
        </div>
      )}
    </>
  )
}

// ─── Assignments Tab ─────────────────────────
const assignmentTypeMap: Record<string, 'secondary' | 'success' | 'warning'> = {
  homework: 'secondary',
  project: 'success',
  quiz: 'warning',
  classwork: 'secondary',
}

const assignmentColumns: Column<Assignment>[] = [
  { key: 'title', header: 'Title', sortable: true },
  { key: 'class_name', header: 'Class' },
  { key: 'subject_name', header: 'Subject' },
  { key: 'teacher_name', header: 'Teacher' },
  {
    key: 'assignment_type',
    header: 'Type',
    render: (a) => (
      <Badge variant={assignmentTypeMap[a.assignment_type] ?? 'secondary'}>
        {a.assignment_type}
      </Badge>
    ),
  },
  { key: 'due_date', header: 'Due Date', sortable: true, render: (a) => <>{formatDate(a.due_date)}</> },
  { key: 'max_marks', header: 'Max Marks' },
  {
    key: 'is_published',
    header: 'Published',
    render: (a) => (
      <Badge variant={a.is_published ? 'success' : 'secondary'}>
        {a.is_published ? 'Published' : 'Draft'}
      </Badge>
    ),
  },
]

function AssignmentsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ title: '', description: '', due_date: '', max_marks: '', assignment_type: 'homework' })

  const { data, isLoading } = useQuery({
    queryKey: ['assignments', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Assignment>>('/lms/assignments/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/lms/assignments/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignments'] })
      setDialogOpen(false)
      setForm({ title: '', description: '', due_date: '', max_marks: '', assignment_type: 'homework' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Assignment</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Assignment</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="asgn-title">Title</Label>
                <Input id="asgn-title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="asgn-desc">Description</Label>
                <Textarea id="asgn-desc" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="asgn-type">Type</Label>
                  <Select value={form.assignment_type} onValueChange={(v) => setForm({ ...form, assignment_type: v })}>
                    <SelectTrigger id="asgn-type"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="homework">Homework</SelectItem>
                      <SelectItem value="project">Project</SelectItem>
                      <SelectItem value="quiz">Quiz</SelectItem>
                      <SelectItem value="classwork">Classwork</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="asgn-due">Due Date</Label>
                  <Input id="asgn-due" type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="asgn-marks">Max Marks</Label>
                  <Input id="asgn-marks" type="number" value={form.max_marks} onChange={(e) => setForm({ ...form, max_marks: e.target.value })} />
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
        data={(data?.results ?? []) as (Assignment & Record<string, unknown>)[]}
        columns={assignmentColumns}
        searchPlaceholder="Search assignments…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No assignments found."
      />
    </>
  )
}

// ─── Live Classes Tab ────────────────────────
const platformBadge: Record<string, 'secondary' | 'success' | 'warning'> = {
  zoom: 'success',
  google_meet: 'warning',
  teams: 'secondary',
  custom: 'secondary',
}

const liveClassColumns: Column<LiveClass>[] = [
  { key: 'title', header: 'Title', sortable: true },
  { key: 'teacher_name', header: 'Teacher' },
  {
    key: 'platform',
    header: 'Platform',
    render: (lc) => (
      <Badge variant={platformBadge[lc.platform] ?? 'secondary'}>
        {lc.platform.replace('_', ' ')}
      </Badge>
    ),
  },
  { key: 'scheduled_at', header: 'Scheduled At', sortable: true, render: (lc) => <>{formatDate(lc.scheduled_at)}</> },
  { key: 'duration_minutes', header: 'Duration (min)' },
]

function LiveClassesTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ title: '', scheduled_at: '', duration_minutes: '', platform: 'zoom' })

  const { data, isLoading } = useQuery({
    queryKey: ['live-classes', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<LiveClass>>('/lms/live-classes/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/lms/live-classes/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['live-classes'] })
      setDialogOpen(false)
      setForm({ title: '', scheduled_at: '', duration_minutes: '', platform: 'zoom' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" /><Video className="mr-1 h-4 w-4" />Add Live Class</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add Live Class</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="lc-title">Title</Label>
                <Input id="lc-title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="lc-platform">Platform</Label>
                  <Select value={form.platform} onValueChange={(v) => setForm({ ...form, platform: v })}>
                    <SelectTrigger id="lc-platform"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="zoom">Zoom</SelectItem>
                      <SelectItem value="google_meet">Google Meet</SelectItem>
                      <SelectItem value="teams">Teams</SelectItem>
                      <SelectItem value="custom">Custom</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="lc-date">Scheduled At</Label>
                  <Input id="lc-date" type="datetime-local" value={form.scheduled_at} onChange={(e) => setForm({ ...form, scheduled_at: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="lc-dur">Duration (min)</Label>
                  <Input id="lc-dur" type="number" value={form.duration_minutes} onChange={(e) => setForm({ ...form, duration_minutes: e.target.value })} />
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
        data={(data?.results ?? []) as (LiveClass & Record<string, unknown>)[]}
        columns={liveClassColumns}
        searchPlaceholder="Search live classes…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No live classes found."
      />
    </>
  )
}

// ─── Main Page ───────────────────────────────
export default function LmsPage() {
  return (
    <div>
      <PageHeader title="Learning Management" description="Manage courses, assignments, and live classes" />
      <Tabs defaultValue="courses">
        <TabsList>
          <TabsTrigger value="courses">Courses</TabsTrigger>
          <TabsTrigger value="assignments">Assignments</TabsTrigger>
          <TabsTrigger value="live-classes">Live Classes</TabsTrigger>
        </TabsList>
        <TabsContent value="courses"><CoursesTab /></TabsContent>
        <TabsContent value="assignments"><AssignmentsTab /></TabsContent>
        <TabsContent value="live-classes"><LiveClassesTab /></TabsContent>
      </Tabs>
    </div>
  )
}
