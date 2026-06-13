// ─── Common ──────────────────────────────────
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiError {
  status_code: number
  errors: { field: string; message: string }[]
}

// ─── Auth ────────────────────────────────────
export type UserRole =
  | 'super_admin'
  | 'school_admin'
  | 'principal'
  | 'teacher'
  | 'student'
  | 'parent'
  | 'accountant'
  | 'librarian'
  | 'hr'
  | 'transport_manager'
  | 'nurse'
  | 'staff'

export interface User {
  id: string
  email: string
  username: string
  first_name: string
  last_name: string
  phone: string
  avatar: string
  role: UserRole
  school: string | null
  school_name: string
  full_name: string
  is_active: boolean
  date_joined: string
  last_login: string | null
  mfa_enabled: boolean
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface TokenResponse {
  access: string
  refresh: string
}

// ─── Core ────────────────────────────────────
export interface School {
  id: string
  name: string
  code: string
  logo: string
  email: string
  phone: string
  website: string
  address_line1: string
  city: string
  state: string
  country: string
  postal_code: string
  timezone: string
  currency: string
  is_active: boolean
  subscription_plan: string
  max_students: number
  max_staff: number
  created_at: string
}

export interface Campus {
  id: string
  school: string
  school_name: string
  name: string
  code: string
  city: string
  is_active: boolean
  is_main: boolean
}

export interface AcademicYear {
  id: string
  school: string
  name: string
  start_date: string
  end_date: string
  is_current: boolean
  terms: Term[]
}

export interface Term {
  id: string
  academic_year: string
  name: string
  term_type: string
  start_date: string
  end_date: string
  is_current: boolean
  order: number
}

// ─── Students ────────────────────────────────
export interface Student {
  id: string
  user: string
  school: string
  student_id: string
  admission_number: string
  admission_date: string
  full_name: string
  email: string
  date_of_birth: string
  gender: string
  class_name: string
  section_name: string
  current_class: string | null
  current_section: string | null
  roll_number: string
  status: string
  photo: string
}

export interface Parent {
  id: string
  user: string
  school: string
  full_name: string
  email: string
  occupation: string
  children: { student_id: string; name: string; relationship: string }[]
}

// ─── Academics ───────────────────────────────
export interface Department {
  id: string
  school: string
  name: string
  code: string
  head: string | null
  head_name: string
  is_active: boolean
}

export interface Class {
  id: string
  school: string
  name: string
  code: string
  numeric_level: number
  capacity: number
  is_active: boolean
  sections: Section[]
  student_count: number
}

export interface Section {
  id: string
  class_obj: string
  class_name: string
  name: string
  capacity: number
  class_teacher: string | null
  teacher_name: string
  is_active: boolean
}

export interface Subject {
  id: string
  school: string
  department: string | null
  department_name: string
  name: string
  code: string
  subject_type: string
  credits: number
  is_active: boolean
  is_mandatory: boolean
}

export interface Teacher {
  id: string
  user: string
  school: string
  employee_id: string
  department: string | null
  department_name: string
  designation: string
  full_name: string
  email: string
  is_active: boolean
}

export interface Enrollment {
  id: string
  student: string
  student_name: string
  class_obj: string
  class_name: string
  section: string | null
  section_name: string
  academic_year: string
  roll_number: string
  is_active: boolean
}

// ─── Attendance ──────────────────────────────
export interface StudentAttendance {
  id: string
  student: string
  student_name: string
  student_id: string
  class_obj: string
  section: string | null
  date: string
  status: 'present' | 'absent' | 'late' | 'excused' | 'half_day'
  marking_method: string
  remarks: string
}

// ─── Examinations ────────────────────────────
export interface Exam {
  id: string
  school: string
  academic_year: string
  term: string
  exam_type: string
  exam_type_name: string
  name: string
  start_date: string
  end_date: string
  is_published: boolean
}

export interface Grade {
  id: string
  student: string
  student_name: string
  exam_schedule: string
  subject_name: string
  marks_obtained: number
  grade_letter: string
  percentage: number
  is_passed: boolean
}

export interface ReportCard {
  id: string
  student: string
  student_name: string
  academic_year: string
  term: string
  percentage: number
  gpa: number | null
  rank: number | null
  is_published: boolean
}

// ─── Finance ─────────────────────────────────
export interface Invoice {
  id: string
  invoice_number: string
  student: string
  student_name: string
  issue_date: string
  due_date: string
  total_amount: number
  paid_amount: number
  balance: number
  status: string
}

export interface Payment {
  id: string
  invoice: string
  invoice_number: string
  student: string
  student_name: string
  amount: number
  payment_method: string
  payment_date: string
  receipt_number: string
  status: string
}

export interface FeeCategory {
  id: string
  school: string
  name: string
  is_recurring: boolean
  is_active: boolean
}

// ─── LMS ─────────────────────────────────────
export interface Course {
  id: string
  title: string
  description: string
  instructor: string
  instructor_name: string
  thumbnail: string
  is_published: boolean
  module_count: number
}

export interface Assignment {
  id: string
  title: string
  description: string
  class_obj: string
  class_name: string
  subject: string
  subject_name: string
  teacher: string
  teacher_name: string
  due_date: string
  max_marks: number
  is_published: boolean
  assignment_type: string
}

// ─── Admissions ──────────────────────────────
export interface AdmissionApplication {
  id: string
  application_number: string
  school: string
  first_name: string
  last_name: string
  email: string
  phone: string
  date_of_birth: string
  gender: string
  applying_for_class: string
  class_name: string
  status: string
  merit_score: number | null
  parent_name: string
  parent_email: string
  parent_phone: string
  previous_school: string
  remarks: string
  created_at: string
}

// ─── Communication ──────────────────────────
export interface Message {
  id: string
  sender: string
  recipient: string
  subject: string
  body: string
  is_read: boolean
  created_at: string
}

export interface Announcement {
  id: string
  title: string
  content: string
  author: string
  target_audience: string
  is_pinned: boolean
  is_active: boolean
  created_at: string
}

export interface Notification {
  id: string
  title: string
  message: string
  notification_type: string
  is_read: boolean
  created_at: string
  link: string
}

// ─── Library ─────────────────────────────────
export interface Book {
  id: string
  title: string
  isbn: string
  author: string
  publisher: string
  category: string
  total_copies: number
  available_copies: number
  is_active: boolean
}

// ─── Transport ───────────────────────────────
export interface Vehicle {
  id: string
  vehicle_number: string
  vehicle_type: string
  capacity: number
  is_active: boolean
}

export interface BusRoute {
  id: string
  name: string
  code: string
  start_location: string
  end_location: string
  monthly_fee: number
  is_active: boolean
}

// ─── HR ──────────────────────────────────────
export interface LeaveRequest {
  id: string
  employee: string
  leave_type: string
  start_date: string
  end_date: string
  days: number
  reason: string
  status: string
}

// ─── Timetable ───────────────────────────────
export interface TimetableEntry {
  id: string
  class_obj: string
  class_name: string
  section: string | null
  section_name: string
  subject: string
  subject_name: string
  teacher: string
  teacher_name: string
  room: string | null
  period: string
  day_of_week: string
}

// ─── Discipline ──────────────────────────────
export interface DisciplineIncident {
  id: string
  student: string
  student_name: string
  category: string
  incident_date: string
  description: string
  status: string
  action_taken: string
}

// ─── Analytics ───────────────────────────────
export interface DashboardWidget {
  id: string
  title: string
  widget_type: string
  data_source: string
  config: Record<string, unknown>
  position: number
}
