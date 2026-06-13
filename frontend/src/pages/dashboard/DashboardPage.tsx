import {
  BarChart3,
  BookOpen,
  CreditCard,
  GraduationCap,
  School,
  UserCheck,
  Users,
  Wallet,
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { PageHeader } from '@/components/layout/PageHeader'
import { StatsCard, StatsGrid } from '@/components/layout/StatsCard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function DashboardPage() {
  const { user } = useAuth()

  if (user?.role === 'super_admin') return <SuperAdminDashboard />
  if (user?.role === 'school_admin' || user?.role === 'principal') return <AdminDashboard />
  if (user?.role === 'teacher') return <TeacherDashboard />
  if (user?.role === 'student') return <StudentDashboard />
  if (user?.role === 'parent') return <ParentDashboard />
  return <DefaultDashboard role={user?.role || 'staff'} />
}

function SuperAdminDashboard() {
  return (
    <div>
      <PageHeader title="Super Admin Dashboard" description="System-wide overview" />
      <StatsGrid>
        <StatsCard title="Total Schools" value="12" icon={School} trend={{ value: 8.5, label: 'vs last month' }} />
        <StatsCard title="Total Students" value="4,523" icon={GraduationCap} trend={{ value: 12, label: 'vs last year' }} />
        <StatsCard title="Total Staff" value="856" icon={Users} />
        <StatsCard title="Revenue" value="$1.2M" icon={CreditCard} trend={{ value: 15, label: 'vs last month' }} />
      </StatsGrid>
      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <RecentActivityCard />
        <QuickActionsCard />
      </div>
    </div>
  )
}

function AdminDashboard() {
  return (
    <div>
      <PageHeader title="School Dashboard" description="Today's overview" />
      <StatsGrid>
        <StatsCard title="Students" value="1,234" icon={GraduationCap} trend={{ value: 5, label: 'new this term' }} />
        <StatsCard title="Teachers" value="89" icon={Users} />
        <StatsCard title="Attendance Today" value="92.5%" icon={UserCheck} trend={{ value: 2.3, label: 'vs yesterday' }} />
        <StatsCard title="Pending Fees" value="$45,200" icon={Wallet} />
      </StatsGrid>
      <div className="mt-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <RecentActivityCard />
        <UpcomingEventsCard />
        <QuickActionsCard />
      </div>
    </div>
  )
}

function TeacherDashboard() {
  return (
    <div>
      <PageHeader title="Teacher Dashboard" description="Your classes and tasks" />
      <StatsGrid>
        <StatsCard title="My Classes" value="5" icon={BookOpen} />
        <StatsCard title="Total Students" value="156" icon={GraduationCap} />
        <StatsCard title="Pending Assignments" value="8" icon={BarChart3} />
        <StatsCard title="Today's Periods" value="6" icon={UserCheck} />
      </StatsGrid>
      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <TodayScheduleCard />
        <RecentActivityCard />
      </div>
    </div>
  )
}

function StudentDashboard() {
  return (
    <div>
      <PageHeader title="Student Dashboard" description="Your academic overview" />
      <StatsGrid>
        <StatsCard title="GPA" value="3.75" icon={BarChart3} trend={{ value: 0.15, label: 'vs last term' }} />
        <StatsCard title="Attendance" value="95.2%" icon={UserCheck} />
        <StatsCard title="Assignments Due" value="3" icon={BookOpen} />
        <StatsCard title="Fee Balance" value="$250" icon={CreditCard} />
      </StatsGrid>
      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <TodayScheduleCard />
        <RecentActivityCard />
      </div>
    </div>
  )
}

function ParentDashboard() {
  return (
    <div>
      <PageHeader title="Parent Dashboard" description="Monitor your children's progress" />
      <StatsGrid>
        <StatsCard title="Children" value="2" icon={GraduationCap} />
        <StatsCard title="Avg. Attendance" value="94.8%" icon={UserCheck} />
        <StatsCard title="Avg. GPA" value="3.6" icon={BarChart3} />
        <StatsCard title="Pending Fees" value="$500" icon={CreditCard} />
      </StatsGrid>
      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <RecentActivityCard />
        <QuickActionsCard />
      </div>
    </div>
  )
}

function DefaultDashboard({ role }: { role: string }) {
  return (
    <div>
      <PageHeader title="Dashboard" description={`Welcome, ${role.replace('_', ' ')}`} />
      <StatsGrid>
        <StatsCard title="Tasks" value="5" icon={BookOpen} />
        <StatsCard title="Messages" value="3" icon={Users} />
        <StatsCard title="Notifications" value="7" icon={BarChart3} />
        <StatsCard title="Calendar" value="2 events" icon={UserCheck} />
      </StatsGrid>
    </div>
  )
}

function RecentActivityCard() {
  const activities = [
    { text: 'New student enrolled: John Smith', time: '2 min ago', type: 'success' as const },
    { text: 'Fee payment received: $500', time: '15 min ago', type: 'default' as const },
    { text: 'Exam schedule published for Term 2', time: '1 hour ago', type: 'secondary' as const },
    { text: 'Leave request from Sarah Wilson', time: '2 hours ago', type: 'warning' as const },
    { text: 'Attendance marked for Class 10-A', time: '3 hours ago', type: 'default' as const },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {activities.map((activity, i) => (
            <div key={i} className="flex items-start justify-between gap-2">
              <p className="text-sm">{activity.text}</p>
              <Badge variant={activity.type} className="shrink-0 text-xs">
                {activity.time}
              </Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function UpcomingEventsCard() {
  const events = [
    { title: 'Parent-Teacher Meeting', date: 'Jun 15, 2026' },
    { title: 'Mid-Term Exams Begin', date: 'Jun 20, 2026' },
    { title: 'Sports Day', date: 'Jul 1, 2026' },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Upcoming Events</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {events.map((event, i) => (
            <div key={i} className="flex items-center justify-between">
              <p className="text-sm font-medium">{event.title}</p>
              <p className="text-xs text-muted-foreground">{event.date}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function TodayScheduleCard() {
  const periods = [
    { time: '8:00 - 8:45', subject: 'Mathematics', class: '10-A', room: 'Room 201' },
    { time: '8:50 - 9:35', subject: 'Physics', class: '10-B', room: 'Lab 3' },
    { time: '9:40 - 10:25', subject: 'Chemistry', class: '11-A', room: 'Lab 1' },
    { time: '10:45 - 11:30', subject: 'Mathematics', class: '9-C', room: 'Room 105' },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Today's Schedule</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {periods.map((period, i) => (
            <div key={i} className="flex items-center gap-4 rounded-lg border p-3">
              <div className="text-xs font-medium text-muted-foreground w-24">{period.time}</div>
              <div className="flex-1">
                <p className="text-sm font-medium">{period.subject}</p>
                <p className="text-xs text-muted-foreground">{period.class} · {period.room}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function QuickActionsCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-2">
          {[
            'Mark Attendance',
            'Add Student',
            'Create Invoice',
            'Send Message',
            'View Reports',
            'Manage Timetable',
          ].map((action) => (
            <button
              key={action}
              className="rounded-lg border p-3 text-center text-sm font-medium text-foreground hover:bg-accent transition-colors"
            >
              {action}
            </button>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
