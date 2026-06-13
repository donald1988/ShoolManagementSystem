import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import api from '@/lib/api'
import { formatDate } from '@/lib/utils'
import type { PaginatedResponse, Student } from '@/types'
import { PageHeader } from '@/components/layout/PageHeader'
import { DataTable, type Column } from '@/components/ui/data-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loading } from '@/components/ui/loading'
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

const statusBadge: Record<string, 'success' | 'warning' | 'secondary' | 'destructive'> = {
  enrolled: 'success',
  new_admission: 'warning',
  graduated: 'secondary',
  suspended: 'destructive',
}

const columns: Column<Student>[] = [
  { key: 'student_id', header: 'Student ID', sortable: true },
  { key: 'full_name', header: 'Full Name', sortable: true },
  { key: 'email', header: 'Email' },
  { key: 'class_name', header: 'Class' },
  { key: 'section_name', header: 'Section' },
  { key: 'roll_number', header: 'Roll No.' },
  {
    key: 'status',
    header: 'Status',
    render: (s) => (
      <Badge variant={statusBadge[s.status] ?? 'secondary'}>
        {s.status.replace('_', ' ')}
      </Badge>
    ),
  },
]

export default function StudentsPage() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({
    user: '',
    student_id: '',
    admission_number: '',
    admission_date: '',
    date_of_birth: '',
    gender: 'male',
    status: 'new_admission',
  })

  const { data, isLoading } = useQuery({
    queryKey: ['students', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Student>>('/students/students/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/students/students/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['students'] })
      setDialogOpen(false)
      setForm({ user: '', student_id: '', admission_number: '', admission_date: '', date_of_birth: '', gender: 'male', status: 'new_admission' })
    },
  })

  if (isLoading) return <Loading className="h-64" />

  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <div>
      <PageHeader title="Students" description="Manage student records">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Student</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Student</DialogTitle>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="user">User Email</Label>
                <Input id="user" value={form.user} onChange={(e) => setForm({ ...form, user: e.target.value })} placeholder="user@example.com" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="student_id">Student ID</Label>
                  <Input id="student_id" value={form.student_id} onChange={(e) => setForm({ ...form, student_id: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="admission_number">Admission No.</Label>
                  <Input id="admission_number" value={form.admission_number} onChange={(e) => setForm({ ...form, admission_number: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="admission_date">Admission Date</Label>
                  <Input id="admission_date" type="date" value={form.admission_date} onChange={(e) => setForm({ ...form, admission_date: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="date_of_birth">Date of Birth</Label>
                  <Input id="date_of_birth" type="date" value={form.date_of_birth} onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label>Gender</Label>
                  <Select value={form.gender} onValueChange={(v) => setForm({ ...form, gender: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="male">Male</SelectItem>
                      <SelectItem value="female">Female</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label>Status</Label>
                  <Select value={form.status} onValueChange={(v) => setForm({ ...form, status: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="new_admission">New Admission</SelectItem>
                      <SelectItem value="enrolled">Enrolled</SelectItem>
                      <SelectItem value="graduated">Graduated</SelectItem>
                      <SelectItem value="suspended">Suspended</SelectItem>
                    </SelectContent>
                  </Select>
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
      </PageHeader>

      <DataTable
        data={(data?.results ?? []) as (Student & Record<string, unknown>)[]}
        columns={columns}
        searchPlaceholder="Search by name or student ID…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No students found."
      />
    </div>
  )
}
