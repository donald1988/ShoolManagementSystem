import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, CheckCircle, Banknote } from 'lucide-react'
import api from '@/lib/api'
import { formatCurrency } from '@/lib/utils'
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

// ─── Types ───────────────────────────────────
interface Payslip {
  id: string
  employee: string
  employee_name: string
  month: number
  year: number
  gross_salary: number
  total_deductions: number
  net_salary: number
  status: string
}

interface SalaryStructure {
  id: string
  name: string
  base_salary: number
  gross_salary: number
  net_salary: number
  is_active: boolean
}

interface PayrollRun {
  id: string
  month: number
  year: number
  total_employees: number
  total_net: number
  status: string
}

const payslipStatusBadge: Record<string, 'secondary' | 'success' | 'warning' | 'destructive'> = {
  draft: 'secondary',
  approved: 'warning',
  paid: 'success',
  cancelled: 'destructive',
}

const monthName = (m: number) =>
  new Date(2000, m - 1).toLocaleString('en-US', { month: 'long' })

// ─── Payslips Tab ────────────────────────────
const payslipColumns: Column<Payslip>[] = [
  { key: 'employee_name', header: 'Employee', sortable: true },
  { key: 'month', header: 'Month', render: (p) => <>{monthName(p.month)}</> },
  { key: 'year', header: 'Year', sortable: true },
  { key: 'gross_salary', header: 'Gross', sortable: true, render: (p) => <>{formatCurrency(p.gross_salary)}</> },
  { key: 'total_deductions', header: 'Deductions', render: (p) => <>{formatCurrency(p.total_deductions)}</> },
  { key: 'net_salary', header: 'Net', sortable: true, render: (p) => <>{formatCurrency(p.net_salary)}</> },
  {
    key: 'status',
    header: 'Status',
    render: (p) => (
      <Badge variant={payslipStatusBadge[p.status] ?? 'secondary'}>{p.status}</Badge>
    ),
  },
]

function PayslipsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['payslips', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Payslip>>('/payroll/payslips/', { params })
      return data
    },
  })

  const approveMutation = useMutation({
    mutationFn: (id: string) => api.post(`/payroll/payslips/${id}/approve/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['payslips'] }),
  })

  const markPaidMutation = useMutation({
    mutationFn: (id: string) => api.post(`/payroll/payslips/${id}/mark-paid/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['payslips'] }),
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  const columnsWithAction: Column<Payslip>[] = [
    ...payslipColumns,
    {
      key: 'actions',
      header: 'Actions',
      render: (p) => (
        <div className="flex gap-1">
          {p.status === 'draft' && (
            <Button size="sm" variant="outline" onClick={() => approveMutation.mutate(p.id)} disabled={approveMutation.isPending}>
              <CheckCircle className="mr-1 h-3 w-3" />Approve
            </Button>
          )}
          {p.status === 'approved' && (
            <Button size="sm" variant="outline" onClick={() => markPaidMutation.mutate(p.id)} disabled={markPaidMutation.isPending}>
              <Banknote className="mr-1 h-3 w-3" />Mark Paid
            </Button>
          )}
        </div>
      ),
    },
  ]

  return (
    <DataTable
      data={(data?.results ?? []) as (Payslip & Record<string, unknown>)[]}
      columns={columnsWithAction}
      searchPlaceholder="Search payslips…"
      onSearch={(q) => { setSearch(q); setPage(1) }}
      isLoading={isLoading}
      pagination={{ page, totalPages, onPageChange: setPage }}
      emptyMessage="No payslips found."
    />
  )
}

// ─── Salary Structures Tab ───────────────────
const salaryColumns: Column<SalaryStructure>[] = [
  { key: 'name', header: 'Name', sortable: true },
  { key: 'base_salary', header: 'Base', sortable: true, render: (s) => <>{formatCurrency(s.base_salary)}</> },
  { key: 'gross_salary', header: 'Gross', render: (s) => <>{formatCurrency(s.gross_salary)}</> },
  { key: 'net_salary', header: 'Net', render: (s) => <>{formatCurrency(s.net_salary)}</> },
  {
    key: 'is_active',
    header: 'Active',
    render: (s) => (
      <Badge variant={s.is_active ? 'success' : 'secondary'}>
        {s.is_active ? 'Active' : 'Inactive'}
      </Badge>
    ),
  },
]

function SalaryStructuresTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ name: '', base_salary: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['salary-structures', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<SalaryStructure>>('/payroll/salary-structures/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/payroll/salary-structures/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['salary-structures'] })
      setDialogOpen(false)
      setForm({ name: '', base_salary: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Structure</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add Salary Structure</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="ss-name">Name</Label>
                <Input id="ss-name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="ss-base">Base Salary</Label>
                <Input id="ss-base" type="number" value={form.base_salary} onChange={(e) => setForm({ ...form, base_salary: e.target.value })} />
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
        data={(data?.results ?? []) as (SalaryStructure & Record<string, unknown>)[]}
        columns={salaryColumns}
        searchPlaceholder="Search structures…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No salary structures found."
      />
    </>
  )
}

// ─── Payroll Runs Tab ────────────────────────
const runStatusBadge: Record<string, 'secondary' | 'success' | 'warning' | 'destructive'> = {
  draft: 'secondary',
  processing: 'warning',
  completed: 'success',
  cancelled: 'destructive',
}

const runColumns: Column<PayrollRun>[] = [
  { key: 'month', header: 'Month', render: (r) => <>{monthName(r.month)}</> },
  { key: 'year', header: 'Year', sortable: true },
  { key: 'total_employees', header: 'Employees' },
  { key: 'total_net', header: 'Total Net', sortable: true, render: (r) => <>{formatCurrency(r.total_net)}</> },
  {
    key: 'status',
    header: 'Status',
    render: (r) => (
      <Badge variant={runStatusBadge[r.status] ?? 'secondary'}>{r.status}</Badge>
    ),
  },
]

function PayrollRunsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ month: '', year: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['payroll-runs', page],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      const { data } = await api.get<PaginatedResponse<PayrollRun>>('/payroll/runs/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/payroll/runs/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payroll-runs'] })
      setDialogOpen(false)
      setForm({ month: '', year: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />New Payroll Run</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>New Payroll Run</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="pr-month">Month</Label>
                  <Input id="pr-month" type="number" min={1} max={12} value={form.month} onChange={(e) => setForm({ ...form, month: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="pr-year">Year</Label>
                  <Input id="pr-year" type="number" value={form.year} onChange={(e) => setForm({ ...form, year: e.target.value })} />
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
        data={(data?.results ?? []) as (PayrollRun & Record<string, unknown>)[]}
        columns={runColumns}
        searchPlaceholder="Search runs…"
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No payroll runs found."
      />
    </>
  )
}

// ─── Main Page ───────────────────────────────
export default function PayrollPage() {
  return (
    <div>
      <PageHeader title="Payroll" description="Manage payslips, salary structures, and payroll runs" />
      <Tabs defaultValue="payslips">
        <TabsList>
          <TabsTrigger value="payslips">Payslips</TabsTrigger>
          <TabsTrigger value="salary-structures">Salary Structures</TabsTrigger>
          <TabsTrigger value="payroll-runs">Payroll Runs</TabsTrigger>
        </TabsList>
        <TabsContent value="payslips"><PayslipsTab /></TabsContent>
        <TabsContent value="salary-structures"><SalaryStructuresTab /></TabsContent>
        <TabsContent value="payroll-runs"><PayrollRunsTab /></TabsContent>
      </Tabs>
    </div>
  )
}
