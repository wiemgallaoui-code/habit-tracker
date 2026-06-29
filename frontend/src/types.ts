export interface Habit {
  id: number;
  name: string;
  created_at: string;
  start_date: string;
  completed_today: boolean;
  current_streak: number;
  longest_streak: number;
  total_completions: number;
  completion_rate: number;
}

export interface Stats extends Habit {
  habit_id: number;
  created_on: string;
  tracking_start: string;
  days_tracked: number;
  last_completed: string | null;
}

export interface ApiError {
  detail: string;
}
