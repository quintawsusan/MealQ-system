export type Role = "SUPER_ADMIN" | "ADMIN" | "STUDENT";
export type SessionStatus = "SCHEDULED" | "ACTIVE" | "PAUSED" | "COMPLETED";
export type BatchStatus = "WAITING" | "CALLED" | "COMPLETED";
export type MealResponse = "GOING" | "SKIPPED" | "NO_RESPONSE";

export interface User {
  user_id: string;
  first_name: string;
  last_name: string;
  user_name: string;
  email: string;
  role: Role;
  is_active: boolean;
  email_verified: boolean;
  failed_attempts: number;
  locked: boolean;
  created_at: string;
  updated_at: string;
}

export interface Student {
  student_id: string;
  user_id: string;
  student_number: number;
  class_id: string;
  class_name: string | null;
  created_at: string;
}

export interface MealType {
  meal_id: string;
  name: string;
  description: string | null;
}

export interface Schedule {
  schedule_id: string;
  meal_type_id: string;
  meal_date: string;
  start_time: string;
  end_time: string;
  menu_description: string | null;
  is_active: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface Session {
  session_id: string;
  schedule_id: string;
  status: SessionStatus;
  batch_size: number;
  release_interval_seconds: number;
  response_window: number;
  started_at: string | null;
  ended_at: string | null;
  created_by: string;
}

export interface BatchMember {
  student_id: string;
  student_number: number;
  student_position: number;
  response: MealResponse;
}

export interface Batch {
  batch_id: string;
  session_id: string;
  batch_number: number;
  status: BatchStatus;
  called_at: string | null;
  completed_at: string | null;
  members: BatchMember[];
}

export interface MyBatch {
  session_id: string;
  batch_id: string;
  batch_number: number;
  batch_status: BatchStatus;
  student_id: string;
  student_number: number;
  student_position: number;
  response: MealResponse;
  responded_at: string | null;
  is_currently_called: boolean;
  response_window_open: boolean;
}

export interface Monitor {
  session: Session;
  current_batch: Batch | null;
  total_students: number;
  going: number;
  skipped: number;
  no_response: number;
  waiting_batches: number;
  called_batches: number;
  completed_batches: number;
}

export interface Device {
  device_id: string;
  student_id: string;
  device_identifier: string;
  is_active: boolean;
}
