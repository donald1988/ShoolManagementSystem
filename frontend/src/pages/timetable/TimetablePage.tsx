import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import api from '@/lib/api'
import type { PaginatedResponse, TimetableEntry, Class } from '@/types'
import { PageHeader } from '@/components/layout/PageHeader'
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

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'] as const

export default function TimetablePage() {
  const queryClient = useQueryClient()
  const [classId, setClassId] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState({
    class_obj: '',
    subject: '',
    teacher: '',
    room: '',
    period: '',
    day_of_week: 'Monday',
  })

  const { data: classes } = useQuery({
    queryKey: ['classes-list'],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<Class>>('/academics/classes/', { params: { page_size: 100 } })
      return data.results
    },
  })

  const { data: entries, isLoading } = useQuery({
    queryKey: ['timetable-entries', classId],
    queryFn: async () => {
      const params: Record<string, string> = { page_size: '200' }
      if (classId) params.class_obj = classId
      const { data } = await api.get<PaginatedResponse<TimetableEntry>>('/timetable/entries/', { params })
      return data.results
    },
    enabled: !!classId,
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => api.post('/timetable/entries/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['timetable-entries'] })
      setDialogOpen(false)
      setForm({ class_obj: '', subject: '', teacher: '', room: '', period: '', day_of_week: 'Monday' })
    },
  })

  // Build grid: rows = unique periods, columns = days
  const { periods, grid } = useMemo(() => {
    if (!entries) return { periods: [] as string[], grid: {} as Record<string, Record<string, TimetableEntry[]>> }
    const periodSet = new Set<string>()
    const g: Record<string, Record<string, TimetableEntry[]>> = {}
    for (const entry of entries) {
      periodSet.add(entry.period)
      if (!g[entry.period]) g[entry.period] = {}
      if (!g[entry.period][entry.day_of_week]) g[entry.period][entry.day_of_week] = []
      g[entry.period][entry.day_of_week].push(entry)
    }
    const sortedPeriods = Array.from(periodSet).sort()
    return { periods: sortedPeriods, grid: g }
  }, [entries])

  return (
    <div>
      <PageHeader title="Timetable" description="View and manage weekly timetable">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Add Entry</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add Timetable Entry</DialogTitle></DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="tt-class">Class ID</Label>
                  <Input id="tt-class" value={form.class_obj} onChange={(e) => setForm({ ...form, class_obj: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="tt-subject">Subject ID</Label>
                  <Input id="tt-subject" value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="tt-teacher">Teacher ID</Label>
                  <Input id="tt-teacher" value={form.teacher} onChange={(e) => setForm({ ...form, teacher: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="tt-room">Room</Label>
                  <Input id="tt-room" value={form.room} onChange={(e) => setForm({ ...form, room: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="tt-period">Period</Label>
                  <Input id="tt-period" value={form.period} onChange={(e) => setForm({ ...form, period: e.target.value })} placeholder="e.g. Period 1" />
                </div>
                <div className="grid gap-2">
                  <Label>Day</Label>
                  <Select value={form.day_of_week} onValueChange={(v) => setForm({ ...form, day_of_week: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {DAYS.map((d) => (
                        <SelectItem key={d} value={d}>{d}</SelectItem>
                      ))}
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
      </PageHeader>

      {/* Class filter */}
      <div className="mb-6 flex items-end gap-4">
        <div className="grid gap-2">
          <Label>Class</Label>
          <Select value={classId} onValueChange={setClassId}>
            <SelectTrigger className="w-52"><SelectValue placeholder="Select class" /></SelectTrigger>
            <SelectContent>
              {classes?.map((c) => (
                <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Timetable grid */}
      {!classId ? (
        <p className="text-center text-muted-foreground py-12">Select a class to view the timetable.</p>
      ) : isLoading ? (
        <Loading className="h-64" />
      ) : periods.length === 0 ? (
        <p className="text-center text-muted-foreground py-12">No timetable entries found for this class.</p>
      ) : (
        <div className="rounded-md border overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="[&_tr]:border-b">
              <tr className="border-b bg-muted/50">
                <th className="h-10 px-4 text-left font-medium text-muted-foreground">Period</th>
                {DAYS.map((day) => (
                  <th key={day} className="h-10 px-4 text-left font-medium text-muted-foreground">{day}</th>
                ))}
              </tr>
            </thead>
            <tbody className="[&_tr:last-child]:border-0">
              {periods.map((period) => (
                <tr key={period} className="border-b transition-colors hover:bg-muted/50">
                  <td className="px-4 py-3 font-medium">{period}</td>
                  {DAYS.map((day) => {
                    const cellEntries = grid[period]?.[day] ?? []
                    return (
                      <td key={day} className="px-4 py-3">
                        {cellEntries.length > 0 ? (
                          cellEntries.map((entry) => (
                            <div key={entry.id} className="mb-1 last:mb-0">
                              <Badge variant="secondary" className="mr-1">{entry.subject_name}</Badge>
                              <span className="text-xs text-muted-foreground">
                                {entry.teacher_name}
                                {entry.room && ` · ${entry.room}`}
                              </span>
                            </div>
                          ))
                        ) : (
                          <span className="text-xs text-muted-foreground">—</span>
                        )}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
