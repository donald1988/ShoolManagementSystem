import { Link, useLocation } from 'react-router-dom'
import {
  BarChart3,
  BookOpen,
  Building2,
  Bus,
  Calendar,
  ChevronLeft,
  ClipboardCheck,
  CreditCard,
  FileText,
  GraduationCap,
  Heart,
  Home,
  Hotel,
  Library,
  MessageSquare,
  Package,
  School,
  Shield,
  UserCheck,
  Users,
  Wallet,
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { cn } from '@/lib/utils'
import type { UserRole } from '@/types'

interface SidebarProps {
  open: boolean
  onToggle: () => void
}

interface NavItem {
  title: string
  href: string
  icon: React.ElementType
  roles: UserRole[]
}

const navItems: NavItem[] = [
  { title: 'Dashboard', href: '/dashboard', icon: Home, roles: ['super_admin', 'school_admin', 'principal', 'teacher', 'student', 'parent', 'accountant', 'librarian', 'hr', 'transport_manager', 'nurse', 'staff'] },
  { title: 'Schools', href: '/dashboard/schools', icon: School, roles: ['super_admin'] },
  { title: 'Students', href: '/dashboard/students', icon: GraduationCap, roles: ['super_admin', 'school_admin', 'principal', 'teacher'] },
  { title: 'Admissions', href: '/dashboard/admissions', icon: UserCheck, roles: ['super_admin', 'school_admin', 'principal'] },
  { title: 'Academics', href: '/dashboard/academics', icon: BookOpen, roles: ['super_admin', 'school_admin', 'principal', 'teacher'] },
  { title: 'Attendance', href: '/dashboard/attendance', icon: ClipboardCheck, roles: ['super_admin', 'school_admin', 'principal', 'teacher'] },
  { title: 'Examinations', href: '/dashboard/examinations', icon: FileText, roles: ['super_admin', 'school_admin', 'principal', 'teacher', 'student', 'parent'] },
  { title: 'LMS', href: '/dashboard/lms', icon: BookOpen, roles: ['super_admin', 'school_admin', 'principal', 'teacher', 'student'] },
  { title: 'Finance', href: '/dashboard/finance', icon: CreditCard, roles: ['super_admin', 'school_admin', 'accountant'] },
  { title: 'Payroll', href: '/dashboard/payroll', icon: Wallet, roles: ['super_admin', 'school_admin', 'accountant', 'hr'] },
  { title: 'HR', href: '/dashboard/hr', icon: Users, roles: ['super_admin', 'school_admin', 'hr'] },
  { title: 'Communication', href: '/dashboard/communication', icon: MessageSquare, roles: ['super_admin', 'school_admin', 'principal', 'teacher', 'student', 'parent'] },
  { title: 'Timetable', href: '/dashboard/timetable', icon: Calendar, roles: ['super_admin', 'school_admin', 'principal', 'teacher', 'student'] },
  { title: 'Library', href: '/dashboard/library', icon: Library, roles: ['super_admin', 'school_admin', 'librarian', 'teacher', 'student'] },
  { title: 'Transport', href: '/dashboard/transport', icon: Bus, roles: ['super_admin', 'school_admin', 'transport_manager'] },
  { title: 'Hostel', href: '/dashboard/hostel', icon: Hotel, roles: ['super_admin', 'school_admin'] },
  { title: 'Inventory', href: '/dashboard/inventory', icon: Package, roles: ['super_admin', 'school_admin'] },
  { title: 'Health', href: '/dashboard/health', icon: Heart, roles: ['super_admin', 'school_admin', 'nurse', 'teacher'] },
  { title: 'Discipline', href: '/dashboard/discipline', icon: Shield, roles: ['super_admin', 'school_admin', 'principal', 'teacher'] },
  { title: 'Analytics', href: '/dashboard/analytics', icon: BarChart3, roles: ['super_admin', 'school_admin', 'principal'] },
  { title: 'Campuses', href: '/dashboard/campuses', icon: Building2, roles: ['super_admin', 'school_admin'] },
]

export function Sidebar({ open, onToggle }: SidebarProps) {
  const location = useLocation()
  const { user } = useAuth()

  const filteredItems = navItems.filter(
    (item) => user && item.roles.includes(user.role)
  )

  return (
    <aside
      className={cn(
        'flex flex-col border-r bg-sidebar transition-all duration-300',
        open ? 'w-64' : 'w-16',
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center justify-between border-b px-4">
        {open && (
          <Link to="/dashboard" className="flex items-center gap-2">
            <GraduationCap className="h-7 w-7 text-primary" />
            <span className="text-lg font-bold text-foreground">SMS</span>
          </Link>
        )}
        <button
          onClick={onToggle}
          className="hidden rounded-md p-1.5 text-muted-foreground hover:bg-sidebar-accent md:block"
        >
          <ChevronLeft className={cn('h-5 w-5 transition-transform', !open && 'rotate-180')} />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-2 py-4">
        <ul className="space-y-1">
          {filteredItems.map((item) => {
            const isActive =
              item.href === '/dashboard'
                ? location.pathname === '/dashboard'
                : location.pathname.startsWith(item.href)
            return (
              <li key={item.href}>
                <Link
                  to={item.href}
                  className={cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-sidebar-foreground hover:bg-sidebar-accent',
                    !open && 'justify-center px-2',
                  )}
                  title={!open ? item.title : undefined}
                >
                  <item.icon className="h-5 w-5 shrink-0" />
                  {open && <span>{item.title}</span>}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Footer */}
      {open && (
        <div className="border-t px-4 py-3">
          <p className="text-xs text-muted-foreground">School Management System</p>
          <p className="text-xs text-muted-foreground">v1.0.0</p>
        </div>
      )}
    </aside>
  )
}
