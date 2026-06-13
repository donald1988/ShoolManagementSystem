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
interface Vehicle {
  id: string
  vehicle_number: string
  vehicle_type: string
  capacity: number
  fuel_type: string
  is_active: boolean
  [key: string]: unknown
}

interface Route {
  id: string
  name: string
  code: string
  start_location: string
  end_location: string
  monthly_fee: number
  is_active: boolean
  [key: string]: unknown
}

interface Driver {
  id: string
  name: string
  phone: string
  license_number: string
  license_expiry: string
  is_active: boolean
  [key: string]: unknown
}

// ─── Vehicles Tab ────────────────────────────
const vehicleTypeBadge: Record<string, 'secondary' | 'success' | 'warning'> = {
  bus: 'success',
  van: 'warning',
  car: 'secondary',
  minibus: 'warning',
}

const vehicleColumns: Column<Vehicle>[] = [
  { key: 'vehicle_number', header: 'Vehicle #', sortable: true },
  {
    key: 'vehicle_type',
    header: 'Type',
    render: (v) => (
      <Badge variant={vehicleTypeBadge[v.vehicle_type] ?? 'secondary'}>
        {v.vehicle_type}
      </Badge>
    ),
  },
  { key: 'capacity', header: 'Capacity' },
  { key: 'fuel_type', header: 'Fuel' },
  {
    key: 'is_active',
    header: 'Status',
    render: (v) => (
      <Badge variant={v.is_active ? 'success' : 'secondary'}>
        {v.is_active ? 'Active' : 'Inactive'}
      </Badge>
    ),
  },
]

function VehiclesTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ vehicle_number: '', vehicle_type: 'bus', capacity: '', fuel_type: 'diesel' })

  const { data, isLoading } = useQuery({
    queryKey: ['vehicles', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Vehicle>>('/transport/vehicles/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/transport/vehicles/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] })
      setDialogOpen(false)
      setForm({ vehicle_number: '', vehicle_type: 'bus', capacity: '', fuel_type: 'diesel' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Vehicle</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Vehicle</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="veh-num">Vehicle Number</Label>
                  <Input id="veh-num" value={form.vehicle_number} onChange={(e) => setForm({ ...form, vehicle_number: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label>Vehicle Type</Label>
                  <Select value={form.vehicle_type} onValueChange={(v) => setForm({ ...form, vehicle_type: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="bus">Bus</SelectItem>
                      <SelectItem value="van">Van</SelectItem>
                      <SelectItem value="minibus">Minibus</SelectItem>
                      <SelectItem value="car">Car</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="veh-cap">Capacity</Label>
                  <Input id="veh-cap" type="number" value={form.capacity} onChange={(e) => setForm({ ...form, capacity: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label>Fuel Type</Label>
                  <Select value={form.fuel_type} onValueChange={(v) => setForm({ ...form, fuel_type: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="diesel">Diesel</SelectItem>
                      <SelectItem value="petrol">Petrol</SelectItem>
                      <SelectItem value="electric">Electric</SelectItem>
                      <SelectItem value="cng">CNG</SelectItem>
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
      </div>
      <DataTable
        data={(data?.results ?? []) as Vehicle[]}
        columns={vehicleColumns}
        searchPlaceholder="Search vehicles…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No vehicles found."
      />
    </>
  )
}

// ─── Routes Tab ──────────────────────────────
const routeColumns: Column<Route>[] = [
  { key: 'name', header: 'Name', sortable: true },
  { key: 'code', header: 'Code' },
  { key: 'start_location', header: 'Start' },
  { key: 'end_location', header: 'End' },
  { key: 'monthly_fee', header: 'Monthly Fee', sortable: true, render: (r) => <>{formatCurrency(r.monthly_fee)}</> },
  {
    key: 'is_active',
    header: 'Status',
    render: (r) => (
      <Badge variant={r.is_active ? 'success' : 'secondary'}>
        {r.is_active ? 'Active' : 'Inactive'}
      </Badge>
    ),
  },
]

function RoutesTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ name: '', code: '', start_location: '', end_location: '', monthly_fee: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['routes', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Route>>('/transport/routes/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/transport/routes/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['routes'] })
      setDialogOpen(false)
      setForm({ name: '', code: '', start_location: '', end_location: '', monthly_fee: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Route</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Route</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="rt-name">Name</Label>
                  <Input id="rt-name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="rt-code">Code</Label>
                  <Input id="rt-code" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="rt-start">Start Location</Label>
                  <Input id="rt-start" value={form.start_location} onChange={(e) => setForm({ ...form, start_location: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="rt-end">End Location</Label>
                  <Input id="rt-end" value={form.end_location} onChange={(e) => setForm({ ...form, end_location: e.target.value })} />
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="rt-fee">Monthly Fee</Label>
                <Input id="rt-fee" type="number" value={form.monthly_fee} onChange={(e) => setForm({ ...form, monthly_fee: e.target.value })} />
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
        data={(data?.results ?? []) as Route[]}
        columns={routeColumns}
        searchPlaceholder="Search routes…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No routes found."
      />
    </>
  )
}

// ─── Drivers Tab ─────────────────────────────
const driverColumns: Column<Driver>[] = [
  { key: 'name', header: 'Name', sortable: true },
  { key: 'phone', header: 'Phone' },
  { key: 'license_number', header: 'License #' },
  { key: 'license_expiry', header: 'License Expiry', sortable: true, render: (d) => <>{formatDate(d.license_expiry)}</> },
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

function DriversTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ name: '', phone: '', license_number: '', license_expiry: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['drivers', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Driver>>('/transport/drivers/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/transport/drivers/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drivers'] })
      setDialogOpen(false)
      setForm({ name: '', phone: '', license_number: '', license_expiry: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Driver</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Driver</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="drv-name">Name</Label>
                  <Input id="drv-name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="drv-phone">Phone</Label>
                  <Input id="drv-phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="drv-license">License Number</Label>
                  <Input id="drv-license" value={form.license_number} onChange={(e) => setForm({ ...form, license_number: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="drv-expiry">License Expiry</Label>
                  <Input id="drv-expiry" type="date" value={form.license_expiry} onChange={(e) => setForm({ ...form, license_expiry: e.target.value })} />
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
        data={(data?.results ?? []) as Driver[]}
        columns={driverColumns}
        searchPlaceholder="Search drivers…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No drivers found."
      />
    </>
  )
}

// ─── Main Page ───────────────────────────────
export default function TransportPage() {
  return (
    <div>
      <PageHeader title="Transport" description="Manage vehicles, routes, and drivers" />
      <Tabs defaultValue="vehicles">
        <TabsList>
          <TabsTrigger value="vehicles">Vehicles</TabsTrigger>
          <TabsTrigger value="routes">Routes</TabsTrigger>
          <TabsTrigger value="drivers">Drivers</TabsTrigger>
        </TabsList>
        <TabsContent value="vehicles"><VehiclesTab /></TabsContent>
        <TabsContent value="routes"><RoutesTab /></TabsContent>
        <TabsContent value="drivers"><DriversTab /></TabsContent>
      </Tabs>
    </div>
  )
}
