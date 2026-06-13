import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, LogIn, LogOut } from 'lucide-react'
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

// ─── Types ───────────────────────────────────
interface Building {
  id: string
  name: string
  code: string
  warden: string
  warden_name: string
  total_rooms: number
  is_active: boolean
  [key: string]: unknown
}

interface Room {
  id: string
  room_number: string
  room_type: string
  capacity: number
  occupied: number
  monthly_fee: number
  is_available: boolean
  [key: string]: unknown
}

interface Allocation {
  id: string
  student: string
  student_name: string
  room: string
  room_number: string
  check_in_date: string
  check_out_date: string | null
  monthly_fee: number
  is_active: boolean
  [key: string]: unknown
}

// ─── Buildings Tab ───────────────────────────
const buildingColumns: Column<Building>[] = [
  { key: 'name', header: 'Name', sortable: true },
  { key: 'code', header: 'Code' },
  { key: 'warden_name', header: 'Warden' },
  { key: 'total_rooms', header: 'Total Rooms' },
  {
    key: 'is_active',
    header: 'Status',
    render: (b) => (
      <Badge variant={b.is_active ? 'success' : 'secondary'}>
        {b.is_active ? 'Active' : 'Inactive'}
      </Badge>
    ),
  },
]

function BuildingsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ name: '', code: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['hostel-buildings', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Building>>('/hostel/buildings/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/hostel/buildings/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hostel-buildings'] })
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
            <Button><Plus className="mr-2 h-4 w-4" />Add Building</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Building</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="bld-name">Name</Label>
                  <Input id="bld-name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="bld-code">Code</Label>
                  <Input id="bld-code" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
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
        data={(data?.results ?? []) as Building[]}
        columns={buildingColumns}
        searchPlaceholder="Search buildings…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No buildings found."
      />
    </>
  )
}

// ─── Rooms Tab ───────────────────────────────
const roomTypeBadge: Record<string, 'secondary' | 'success' | 'warning'> = {
  single: 'success',
  double: 'warning',
  dormitory: 'secondary',
  suite: 'success',
}

const roomColumns: Column<Room>[] = [
  { key: 'room_number', header: 'Room #', sortable: true },
  {
    key: 'room_type',
    header: 'Type',
    render: (r) => (
      <Badge variant={roomTypeBadge[r.room_type] ?? 'secondary'}>
        {r.room_type}
      </Badge>
    ),
  },
  { key: 'capacity', header: 'Capacity' },
  { key: 'occupied', header: 'Occupied' },
  { key: 'monthly_fee', header: 'Monthly Fee', sortable: true, render: (r) => <>{formatCurrency(r.monthly_fee)}</> },
  {
    key: 'is_available',
    header: 'Available',
    render: (r) => (
      <Badge variant={r.is_available ? 'success' : 'destructive'}>
        {r.is_available ? 'Available' : 'Full'}
      </Badge>
    ),
  },
]

function RoomsTab() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['hostel-rooms', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Room>>('/hostel/rooms/', { params })
      return data
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <DataTable
      data={(data?.results ?? []) as Room[]}
      columns={roomColumns}
      searchPlaceholder="Search rooms…"
      onSearch={(q) => { setSearch(q); setPage(1) }}
      isLoading={isLoading}
      pagination={{ page, totalPages, onPageChange: setPage }}
      emptyMessage="No rooms found."
    />
  )
}

// ─── Allocations Tab ─────────────────────────
const allocationColumns: Column<Allocation>[] = [
  { key: 'student_name', header: 'Student', sortable: true },
  { key: 'room_number', header: 'Room' },
  { key: 'check_in_date', header: 'Check-in', sortable: true, render: (a) => <>{formatDate(a.check_in_date)}</> },
  { key: 'check_out_date', header: 'Check-out', render: (a) => <>{a.check_out_date ? formatDate(a.check_out_date) : '—'}</> },
  { key: 'monthly_fee', header: 'Monthly Fee', render: (a) => <>{formatCurrency(a.monthly_fee)}</> },
  {
    key: 'is_active',
    header: 'Status',
    render: (a) => (
      <Badge variant={a.is_active ? 'success' : 'secondary'}>
        {a.is_active ? 'Active' : 'Inactive'}
      </Badge>
    ),
  },
]

function AllocationsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['hostel-allocations', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Allocation>>('/hostel/allocations/', { params })
      return data
    },
  })

  const checkInMutation = useMutation({
    mutationFn: (id: string) => api.post(`/hostel/allocations/${id}/check-in/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['hostel-allocations'] }),
  })

  const checkOutMutation = useMutation({
    mutationFn: (id: string) => api.post(`/hostel/allocations/${id}/check-out/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['hostel-allocations'] }),
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  const columnsWithAction: Column<Allocation>[] = [
    ...allocationColumns,
    {
      key: 'actions',
      header: 'Actions',
      render: (a) => (
        <div className="flex gap-1">
          {!a.check_in_date && (
            <Button size="sm" variant="outline" onClick={() => checkInMutation.mutate(a.id)} disabled={checkInMutation.isPending}>
              <LogIn className="mr-1 h-3 w-3" />Check-in
            </Button>
          )}
          {a.is_active && a.check_in_date && !a.check_out_date && (
            <Button size="sm" variant="outline" onClick={() => checkOutMutation.mutate(a.id)} disabled={checkOutMutation.isPending}>
              <LogOut className="mr-1 h-3 w-3" />Check-out
            </Button>
          )}
        </div>
      ),
    },
  ]

  return (
    <DataTable
      data={(data?.results ?? []) as Allocation[]}
      columns={columnsWithAction}
      searchPlaceholder="Search allocations…"
      onSearch={(q) => { setSearch(q); setPage(1) }}
      isLoading={isLoading}
      pagination={{ page, totalPages, onPageChange: setPage }}
      emptyMessage="No allocations found."
    />
  )
}

// ─── Main Page ───────────────────────────────
export default function HostelPage() {
  return (
    <div>
      <PageHeader title="Hostel" description="Manage buildings, rooms, and allocations" />
      <Tabs defaultValue="buildings">
        <TabsList>
          <TabsTrigger value="buildings">Buildings</TabsTrigger>
          <TabsTrigger value="rooms">Rooms</TabsTrigger>
          <TabsTrigger value="allocations">Allocations</TabsTrigger>
        </TabsList>
        <TabsContent value="buildings"><BuildingsTab /></TabsContent>
        <TabsContent value="rooms"><RoomsTab /></TabsContent>
        <TabsContent value="allocations"><AllocationsTab /></TabsContent>
      </Tabs>
    </div>
  )
}
