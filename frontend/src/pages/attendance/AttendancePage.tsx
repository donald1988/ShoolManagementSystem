import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { CheckCircle, XCircle } from 'lucide-react'
import api from '@/lib/api'
import type { PaginatedResponse, StudentAttendance, Class, Section } from '@/types'
import { PageHeader } from '@/components/layout/PageHeader'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loading } from '@/components/ui/loading'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const statusColors: Record<string, 'success' | 'destructive' | 'warning' | 'secondary'> = {
  present: 'success',
  absent: 'destructive',
  late: 'warning',
  excused: 'secondary',
  half_day: 'warning',
}

const statusOptions = ['present', 'absent', 'late', 'excused', 'half_day'] as const

export default function AttendancePage() {
  const queryClient = useQueryClient()
  const today = new Date().toISOString().split('T')[0]
  const [date, setDate] = useState(today)
  const [classId, setClassId] = useState('')
  const [sectionId, setSectionId] = useState('')
  const [localStatuses, setLocalStatuses] = useState<Record<string, string>>({})

  const { data: classes } = useQuery({
    queryKey: ['classes-list'],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<Class>>('/academics/classes/', { params: { page_size: 100 } })
      return data.results
    },
  })

  const selectedClass = useMemo(() => classes?.find((c) => c.id === classId), [classes, classId])

  const { data: sections } = useQuery({
    queryKey: ['sections-list', classId],
    queryFn: async () => {
      if (!classId) return []
      return selectedClass?.sections ?? []
    },
    enabled: !!classId,
  })

  const { data: attendance, isLoading } = useQuery({
    queryKey: ['attendance', date, classId, sectionId],
    queryFn: async () => {
      const params: Record<string, string> = { date }
      if (classId) params.class_obj = classId
      if (sectionId) params.section = sectionId
      const { data } = await api.get<PaginatedResponse<StudentAttendance>>('/attendance/student/', { params: { ...params, page_size: 200 } })
      return data.results
    },
    enabled: !!date && !!classId,
  })

  const bulkMarkMutation = useMutation({
    mutationFn: (payload: { date: string; class_obj: string; section?: string; records: { student: string; status: string }[] }) =>
      api.post('/attendance/student/bulk_mark/', payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['attendance'] })
      setLocalStatuses({})
    },
  })

  const handleStatusChange = (studentId: string, status: string) => {
    setLocalStatuses((prev) => ({ ...prev, [studentId]: status }))
  }

  const handleBulkMark = (status: string) => {
    if (!attendance) return
    const records = attendance.map((a) => ({ student: a.student, status }))
    bulkMarkMutation.mutate({ date, class_obj: classId, ...(sectionId && { section: sectionId }), records })
  }

  const handleSave = () => {
    if (!attendance) return
    const records = attendance.map((a) => ({
      student: a.student,
      status: localStatuses[a.student] ?? a.status,
    }))
    bulkMarkMutation.mutate({ date, class_obj: classId, ...(sectionId && { section: sectionId }), records })
  }

  const getStatus = (a: StudentAttendance) => localStatuses[a.student] ?? a.status

  return (
    <div>
      <PageHeader title="Attendance" description="Mark and manage student attendance" />

      {/* Filters */}
      <div className="mb-6 flex flex-wrap items-end gap-4">
        <div className="grid gap-2">
          <Label>Date</Label>
          <Input type="date" value={date} onChange={(e) => setDate(e.target.value)} className="w-44" />
        </div>
        <div className="grid gap-2">
          <Label>Class</Label>
          <Select value={classId} onValueChange={(v) => { setClassId(v); setSectionId('') }}>
            <SelectTrigger className="w-44"><SelectValue placeholder="Select class" /></SelectTrigger>
            <SelectContent>
              {classes?.map((c) => (
                <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-2">
          <Label>Section</Label>
          <Select value={sectionId} onValueChange={setSectionId}>
            <SelectTrigger className="w-44"><SelectValue placeholder="All sections" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="">All</SelectItem>
              {sections?.map((s) => (
                <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => handleBulkMark('present')}>
            <CheckCircle className="mr-2 h-4 w-4" />Mark All Present
          </Button>
          <Button variant="outline" onClick={() => handleBulkMark('absent')}>
            <XCircle className="mr-2 h-4 w-4" />Mark All Absent
          </Button>
        </div>
      </div>

      {/* Table */}
      {!classId ? (
        <p className="text-center text-muted-foreground py-12">Select a class to view attendance.</p>
      ) : isLoading ? (
        <Loading className="h-64" />
      ) : (
        <>
          <div className="rounded-md border">
            <div className="overflow-x-auto">
              <table className="w-full caption-bottom text-sm">
                <thead className="[&_tr]:border-b">
                  <tr className="border-b transition-colors hover:bg-muted/50">
                    <th className="h-10 px-4 text-left font-medium text-muted-foreground">Student ID</th>
                    <th className="h-10 px-4 text-left font-medium text-muted-foreground">Student Name</th>
                    <th className="h-10 px-4 text-left font-medium text-muted-foreground">Status</th>
                    <th className="h-10 px-4 text-left font-medium text-muted-foreground">Change</th>
                  </tr>
                </thead>
                <tbody className="[&_tr:last-child]:border-0">
                  {attendance && attendance.length > 0 ? (
                    attendance.map((a) => (
                      <tr key={a.id} className="border-b transition-colors hover:bg-muted/50">
                        <td className="px-4 py-2">{a.student_id}</td>
                        <td className="px-4 py-2">{a.student_name}</td>
                        <td className="px-4 py-2">
                          <Badge variant={statusColors[getStatus(a)] ?? 'secondary'}>
                            {getStatus(a)}
                          </Badge>
                        </td>
                        <td className="px-4 py-2">
                          <Select value={getStatus(a)} onValueChange={(v) => handleStatusChange(a.student, v)}>
                            <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
                            <SelectContent>
                              {statusOptions.map((s) => (
                                <SelectItem key={s} value={s}>{s}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} className="h-24 text-center text-muted-foreground">
                        No attendance records found for the selected filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
          {attendance && attendance.length > 0 && Object.keys(localStatuses).length > 0 && (
            <div className="mt-4 flex justify-end">
              <Button onClick={handleSave} disabled={bulkMarkMutation.isPending}>
                {bulkMarkMutation.isPending ? 'Saving…' : 'Save Changes'}
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
