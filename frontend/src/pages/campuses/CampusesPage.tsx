import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import api from '@/lib/api'
import type { PaginatedResponse } from '@/types'
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

// ─── Types ───────────────────────────────────
interface Campus {
  id: string
  name: string
  code: string
  school_name: string
  city: string
  is_main: boolean
  is_active: boolean
  [key: string]: unknown
}

const columns: Column<Campus>[] = [
  { key: 'name', header: 'Name', sortable: true },
  { key: 'code', header: 'Code' },
  { key: 'school_name', header: 'School' },
  { key: 'city', header: 'City' },
  {
    key: 'is_main',
    header: 'Main',
    render: (c) => (
      <Badge variant={c.is_main ? 'success' : 'secondary'}>
        {c.is_main ? 'Main' : 'Branch'}
      </Badge>
    ),
  },
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

export default function CampusesPage() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ name: '', code: '', city: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['campuses', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Campus>>('/core/campuses/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/core/campuses/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campuses'] })
      setDialogOpen(false)
      setForm({ name: '', code: '', city: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />

  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <div>
      <PageHeader title="Campuses" description="Manage school campuses">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Campus</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Campus</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="campus-name">Name</Label>
                  <Input id="campus-name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="campus-code">Code</Label>
                  <Input id="campus-code" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="campus-city">City</Label>
                <Input id="campus-city" value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} />
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
        data={(data?.results ?? []) as Campus[]}
        columns={columns}
        searchPlaceholder="Search campuses…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No campuses found."
      />
    </div>
  )
}
