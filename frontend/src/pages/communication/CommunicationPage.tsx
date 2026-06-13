import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Mail, Pin, Bell, Check } from 'lucide-react'
import api from '@/lib/api'
import { formatDate, truncate, cn } from '@/lib/utils'
import type { PaginatedResponse, Message, Announcement, Notification } from '@/types'
import { PageHeader } from '@/components/layout/PageHeader'
import { DataTable, type Column } from '@/components/ui/data-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loading } from '@/components/ui/loading'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
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

// ─── Messages Tab (Inbox View) ───────────────
function MessagesTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ recipient: '', subject: '', body: '' })

  const { data, isLoading } = useQuery({
    queryKey: ['messages', page],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      const { data } = await api.get<PaginatedResponse<Message>>('/communication/messages/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/communication/messages/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['messages'] })
      setDialogOpen(false)
      setForm({ recipient: '', subject: '', body: '' })
    },
  })

  const markReadMutation = useMutation({
    mutationFn: (id: string) => api.patch(`/communication/messages/${id}/`, { is_read: true }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['messages'] }),
  })

  if (isLoading) return <Loading className="h-64" />
  const messages = data?.results ?? []
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" /><Mail className="mr-1 h-4 w-4" />Compose</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader><DialogTitle>Compose Message</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="msg-to">Recipient ID</Label>
                <Input id="msg-to" value={form.recipient} onChange={(e) => setForm({ ...form, recipient: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="msg-subject">Subject</Label>
                <Input id="msg-subject" value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="msg-body">Body</Label>
                <Textarea id="msg-body" rows={6} value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button onClick={() => createMutation.mutate(form)} disabled={createMutation.isPending}>
                {createMutation.isPending ? 'Sending…' : 'Send'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid min-h-[500px] gap-4 md:grid-cols-[360px_1fr]">
        {/* Message list */}
        <Card className="overflow-hidden">
          <div className="divide-y overflow-y-auto" style={{ maxHeight: 500 }}>
            {messages.length === 0 ? (
              <p className="p-6 text-center text-sm text-muted-foreground">No messages.</p>
            ) : (
              messages.map((msg) => (
                <button
                  key={msg.id}
                  onClick={() => {
                    setSelectedMessage(msg)
                    if (!msg.is_read) markReadMutation.mutate(msg.id)
                  }}
                  className={cn(
                    'w-full px-4 py-3 text-left transition-colors hover:bg-muted/50',
                    selectedMessage?.id === msg.id && 'bg-muted',
                    !msg.is_read && 'font-semibold',
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm">{msg.sender}</span>
                    <span className="text-xs text-muted-foreground">{formatDate(msg.created_at)}</span>
                  </div>
                  <p className="mt-0.5 text-sm">{msg.subject}</p>
                  <p className="mt-0.5 text-xs text-muted-foreground">{truncate(msg.body, 80)}</p>
                </button>
              ))
            )}
          </div>
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 border-t p-2">
              <Button variant="ghost" size="sm" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>Prev</Button>
              <span className="text-xs text-muted-foreground">{page}/{totalPages}</span>
              <Button variant="ghost" size="sm" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next</Button>
            </div>
          )}
        </Card>

        {/* Message detail */}
        <Card>
          <CardContent className="p-6">
            {selectedMessage ? (
              <>
                <h2 className="text-lg font-semibold">{selectedMessage.subject}</h2>
                <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
                  <span>From: {selectedMessage.sender}</span>
                  <span>·</span>
                  <span>{formatDate(selectedMessage.created_at)}</span>
                </div>
                <div className="mt-4 whitespace-pre-wrap text-sm">{selectedMessage.body}</div>
              </>
            ) : (
              <p className="py-12 text-center text-muted-foreground">Select a message to read</p>
            )}
          </CardContent>
        </Card>
      </div>
    </>
  )
}

// ─── Announcements Tab ───────────────────────
const audienceBadge: Record<string, 'secondary' | 'success' | 'warning' | 'destructive'> = {
  all: 'secondary',
  students: 'success',
  teachers: 'warning',
  parents: 'destructive',
  staff: 'secondary',
}

const announcementColumns: Column<Announcement>[] = [
  { key: 'title', header: 'Title', sortable: true },
  {
    key: 'target_audience',
    header: 'Audience',
    render: (a) => (
      <Badge variant={audienceBadge[a.target_audience] ?? 'secondary'}>
        {a.target_audience}
      </Badge>
    ),
  },
  {
    key: 'is_pinned',
    header: 'Pinned',
    render: (a) =>
      a.is_pinned ? (
        <Badge variant="warning"><Pin className="mr-1 h-3 w-3" />Pinned</Badge>
      ) : (
        <span className="text-muted-foreground">—</span>
      ),
  },
  { key: 'created_at', header: 'Created', sortable: true, render: (a) => <>{formatDate(a.created_at)}</> },
]

function AnnouncementsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({ title: '', content: '', target_audience: 'all', is_pinned: false })

  const { data, isLoading } = useQuery({
    queryKey: ['announcements', page, search],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      if (search) params.search = search
      const { data } = await api.get<PaginatedResponse<Announcement>>('/communication/announcements/', { params })
      return data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/communication/announcements/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['announcements'] })
      setDialogOpen(false)
      setForm({ title: '', content: '', target_audience: 'all', is_pinned: false })
    },
  })

  if (isLoading) return <Loading className="h-64" />
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Announcement</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>New Announcement</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="ann-title">Title</Label>
                <Input id="ann-title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="ann-content">Content</Label>
                <Textarea id="ann-content" rows={4} value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="ann-audience">Target Audience</Label>
                  <Select value={form.target_audience} onValueChange={(v) => setForm({ ...form, target_audience: v })}>
                    <SelectTrigger id="ann-audience"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All</SelectItem>
                      <SelectItem value="students">Students</SelectItem>
                      <SelectItem value="teachers">Teachers</SelectItem>
                      <SelectItem value="parents">Parents</SelectItem>
                      <SelectItem value="staff">Staff</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-end gap-2 pb-1">
                  <input
                    id="ann-pinned"
                    type="checkbox"
                    checked={form.is_pinned}
                    onChange={(e) => setForm({ ...form, is_pinned: e.target.checked })}
                    className="h-4 w-4 rounded border-gray-300"
                  />
                  <Label htmlFor="ann-pinned">Pin announcement</Label>
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
        data={(data?.results ?? []) as (Announcement & Record<string, unknown>)[]}
        columns={announcementColumns}
        searchPlaceholder="Search announcements…"
        onSearch={(q) => { setSearch(q); setPage(1) }}
        isLoading={isLoading}
        pagination={{ page, totalPages, onPageChange: setPage }}
        emptyMessage="No announcements found."
      />
    </>
  )
}

// ─── Notifications Tab ───────────────────────
const notificationTypeBadge: Record<string, 'secondary' | 'success' | 'warning' | 'destructive'> = {
  info: 'secondary',
  success: 'success',
  warning: 'warning',
  error: 'destructive',
  alert: 'destructive',
}

function NotificationsTab() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['notifications', page],
    queryFn: async () => {
      const params: Record<string, string | number> = { page, page_size: 20 }
      const { data } = await api.get<PaginatedResponse<Notification>>('/communication/notifications/', { params })
      return data
    },
  })

  const markReadMutation = useMutation({
    mutationFn: (id: string) => api.patch(`/communication/notifications/${id}/`, { is_read: true }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  })

  if (isLoading) return <Loading className="h-64" />
  const notifications = data?.results ?? []
  const totalPages = data ? Math.ceil(data.count / 20) : 1

  return (
    <div className="space-y-2">
      {notifications.length === 0 ? (
        <p className="py-12 text-center text-muted-foreground">No notifications.</p>
      ) : (
        notifications.map((n) => (
          <Card key={n.id} className={cn(!n.is_read && 'border-primary/30 bg-primary/5')}>
            <CardContent className="flex items-start gap-3 p-4">
              <Bell className={cn('mt-0.5 h-4 w-4 shrink-0', n.is_read ? 'text-muted-foreground' : 'text-primary')} />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className={cn('text-sm', !n.is_read && 'font-semibold')}>{n.title}</span>
                  <Badge variant={notificationTypeBadge[n.notification_type] ?? 'secondary'} className="text-[10px]">
                    {n.notification_type}
                  </Badge>
                </div>
                <p className="mt-0.5 text-sm text-muted-foreground">{n.message}</p>
                <span className="mt-1 text-xs text-muted-foreground">{formatDate(n.created_at)}</span>
              </div>
              {!n.is_read && (
                <Button size="sm" variant="ghost" onClick={() => markReadMutation.mutate(n.id)} disabled={markReadMutation.isPending}>
                  <Check className="mr-1 h-3 w-3" />Read
                </Button>
              )}
            </CardContent>
          </Card>
        ))
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-4">
          <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>Previous</Button>
          <span className="text-sm text-muted-foreground">Page {page} of {totalPages}</span>
          <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next</Button>
        </div>
      )}
    </div>
  )
}

// ─── Main Page ───────────────────────────────
export default function CommunicationPage() {
  return (
    <div>
      <PageHeader title="Communication" description="Messages, announcements, and notifications" />
      <Tabs defaultValue="messages">
        <TabsList>
          <TabsTrigger value="messages">Messages</TabsTrigger>
          <TabsTrigger value="announcements">Announcements</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
        </TabsList>
        <TabsContent value="messages"><MessagesTab /></TabsContent>
        <TabsContent value="announcements"><AnnouncementsTab /></TabsContent>
        <TabsContent value="notifications"><NotificationsTab /></TabsContent>
      </Tabs>
    </div>
  )
}
