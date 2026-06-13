import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, CheckCircle, XCircle } from 'lucide-react'
import api from '@/lib/api'
import { formatDate } from '@/lib/utils'
import type { PaginatedResponse } from '@/types'
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

// ─── Types ───────────────────────────────────
interface Employee {
  id: string
  employee_id: string
  user: { full_name: string }
  department: string
  department_name: string
  designation: string
  contract_type: string
  is_active: boolean
  [key: string]: unknown
}

interface LeaveRequest {
  id: string
  employee: string
  employee_name: string
  leave_type: string
  start_date: string
  end_date: string
  days: number
  status: string
  [key: string]: unknown
}

interface Recruitment {
  id: string
  position: string
  department: string
  department_name: string
  num_positions: number
  application_deadline: string
  status: string
  [key: string]: unknown
}

// ─── Employees Tab ───────────────────────────
const contractBadge: Record<string, 'secondary' | 'success' | 'warning'> = {
  permanent: 'success',
  contract: 'warning',
  temporary: 'secondary',
  probation: 'warning',
}

const employeeColumns: Column<Employee>[] = [
  { key: 'employee_id', header: 'Employee ID', sortable: true },
  {
    key: 'user',
    header: 'Full Name',
    render: (e) => <>{e.user?.full_name ?? '—'}</>,
  },
  { key: 'department_name', header: 'Department' },
  { key: 'designation', header: 'Designation' },
  {
    key: 'contract_type',
    header: 'Contract',
    render: (e) => (
      <Badge variant={contractBadge[e.contract_type] ?? 'secondary'}>
        {e.contract_type}
      </Badge>
    ),
  },
  {
    key: 'is_active',
    header: 'Status',
    render: (e) => (
      <Badge variant={e.is_active ? 'success' : 'secondary'}>
        {e.is_active ? 'Active' : 'Inactive'}
      </Badge>
    ),
  },
]

function EmployeesTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ user: '', employee_id: '', designation: '', contract_type: 'permanent' })

  const { data, isLoading } = useQuery({
    queryKey: ['employees', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Employee>>('/hr/employees/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/hr/employees/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
      setDialogOpen(false)
      setForm({ user: '', employee_id: '', designation: '', contract_type: 'permanent' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Employee</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Employee</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="emp-user">User Email</Label>
                <Input id="emp-user" value={form.user} onChange={(e) => setForm({ ...form, user: e.target.value })} placeholder="user@example.com" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="emp-id">Employee ID</Label>
                  <Input id="emp-id" value={form.employee_id} onChange={(e) => setForm({ ...form, employee_id: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="emp-desig">Designation</Label>
                  <Input id="emp-desig" value={form.designation} onChange={(e) => setForm({ ...form, designation: e.target.value })} />
                </div>
              </div>
              <div className="grid gap-2">
                <Label>Contract Type</Label>
                <Select value={form.contract_type} onValueChange={(v) => setForm({ ...form, contract_type: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="permanent">Permanent</SelectItem>
                    <SelectItem value="contract">Contract</SelectItem>
                    <SelectItem value="temporary">Temporary</SelectItem>
                    <SelectItem value="probation">Probation</SelectItem>
                  </SelectContent>
                </Select>
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
        data={(data?.results ?? []) as Employee[]}
        columns={employeeColumns}
        searchPlaceholder="Search employees…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No employees found."
      />
    </>
  )
}

// ─── Leave Requests Tab ──────────────────────
const leaveStatusBadge: Record<string, 'secondary' | 'success' | 'warning' | 'destructive'> = {
  pending: 'warning',
  approved: 'success',
  rejected: 'destructive',
}

const leaveColumns: Column<LeaveRequest>[] = [
  { key: 'employee_name', header: 'Employee', sortable: true },
  { key: 'leave_type', header: 'Leave Type' },
  { key: 'start_date', header: 'Start Date', sortable: true, render: (l) => <>{formatDate(l.start_date)}</> },
  { key: 'end_date', header: 'End Date', render: (l) => <>{formatDate(l.end_date)}</> },
  { key: 'days', header: 'Days' },
  {
    key: 'status',
    header: 'Status',
    render: (l) => (
      <Badge variant={leaveStatusBadge[l.status] ?? 'secondary'}>
        {l.status}
      </Badge>
    ),
  },
]

function LeaveRequestsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['leave-requests', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<LeaveRequest>>('/hr/leave-requests/', { params })
      return data
    },
  })

  const actionMutation = useMutation({
    mutationFn: ({ id, action }: { id: string; action: 'approve' | 'reject' }) =>
      api.post(`/hr/leave-requests/${id}/${action}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['leave-requests'] }),
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  const columnsWithAction: Column<LeaveRequest>[] = [
    ...leaveColumns,
    {
      key: 'actions',
      header: 'Actions',
      render: (l) =>
        l.status === 'pending' ? (
          <div className="flex items-center gap-1">
            <Button
              size="sm"
              variant="ghost"
              className="text-green-600 hover:text-green-700"
              onClick={() => actionMutation.mutate({ id: l.id, action: 'approve' })}
              disabled={actionMutation.isPending}
            >
              <CheckCircle className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="text-red-600 hover:text-red-700"
              onClick={() => actionMutation.mutate({ id: l.id, action: 'reject' })}
              disabled={actionMutation.isPending}
            >
              <XCircle className="h-4 w-4" />
            </Button>
          </div>
        ) : null,
    },
  ]

  return (
    <DataTable
      data={(data?.results ?? []) as LeaveRequest[]}
      columns={columnsWithAction}
      searchPlaceholder="Search leave requests…"
      onSearch={(q) => { setSearch(q); setPage(1) }}
      isLoading={isLoading}
      pagination={{ page, totalPages, onPageChange: setPage }}
      emptyMessage="No leave requests found."
    />
  )
}

// ─── Recruitment Tab ─────────────────────────
const recruitStatusBadge: Record<string, 'secondary' | 'success' | 'warning' | 'destructive'> = {
  open: 'success',
  closed: 'secondary',
  on_hold: 'warning',
  cancelled: 'destructive',
}

const recruitmentColumns: Column<Recruitment>[] = [
  { key: 'position', header: 'Position', sortable: true },
  { key: 'department_name', header: 'Department' },
  { key: 'num_positions', header: 'Positions' },
  { key: 'application_deadline', header: 'Deadline', sortable: true, render: (r) => <>{formatDate(r.application_deadline)}</> },
  {
    key: 'status',
    header: 'Status',
    render: (r) => (
      <Badge variant={recruitStatusBadge[r.status] ?? 'secondary'}>
        {r.status.replace('_', ' ')}
      </Badge>
    ),
  },
]

function RecruitmentTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ position: '', department: '', num_positions: '', application_deadline: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['recruitments', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Recruitment>>('/hr/recruitments/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/hr/recruitments/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recruitments'] })
      setDialogOpen(false)
      setForm({ position: '', department: '', num_positions: '', application_deadline: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Recruitment</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Recruitment</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="rec-pos">Position</Label>
                  <Input id="rec-pos" value={form.position} onChange={(e) => setForm({ ...form, position: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="rec-dept">Department ID</Label>
                  <Input id="rec-dept" value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="rec-num">Number of Positions</Label>
                  <Input id="rec-num" type="number" value={form.num_positions} onChange={(e) => setForm({ ...form, num_positions: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="rec-deadline">Application Deadline</Label>
                  <Input id="rec-deadline" type="date" value={form.application_deadline} onChange={(e) => setForm({ ...form, application_deadline: e.target.value })} />
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
        data={(data?.results ?? []) as Recruitment[]}
        columns={recruitmentColumns}
        searchPlaceholder="Search recruitments…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No recruitments found."
      />
    </>
  )
}

// ─── Main Page ───────────────────────────────
export default function HrPage() {
  return (
    <div>
      <PageHeader title="Human Resources" description="Manage employees, leave requests, and recruitment" />
      <Tabs defaultValue="employees">
        <TabsList>
          <TabsTrigger value="employees">Employees</TabsTrigger>
          <TabsTrigger value="leave">Leave Requests</TabsTrigger>
          <TabsTrigger value="recruitment">Recruitment</TabsTrigger>
        </TabsList>
        <TabsContent value="employees"><EmployeesTab /></TabsContent>
        <TabsContent value="leave"><LeaveRequestsTab /></TabsContent>
        <TabsContent value="recruitment"><RecruitmentTab /></TabsContent>
      </Tabs>
    </div>
  )
}
