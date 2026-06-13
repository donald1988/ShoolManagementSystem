import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import api from '@/lib/api'
import { formatDate, formatCurrency } from '@/lib/utils'
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
interface Asset {
  id: string
  asset_code: string
  name: string
  category: string
  condition: string
  status: string
  location: string
  [key: string]: unknown
}

interface Maintenance {
  id: string
  asset: string
  asset_name: string
  maintenance_type: string
  scheduled_date: string
  completed_date: string | null
  cost: number
  status: string
  [key: string]: unknown
}

// ─── Assets Tab ──────────────────────────────
const conditionBadge: Record<string, 'secondary' | 'success' | 'warning' | 'destructive'> = {
  new: 'success',
  good: 'secondary',
  poor: 'warning',
  damaged: 'destructive',
}

const assetStatusBadge: Record<string, 'secondary' | 'success' | 'warning'> = {
  available: 'success',
  in_use: 'secondary',
  maintenance: 'warning',
}

const assetColumns: Column<Asset>[] = [
  { key: 'asset_code', header: 'Asset Code', sortable: true },
  { key: 'name', header: 'Name', sortable: true },
  { key: 'category', header: 'Category' },
  {
    key: 'condition',
    header: 'Condition',
    render: (a) => (
      <Badge variant={conditionBadge[a.condition] ?? 'secondary'}>
        {a.condition}
      </Badge>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (a) => (
      <Badge variant={assetStatusBadge[a.status] ?? 'secondary'}>
        {a.status.replace('_', ' ')}
      </Badge>
    ),
  },
  { key: 'location', header: 'Location' },
]

function AssetsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ asset_code: '', name: '', category: '', condition: 'new', location: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['assets', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Asset>>('/inventory/assets/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/inventory/assets/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] })
      setDialogOpen(false)
      setForm({ asset_code: '', name: '', category: '', condition: 'new', location: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Asset</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Asset</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="ast-code">Asset Code</Label>
                  <Input id="ast-code" value={form.asset_code} onChange={(e) => setForm({ ...form, asset_code: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="ast-name">Name</Label>
                  <Input id="ast-name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="ast-cat">Category</Label>
                  <Input id="ast-cat" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label>Condition</Label>
                  <Select value={form.condition} onValueChange={(v) => setForm({ ...form, condition: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="new">New</SelectItem>
                      <SelectItem value="good">Good</SelectItem>
                      <SelectItem value="poor">Poor</SelectItem>
                      <SelectItem value="damaged">Damaged</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="ast-loc">Location</Label>
                <Input id="ast-loc" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
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
        data={(data?.results ?? []) as Asset[]}
        columns={assetColumns}
        searchPlaceholder="Search assets…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No assets found."
      />
    </>
  )
}

// ─── Maintenance Tab ─────────────────────────
const maintTypeBadge: Record<string, 'secondary' | 'success' | 'warning'> = {
  preventive: 'success',
  corrective: 'warning',
  emergency: 'warning',
  routine: 'secondary',
}

const maintStatusBadge: Record<string, 'secondary' | 'success' | 'warning' | 'destructive'> = {
  scheduled: 'secondary',
  in_progress: 'warning',
  completed: 'success',
  cancelled: 'destructive',
}

const maintenanceColumns: Column<Maintenance>[] = [
  { key: 'asset_name', header: 'Asset', sortable: true },
  {
    key: 'maintenance_type',
    header: 'Type',
    render: (m) => (
      <Badge variant={maintTypeBadge[m.maintenance_type] ?? 'secondary'}>
        {m.maintenance_type}
      </Badge>
    ),
  },
  { key: 'scheduled_date', header: 'Scheduled', sortable: true, render: (m) => <>{formatDate(m.scheduled_date)}</> },
  { key: 'completed_date', header: 'Completed', render: (m) => <>{m.completed_date ? formatDate(m.completed_date) : '—'}</> },
  { key: 'cost', header: 'Cost', render: (m) => <>{formatCurrency(m.cost)}</> },
  {
    key: 'status',
    header: 'Status',
    render: (m) => (
      <Badge variant={maintStatusBadge[m.status] ?? 'secondary'}>
        {m.status.replace('_', ' ')}
      </Badge>
    ),
  },
]

function MaintenanceTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ asset: '', maintenance_type: 'preventive', scheduled_date: '', cost: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['maintenance', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Maintenance>>('/inventory/maintenance/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/inventory/maintenance/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance'] })
      setDialogOpen(false)
      setForm({ asset: '', maintenance_type: 'preventive', scheduled_date: '', cost: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Maintenance</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add Maintenance Record</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="mnt-asset">Asset ID</Label>
                  <Input id="mnt-asset" value={form.asset} onChange={(e) => setForm({ ...form, asset: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label>Maintenance Type</Label>
                  <Select value={form.maintenance_type} onValueChange={(v) => setForm({ ...form, maintenance_type: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="preventive">Preventive</SelectItem>
                      <SelectItem value="corrective">Corrective</SelectItem>
                      <SelectItem value="emergency">Emergency</SelectItem>
                      <SelectItem value="routine">Routine</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="mnt-date">Scheduled Date</Label>
                  <Input id="mnt-date" type="date" value={form.scheduled_date} onChange={(e) => setForm({ ...form, scheduled_date: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="mnt-cost">Cost</Label>
                  <Input id="mnt-cost" type="number" value={form.cost} onChange={(e) => setForm({ ...form, cost: e.target.value })} />
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
        data={(data?.results ?? []) as Maintenance[]}
        columns={maintenanceColumns}
        searchPlaceholder="Search maintenance…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No maintenance records found."
      />
    </>
  )
}

// ─── Main Page ───────────────────────────────
export default function InventoryPage() {
  return (
    <div>
      <PageHeader title="Inventory" description="Manage assets and maintenance" />
      <Tabs defaultValue="assets">
        <TabsList>
          <TabsTrigger value="assets">Assets</TabsTrigger>
          <TabsTrigger value="maintenance">Maintenance</TabsTrigger>
        </TabsList>
        <TabsContent value="assets"><AssetsTab /></TabsContent>
        <TabsContent value="maintenance"><MaintenanceTab /></TabsContent>
      </Tabs>
    </div>
  )
}
