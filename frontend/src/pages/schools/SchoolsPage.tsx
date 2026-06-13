import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import api from '@/lib/api'
import type { PaginatedResponse, School } from '@/types'
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

const columns: Column<School>[] = [
  { key: 'name', header: 'Name', sortable: true },
  { key: 'code', header: 'Code' },
  { key: 'city', header: 'City' },
  { key: 'country', header: 'Country' },
  {
    key: 'subscription_plan',
    header: 'Plan',
    render: (s) => <Badge variant="secondary">{s.subscription_plan}</Badge>,
  },
  {
    key: 'is_active',
    header: 'Status',
    render: (s) => (
      <Badge variant={s.is_active ? 'success' : 'destructive'}>
        {s.is_active ? 'Active' : 'Inactive'}
      </Badge>
    ),
  },
  { key: 'max_students', header: 'Max Students' },
]

export default function SchoolsPage() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({
    name: '',
    code: '',
    email: '',
    phone: '',
    address_line1: '',
    city: '',
    state: '',
    country: '',
    postal_code: '',
    timezone: 'UTC',
    currency: 'USD',
    subscription_plan: 'basic',
    max_students: '',
    max_staff: '',
  })

  const { data, isLoading } = useQuery({
    queryKey: ['schools', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<School>>('/core/schools/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) =>
      api.post('/core/schools/', {
        ...payload,
        max_students: Number(payload.max_students) || 500,
        max_staff: Number(payload.max_staff) || 100,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schools'] })
      setDialogOpen(false)
      setForm({ name: '', code: '', email: '', phone: '', address_line1: '', city: '', state: '', country: '', postal_code: '', timezone: 'UTC', currency: 'USD', subscription_plan: 'basic', max_students: '', max_staff: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />

  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <div>
      <PageHeader title="Schools" description="Manage schools (Super Admin)">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add School</Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Add New School</DialogTitle>
            </DialogHeader>
            <div className="grid gap-4 py-4 max-h-[60vh] overflow-y-auto pr-2">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="name">School Name</Label>
                  <Input id="name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="code">Code</Label>
                  <Input id="code" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="phone">Phone</Label>
                  <Input id="phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="address">Address</Label>
                <Input id="address" value={form.address_line1} onChange={(e) => setForm({ ...form, address_line1: e.target.value })} />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="city">City</Label>
                  <Input id="city" value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="state">State</Label>
                  <Input id="state" value={form.state} onChange={(e) => setForm({ ...form, state: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="country">Country</Label>
                  <Input id="country" value={form.country} onChange={(e) => setForm({ ...form, country: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="postal_code">Postal Code</Label>
                  <Input id="postal_code" value={form.postal_code} onChange={(e) => setForm({ ...form, postal_code: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label>Timezone</Label>
                  <Input value={form.timezone} onChange={(e) => setForm({ ...form, timezone: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label>Currency</Label>
                  <Input value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="grid gap-2">
                  <Label>Subscription Plan</Label>
                  <Select value={form.subscription_plan} onValueChange={(v) => setForm({ ...form, subscription_plan: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="basic">Basic</SelectItem>
                      <SelectItem value="standard">Standard</SelectItem>
                      <SelectItem value="premium">Premium</SelectItem>
                      <SelectItem value="enterprise">Enterprise</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="max_students">Max Students</Label>
                  <Input id="max_students" type="number" value={form.max_students} onChange={(e) => setForm({ ...form, max_students: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="max_staff">Max Staff</Label>
                  <Input id="max_staff" type="number" value={form.max_staff} onChange={(e) => setForm({ ...form, max_staff: e.target.value })} />
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
        data={(data?.results ?? []) as (School & Record<string, unknown>)[]}
        columns={columns}
        searchPlaceholder="Search schools…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No schools found."
      />
    </div>
  )
}
