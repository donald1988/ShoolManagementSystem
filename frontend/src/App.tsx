import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { Loading } from '@/components/ui/loading'

// Lazy-load all pages
const LoginPage = lazy(() => import('@/pages/auth/LoginPage'))
const ProfilePage = lazy(() => import('@/pages/auth/ProfilePage'))
const DashboardPage = lazy(() => import('@/pages/dashboard/DashboardPage'))
const SchoolsPage = lazy(() => import('@/pages/schools/SchoolsPage'))
const CampusesPage = lazy(() => import('@/pages/campuses/CampusesPage'))
const StudentsPage = lazy(() => import('@/pages/students/StudentsPage'))
const ParentsPage = lazy(() => import('@/pages/students/ParentsPage'))
const AdmissionsPage = lazy(() => import('@/pages/admissions/AdmissionsPage'))
const AcademicsPage = lazy(() => import('@/pages/academics/AcademicsPage'))
const AttendancePage = lazy(() => import('@/pages/attendance/AttendancePage'))
const ExaminationsPage = lazy(() => import('@/pages/examinations/ExaminationsPage'))
const LmsPage = lazy(() => import('@/pages/lms/LmsPage'))
const FinancePage = lazy(() => import('@/pages/finance/FinancePage'))
const PayrollPage = lazy(() => import('@/pages/payroll/PayrollPage'))
const HrPage = lazy(() => import('@/pages/hr/HrPage'))
const CommunicationPage = lazy(() => import('@/pages/communication/CommunicationPage'))
const TimetablePage = lazy(() => import('@/pages/timetable/TimetablePage'))
const LibraryPage = lazy(() => import('@/pages/library/LibraryPage'))
const TransportPage = lazy(() => import('@/pages/transport/TransportPage'))
const HostelPage = lazy(() => import('@/pages/hostel/HostelPage'))
const InventoryPage = lazy(() => import('@/pages/inventory/InventoryPage'))
const HealthPage = lazy(() => import('@/pages/health/HealthPage'))
const DisciplinePage = lazy(() => import('@/pages/discipline/DisciplinePage'))
const AnalyticsPage = lazy(() => import('@/pages/analytics/AnalyticsPage'))

function SuspenseWrapper({ children }: { children: React.ReactNode }) {
  return (
    <Suspense
      fallback={
        <div className="flex h-64 items-center justify-center">
          <Loading size="lg" />
        </div>
      }
    >
      {children}
    </Suspense>
  )
}

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route
        path="/login"
        element={
          <SuspenseWrapper>
            <LoginPage />
          </SuspenseWrapper>
        }
      />

      {/* Protected dashboard routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<SuspenseWrapper><DashboardPage /></SuspenseWrapper>} />
        <Route path="profile" element={<SuspenseWrapper><ProfilePage /></SuspenseWrapper>} />
        <Route path="schools" element={<SuspenseWrapper><SchoolsPage /></SuspenseWrapper>} />
        <Route path="campuses" element={<SuspenseWrapper><CampusesPage /></SuspenseWrapper>} />
        <Route path="students" element={<SuspenseWrapper><StudentsPage /></SuspenseWrapper>} />
        <Route path="parents" element={<SuspenseWrapper><ParentsPage /></SuspenseWrapper>} />
        <Route path="admissions" element={<SuspenseWrapper><AdmissionsPage /></SuspenseWrapper>} />
        <Route path="academics" element={<SuspenseWrapper><AcademicsPage /></SuspenseWrapper>} />
        <Route path="attendance" element={<SuspenseWrapper><AttendancePage /></SuspenseWrapper>} />
        <Route path="examinations" element={<SuspenseWrapper><ExaminationsPage /></SuspenseWrapper>} />
        <Route path="lms" element={<SuspenseWrapper><LmsPage /></SuspenseWrapper>} />
        <Route path="finance" element={<SuspenseWrapper><FinancePage /></SuspenseWrapper>} />
        <Route path="payroll" element={<SuspenseWrapper><PayrollPage /></SuspenseWrapper>} />
        <Route path="hr" element={<SuspenseWrapper><HrPage /></SuspenseWrapper>} />
        <Route path="communication" element={<SuspenseWrapper><CommunicationPage /></SuspenseWrapper>} />
        <Route path="timetable" element={<SuspenseWrapper><TimetablePage /></SuspenseWrapper>} />
        <Route path="library" element={<SuspenseWrapper><LibraryPage /></SuspenseWrapper>} />
        <Route path="transport" element={<SuspenseWrapper><TransportPage /></SuspenseWrapper>} />
        <Route path="hostel" element={<SuspenseWrapper><HostelPage /></SuspenseWrapper>} />
        <Route path="inventory" element={<SuspenseWrapper><InventoryPage /></SuspenseWrapper>} />
        <Route path="health" element={<SuspenseWrapper><HealthPage /></SuspenseWrapper>} />
        <Route path="discipline" element={<SuspenseWrapper><DisciplinePage /></SuspenseWrapper>} />
        <Route path="analytics" element={<SuspenseWrapper><AnalyticsPage /></SuspenseWrapper>} />
      </Route>

      {/* Redirects */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
