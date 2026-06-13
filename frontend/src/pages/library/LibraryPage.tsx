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

// ─── Types ───────────────────────────────────
interface Book {
  id: string
  title: string
  isbn: string
  author: string
  category: string
  total_copies: number
  available_copies: number
  is_active: boolean
  [key: string]: unknown
}

interface Transaction {
  id: string
  book_title: string
  member_name: string
  transaction_type: string
  issue_date: string
  due_date: string
  return_date: string | null
  fine_amount: number
  [key: string]: unknown
}

interface Membership {
  id: string
  user_name: string
  membership_number: string
  membership_type: string
  max_books: number
  is_active: boolean
  [key: string]: unknown
}

// ─── Books Tab ───────────────────────────────
const bookColumns: Column<Book>[] = [
  { key: 'title', header: 'Title', sortable: true },
  { key: 'isbn', header: 'ISBN' },
  { key: 'author', header: 'Author', sortable: true },
  { key: 'category', header: 'Category' },
  { key: 'total_copies', header: 'Total Copies' },
  { key: 'available_copies', header: 'Available' },
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

function BooksTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ title: '', isbn: '', author: '', category: '', total_copies: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['books', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Book>>('/library/books/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/library/books/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] })
      setDialogOpen(false)
      setForm({ title: '', isbn: '', author: '', category: '', total_copies: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Book</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add New Book</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="book-title">Title</Label>
                <Input id="book-title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="book-isbn">ISBN</Label>
                  <Input id="book-isbn" value={form.isbn} onChange={(e) => setForm({ ...form, isbn: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="book-author">Author</Label>
                  <Input id="book-author" value={form.author} onChange={(e) => setForm({ ...form, author: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="book-cat">Category</Label>
                  <Input id="book-cat" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="book-copies">Total Copies</Label>
                  <Input id="book-copies" type="number" value={form.total_copies} onChange={(e) => setForm({ ...form, total_copies: e.target.value })} />
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
        data={(data?.results ?? []) as Book[]}
        columns={bookColumns}
        searchPlaceholder="Search by title, ISBN, or author…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No books found."
      />
    </>
  )
}

// ─── Transactions Tab ────────────────────────
const txnTypeBadge: Record<string, 'secondary' | 'success' | 'warning' | 'destructive'> = {
  issue: 'warning',
  return: 'success',
  renew: 'secondary',
  lost: 'destructive',
}

const transactionColumns: Column<Transaction>[] = [
  { key: 'book_title', header: 'Book', sortable: true },
  { key: 'member_name', header: 'Member', sortable: true },
  {
    key: 'transaction_type',
    header: 'Type',
    render: (t) => (
      <Badge variant={txnTypeBadge[t.transaction_type] ?? 'secondary'}>
        {t.transaction_type}
      </Badge>
    ),
  },
  { key: 'issue_date', header: 'Issue Date', sortable: true, render: (t) => <>{formatDate(t.issue_date)}</> },
  { key: 'due_date', header: 'Due Date', render: (t) => <>{formatDate(t.due_date)}</> },
  { key: 'return_date', header: 'Return Date', render: (t) => <>{t.return_date ? formatDate(t.return_date) : '—'}</> },
  { key: 'fine_amount', header: 'Fine', render: (t) => <>{formatCurrency(t.fine_amount)}</> },
]

function TransactionsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ book: '', member: '', due_date: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['library-transactions', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Transaction>>('/library/transactions/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/library/transactions/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['library-transactions'] })
      setDialogOpen(false)
      setForm({ book: '', member: '', due_date: '' })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Issue Book</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Issue Book</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="txn-book">Book ID</Label>
                  <Input id="txn-book" value={form.book} onChange={(e) => setForm({ ...form, book: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="txn-member">Member ID</Label>
                  <Input id="txn-member" value={form.member} onChange={(e) => setForm({ ...form, member: e.target.value })} />
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="txn-due">Due Date</Label>
                <Input id="txn-due" type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button onClick={() => createMutation.mutate(form)} disabled={createMutation.isPending}>
                {createMutation.isPending ? 'Issuing…' : 'Issue'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
      <DataTable
        data={(data?.results ?? []) as Transaction[]}
        columns={transactionColumns}
        searchPlaceholder="Search transactions…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No transactions found."
      />
    </>
  )
}

// ─── Memberships Tab ─────────────────────────
const memberTypeBadge: Record<string, 'secondary' | 'success' | 'warning'> = {
  student: 'success',
  teacher: 'warning',
  staff: 'secondary',
}

const membershipColumns: Column<Membership>[] = [
  { key: 'user_name', header: 'Name', sortable: true },
  { key: 'membership_number', header: 'Membership #' },
  {
    key: 'membership_type',
    header: 'Type',
    render: (m) => (
      <Badge variant={memberTypeBadge[m.membership_type] ?? 'secondary'}>
        {m.membership_type}
      </Badge>
    ),
  },
  { key: 'max_books', header: 'Max Books' },
  {
    key: 'is_active',
    header: 'Status',
    render: (m) => (
      <Badge variant={m.is_active ? 'success' : 'secondary'}>
        {m.is_active ? 'Active' : 'Inactive'}
      </Badge>
    ),
  },
]

function MembershipsTab() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['memberships', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Membership>>('/library/memberships/', { params })
      return data
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <DataTable
      data={(data?.results ?? []) as Membership[]}
      columns={membershipColumns}
      searchPlaceholder="Search memberships…"
      onSearch={(q) => { setSearch(q); setPage(1) }}
      isLoading={isLoading}
      pagination={{ page, totalPages, onPageChange: setPage }}
      emptyMessage="No memberships found."
    />
  )
}

// ─── Main Page ───────────────────────────────
export default function LibraryPage() {
  return (
    <div>
      <PageHeader title="Library" description="Manage books, transactions, and memberships" />
      <Tabs defaultValue="books">
        <TabsList>
          <TabsTrigger value="books">Books</TabsTrigger>
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
          <TabsTrigger value="memberships">Memberships</TabsTrigger>
        </TabsList>
        <TabsContent value="books"><BooksTab /></TabsContent>
        <TabsContent value="transactions"><TransactionsTab /></TabsContent>
        <TabsContent value="memberships"><MembershipsTab /></TabsContent>
      </Tabs>
    </div>
  )
}
