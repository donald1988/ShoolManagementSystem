import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import api from '@/lib/api'
import type { PaginatedResponse, Class, Subject, Department, Teacher } from '@/types'
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

// ─── Classes Tab ─────────────────────────────
const classColumns: Column<Class>[] = [
  { key: 'name', header: 'Name', sortable: true },
  { key: 'code', header: 'Code', sortable: true },
  { key: 'numeric_level', header: 'Level', sortable: true },
  { key: 'capacity', header: 'Capacity' },
  { key: 'student_count', header: 'Students' },
  {
    key: 'is_active',
    header: 'Status',
    render: (c) => (
      <Badge variant={c.is_active ? 'success' : 'secondary'}>
        {c.is_active ? 'Active' : 'Inactive'}
      </Badge>
    ),
  },
]

function ClassesTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ name: '', code: '', numeric_level: '', capacity: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['classes', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Class>>('/academics/classes/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/academics/classes/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['classes'] })
      setDialogOpen(false)
      setForm({ name: '', code: '', numeric_level: '', capacity: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Class</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Class</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="cls-name">Name</Label>
                  <Input id="cls-name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="cls-code">Code</Label>
                  <Input id="cls-code" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="cls-level">Numeric Level</Label>
                  <Input id="cls-level" type="number" value={form.numeric_level} onChange={(e) => setForm({ ...form, numeric_level: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="cls-cap">Capacity</Label>
                  <Input id="cls-cap" type="number" value={form.capacity} onChange={(e) => setForm({ ...form, capacity: e.target.value })} />
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
        data={(data?.results ?? []) as (Class & Record<string, unknown>)[]}
        columns={classColumns}
        searchPlaceholder="Search classes…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No classes found."
      />
    </>
  )
}

// ─── Subjects Tab ────────────────────────────
const subjectColumns: Column<Subject>[] = [
  { key: 'code', header: 'Code', sortable: true },
  { key: 'name', header: 'Name', sortable: true },
  {
    key: 'subject_type',
    header: 'Type',
    render: (s) => <Badge variant="secondary">{s.subject_type}</Badge>,
  },
  { key: 'credits', header: 'Credits' },
  { key: 'department_name', header: 'Department' },
  {
    key: 'is_mandatory',
    header: 'Mandatory',
    render: (s) => (
      <Badge variant={s.is_mandatory ? 'success' : 'secondary'}>
        {s.is_mandatory ? 'Yes' : 'No'}
      </Badge>
    ),
  },
]

function SubjectsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ name: '', code: '', subject_type: 'theory', credits: '', is_mandatory: true })

  const { data, isLoading } = useQuery({
    queryKey: ['subjects', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Subject>>('/academics/subjects/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/academics/subjects/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subjects'] })
      setDialogOpen(false)
      setForm({ name: '', code: '', subject_type: 'theory', credits: '', is_mandatory: true })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Subject</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Subject</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="subj-name">Name</Label>
                  <Input id="subj-name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="subj-code">Code</Label>
                  <Input id="subj-code" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label>Type</Label>
                  <Select value={form.subject_type} onValueChange={(v) => setForm({ ...form, subject_type: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="theory">Theory</SelectItem>
                      <SelectItem value="practical">Practical</SelectItem>
                      <SelectItem value="elective">Elective</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="subj-credits">Credits</Label>
                  <Input id="subj-credits" type="number" value={form.credits} onChange={(e) => setForm({ ...form, credits: e.target.value })} />
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
        data={(data?.results ?? []) as (Subject & Record<string, unknown>)[]}
        columns={subjectColumns}
        searchPlaceholder="Search subjects…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No subjects found."
      />
    </>
  )
}

// ─── Departments Tab ─────────────────────────
const departmentColumns: Column<Department>[] = [
  { key: 'name', header: 'Name', sortable: true },
  { key: 'code', header: 'Code', sortable: true },
  { key: 'head_name', header: 'Head' },
  {
    key: 'is_active',
    header: 'Status',
    render: (d) => (
      <Badge variant={d.is_active ? 'success' : 'secondary'}>
        {d.is_active ? 'Active' : 'Inactive'}
      </Badge>
    ),
  },
]

function DepartmentsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ name: '', code: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['departments', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Department>>('/academics/departments/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/academics/departments/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] })
      setDialogOpen(false)
      setForm({ name: '', code: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Department</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Department</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="dept-name">Name</Label>
                  <Input id="dept-name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="dept-code">Code</Label>
                  <Input id="dept-code" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
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
        data={(data?.results ?? []) as (Department & Record<string, unknown>)[]}
        columns={departmentColumns}
        searchPlaceholder="Search departments…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No departments found."
      />
    </>
  )
}

// ─── Teachers Tab ────────────────────────────
const teacherColumns: Column<Teacher>[] = [
  { key: 'employee_id', header: 'Employee ID', sortable: true },
  { key: 'full_name', header: 'Full Name', sortable: true },
  { key: 'email', header: 'Email' },
  { key: 'department_name', header: 'Department' },
  { key: 'designation', header: 'Designation' },
  {
    key: 'is_active',
    header: 'Status',
    render: (t) => (
      <Badge variant={t.is_active ? 'success' : 'secondary'}>
        {t.is_active ? 'Active' : 'Inactive'}
      </Badge>
    ),
  },
]

function TeachersTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ user: '', employee_id: '', designation: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['teachers', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Teacher>>('/academics/teachers/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/academics/teachers/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teachers'] })
      setDialogOpen(false)
      setForm({ user: '', employee_id: '', designation: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Teacher</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Teacher</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="tch-user">User Email</Label>
                <Input id="tch-user" value={form.user} onChange={(e) => setForm({ ...form, user: e.target.value })} placeholder="user@example.com" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="tch-eid">Employee ID</Label>
                  <Input id="tch-eid" value={form.employee_id} onChange={(e) => setForm({ ...form, employee_id: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="tch-desig">Designation</Label>
                  <Input id="tch-desig" value={form.designation} onChange={(e) => setForm({ ...form, designation: e.target.value })} />
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
        data={(data?.results ?? []) as (Teacher & Record<string, unknown>)[]}
        columns={teacherColumns}
        searchPlaceholder="Search teachers…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No teachers found."
      />
    </>
  )
}

// ─── Main Page ───────────────────────────────
export default function AcademicsPage() {
  return (
    <div>
      <PageHeader title="Academics" description="Manage classes, subjects, departments, and teachers" />
      <Tabs defaultValue="classes">
        <TabsList>
          <TabsTrigger value="classes">Classes</TabsTrigger>
          <TabsTrigger value="subjects">Subjects</TabsTrigger>
          <TabsTrigger value="departments">Departments</TabsTrigger>
          <TabsTrigger value="teachers">Teachers</TabsTrigger>
        </TabsList>
        <TabsContent value="classes"><ClassesTab /></TabsContent>
        <TabsContent value="subjects"><SubjectsTab /></TabsContent>
        <TabsContent value="departments"><DepartmentsTab /></TabsContent>
        <TabsContent value="teachers"><TeachersTab /></TabsContent>
      </Tabs>
    </div>
  )
}
