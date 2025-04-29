/**
 * Interface for Service Reports
 * Represents reports submitted by users about problematic services
 */
export interface ServiceReport {
  id: number;
  service: number;
  service_name?: string;
  service_title?: string;
  service_provider?: string;
  reporter: number;
  reporter_name?: string;
  reporter_username?: string;
  reason: string;
  description?: string;
  status?: string;
  status_display?: string;
  reviewer?: number;
  reviewer_name?: string;
  created_at: string;
  updated_at?: string;
  reviewed?: boolean;
  service_id?: number; // Alias for service
}