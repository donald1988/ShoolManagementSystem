import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import api from '@/lib/api'
import type { PaginatedResponse, Parent } from '@/types'
import { PageHeader } from '@/components/layout/PageHeader'
import { DataTable, type Column } from '@/components/ui/data-table'
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

const columns: Column<Parent>[] = [
  { key: 'full_name', header: 'Full Name', sortable: true },
  { key: 'email', header: 'Email' },
  { key: 'occupation', header: 'Occupation' },
  {
    key: 'children',
    header: 'Children',
    render: (p) => <span>{p.children?.length ?? 0}</span>,
  },
]

export default function ParentsPage() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({
    user: '',
    occupation: '',
  })

  const { data, isLoading } = useQuery({
    queryKey: ['parents', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Parent>>('/students/parents/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/students/parents/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['parents'] })
      setDialogOpen(false)
      setForm({ user: '', occupation: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />

  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <div>
      <PageHeader title="Parents / Guardians" description="Manage parent records">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Parent</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Parent</DialogTitle>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="user">User Email</Label>
                <Input id="user" value={form.user} onChange={(e) => setForm({ ...form, user: e.target.value })} placeholder="parent@example.com" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="occupation">Occupation</Label>
                <Input id="occupation" value={form.occupation} onChange={(e) => setForm({ ...form, occupation: e.target.value })} />
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
        data={(data?.results ?? []) as (Parent & Record<string, unknown>)[]}
        columns={columns}
        searchPlaceholder="Search by name or email…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No parents found."
      />
    </div>
  )
}
