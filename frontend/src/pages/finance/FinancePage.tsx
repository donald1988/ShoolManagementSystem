import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, DollarSign, TrendingUp, AlertCircle, Receipt } from 'lucide-react'
import api from '@/lib/api'
import { formatDate, formatCurrency } from '@/lib/utils'
import type { PaginatedResponse, Invoice, Payment, FeeCategory } from '@/types'
import { PageHeader } from '@/components/layout/PageHeader'
import { StatsCard, StatsGrid } from '@/components/layout/StatsCard'
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
interface Scholarship {
  id: string
  name: string
  discount_type: string
  discount_value: number
  is_active: boolean
}

interface InvoiceStats {
  total_due: number
  total_collected: number
  total_outstanding: number
  overdue_count: number
}

// ─── Invoices Tab ────────────────────────────
const invoiceStatusBadge: Record<string, 'success' | 'destructive' | 'warning' | 'secondary'> = {
  paid: 'success',
  overdue: 'destructive',
  partially_paid: 'warning',
  issued: 'secondary',
}

const invoiceColumns: Column<Invoice>[] = [
  { key: 'invoice_number', header: 'Invoice #', sortable: true },
  { key: 'student_name', header: 'Student', sortable: true },
  { key: 'issue_date', header: 'Issue Date', sortable: true, render: (i) => <>{formatDate(i.issue_date)}</> },
  { key: 'due_date', header: 'Due Date', sortable: true, render: (i) => <>{formatDate(i.due_date)}</> },
  { key: 'total_amount', header: 'Total', sortable: true, render: (i) => <>{formatCurrency(i.total_amount)}</> },
  { key: 'paid_amount', header: 'Paid', render: (i) => <>{formatCurrency(i.paid_amount)}</> },
  { key: 'balance', header: 'Balance', render: (i) => <>{formatCurrency(i.balance)}</> },
  {
    key: 'status',
    header: 'Status',
    render: (i) => (
      <Badge variant={invoiceStatusBadge[i.status] ?? 'secondary'}>
        {i.status.replace('_', ' ')}
      </Badge>
    ),
  },
]

function InvoicesTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ student: '', due_date: '', total_amount: '' })

  const { data: stats } = useQuery({
    queryKey: ['invoice-stats'],
    queryFn: async () => {
      const { data } = await api.get<InvoiceStats>('/finance/invoices/stats/')
      return data
    },
  })

  const { data, isLoading } = useQuery({
    queryKey: ['invoices', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Invoice>>('/finance/invoices/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/finance/invoices/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] })
      queryClient.invalidateQueries({ queryKey: ['invoice-stats'] })
      setDialogOpen(false)
      setForm({ student: '', due_date: '', total_amount: '' })
    },
  })

  const issueMutation = useMutation({
    mutationFn: (id: string) => api.post(`/finance/invoices/${id}/issue/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] })
      queryClient.invalidateQueries({ queryKey: ['invoice-stats'] })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  const columnsWithAction: Column<Invoice>[] = [
    ...invoiceColumns,
    {
      key: 'actions',
      header: 'Actions',
      render: (i) =>
        i.status === 'issued' ? null : (
          <Button size="sm" variant="outline" onClick={() => issueMutation.mutate(i.id)} disabled={issueMutation.isPending}>
            Issue
          </Button>
        ),
    },
  ]

  return (
    <>
      <StatsGrid>
        <StatsCard title="Total Due" value={formatCurrency(stats?.total_due ?? 0)} icon={DollarSign} />
        <StatsCard title="Collected" value={formatCurrency(stats?.total_collected ?? 0)} icon={TrendingUp} />
        <StatsCard title="Outstanding" value={formatCurrency(stats?.total_outstanding ?? 0)} icon={Receipt} />
        <StatsCard title="Overdue" value={stats?.overdue_count ?? 0} icon={AlertCircle} />
      </StatsGrid>

      <div className="mt-6 mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Invoice</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Invoice</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="inv-student">Student ID</Label>
                <Input id="inv-student" value={form.student} onChange={(e) => setForm({ ...form, student: e.target.value })} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="inv-due">Due Date</Label>
                  <Input id="inv-due" type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="inv-amount">Total Amount</Label>
                  <Input id="inv-amount" type="number" value={form.total_amount} onChange={(e) => setForm({ ...form, total_amount: e.target.value })} />
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
        data={(data?.results ?? []) as (Invoice & Record<string, unknown>)[]}
        columns={columnsWithAction}
        searchPlaceholder="Search invoices…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No invoices found."
      />
    </>
  )
}

// ─── Payments Tab ────────────────────────────
const paymentMethodBadge: Record<string, 'secondary' | 'success' | 'warning'> = {
  cash: 'secondary',
  credit_card: 'success',
  bank_transfer: 'warning',
  stripe: 'success',
  paypal: 'success',
}

const paymentColumns: Column<Payment>[] = [
  { key: 'receipt_number', header: 'Receipt #', sortable: true },
  { key: 'student_name', header: 'Student', sortable: true },
  { key: 'amount', header: 'Amount', sortable: true, render: (p) => <>{formatCurrency(p.amount)}</> },
  {
    key: 'payment_method',
    header: 'Method',
    render: (p) => (
      <Badge variant={paymentMethodBadge[p.payment_method] ?? 'secondary'}>
        {p.payment_method.replace('_', ' ')}
      </Badge>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (p) => (
      <Badge variant={p.status === 'completed' ? 'success' : p.status === 'failed' ? 'destructive' : 'secondary'}>
        {p.status}
      </Badge>
    ),
  },
  { key: 'payment_date', header: 'Date', sortable: true, render: (p) => <>{formatDate(p.payment_date)}</> },
]

function PaymentsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ invoice: '', amount: '', payment_method: 'cash' })

  const { data, isLoading } = useQuery({
    queryKey: ['payments', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Payment>>('/finance/payments/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/finance/payments/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] })
      setDialogOpen(false)
      setForm({ invoice: '', amount: '', payment_method: 'cash' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Payment</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Payment</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="pay-invoice">Invoice ID</Label>
                <Input id="pay-invoice" value={form.invoice} onChange={(e) => setForm({ ...form, invoice: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="pay-amount">Amount</Label>
                <Input id="pay-amount" type="number" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="pay-method">Payment Method</Label>
                <Select value={form.payment_method} onValueChange={(v) => setForm({ ...form, payment_method: v })}>
                  <SelectTrigger id="pay-method"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="cash">Cash</SelectItem>
                    <SelectItem value="credit_card">Credit Card</SelectItem>
                    <SelectItem value="bank_transfer">Bank Transfer</SelectItem>
                    <SelectItem value="stripe">Stripe</SelectItem>
                    <SelectItem value="paypal">PayPal</SelectItem>
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
        data={(data?.results ?? []) as (Payment & Record<string, unknown>)[]}
        columns={paymentColumns}
        searchPlaceholder="Search payments…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No payments found."
      />
    </>
  )
}

// ─── Fee Categories Tab ──────────────────────
const feeCategoryColumns: Column<FeeCategory>[] = [
  { key: 'name', header: 'Name', sortable: true },
  {
    key: 'is_recurring',
    header: 'Recurring',
    render: (f) => (
      <Badge variant={f.is_recurring ? 'success' : 'secondary'}>
        {f.is_recurring ? 'Yes' : 'No'}
      </Badge>
    ),
  },
  {
    key: 'is_active',
    header: 'Active',
    render: (f) => (
      <Badge variant={f.is_active ? 'success' : 'secondary'}>
        {f.is_active ? 'Active' : 'Inactive'}
      </Badge>
    ),
  },
]

function FeeCategoriesTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ name: '', is_recurring: false })

  const { data, isLoading } = useQuery({
    queryKey: ['fee-categories', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<FeeCategory>>('/finance/fee-categories/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/finance/fee-categories/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fee-categories'] })
      setDialogOpen(false)
      setForm({ name: '', is_recurring: false })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Category</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add Fee Category</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="fc-name">Name</Label>
                <Input id="fc-name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </div>
              <div className="flex items-center gap-2">
                <input
                  id="fc-recurring"
                  type="checkbox"
                  checked={form.is_recurring}
                  onChange={(e) => setForm({ ...form, is_recurring: e.target.checked })}
                  className="h-4 w-4 rounded border-gray-300"
                />
                <Label htmlFor="fc-recurring">Recurring</Label>
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
        data={(data?.results ?? []) as (FeeCategory & Record<string, unknown>)[]}
        columns={feeCategoryColumns}
        searchPlaceholder="Search categories…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No fee categories found."
      />
    </>
  )
}

// ─── Scholarships Tab ────────────────────────
const scholarshipColumns: Column<Scholarship>[] = [
  { key: 'name', header: 'Name', sortable: true },
  { key: 'discount_type', header: 'Discount Type' },
  {
    key: 'discount_value',
    header: 'Value',
    render: (s) => <>{s.discount_type === 'percentage' ? `${s.discount_value}%` : formatCurrency(s.discount_value)}</>,
  },
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

function ScholarshipsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ name: '', discount_type: 'percentage', discount_value: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['scholarships', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Scholarship>>('/finance/scholarships/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/finance/scholarships/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scholarships'] })
      setDialogOpen(false)
      setForm({ name: '', discount_type: 'percentage', discount_value: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Scholarship</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add Scholarship</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="sch-name">Name</Label>
                <Input id="sch-name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="sch-type">Discount Type</Label>
                  <Select value={form.discount_type} onValueChange={(v) => setForm({ ...form, discount_type: v })}>
                    <SelectTrigger id="sch-type"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="percentage">Percentage</SelectItem>
                      <SelectItem value="fixed">Fixed Amount</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="sch-value">Value</Label>
                  <Input id="sch-value" type="number" value={form.discount_value} onChange={(e) => setForm({ ...form, discount_value: e.target.value })} />
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
        data={(data?.results ?? []) as (Scholarship & Record<string, unknown>)[]}
        columns={scholarshipColumns}
        searchPlaceholder="Search scholarships…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No scholarships found."
      />
    </>
  )
}

// ─── Main Page ───────────────────────────────
export default function FinancePage() {
  return (
    <div>
      <PageHeader title="Finance" description="Manage invoices, payments, fees, and scholarships" />
      <Tabs defaultValue="invoices">
        <TabsList>
          <TabsTrigger value="invoices">Invoices</TabsTrigger>
          <TabsTrigger value="payments">Payments</TabsTrigger>
          <TabsTrigger value="fee-categories">Fee Categories</TabsTrigger>
          <TabsTrigger value="scholarships">Scholarships</TabsTrigger>
        </TabsList>
        <TabsContent value="invoices"><InvoicesTab /></TabsContent>
        <TabsContent value="payments"><PaymentsTab /></TabsContent>
        <TabsContent value="fee-categories"><FeeCategoriesTab /></TabsContent>
        <TabsContent value="scholarships"><ScholarshipsTab /></TabsContent>
      </Tabs>
    </div>
  )
}
