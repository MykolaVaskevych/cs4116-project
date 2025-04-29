export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  role: 'CUSTOMER' | 'BUSINESS' | 'MODERATOR';
  role_display?: string;
  is_verified_customer?: boolean;
  is_business?: boolean;
  is_moderator?: boolean;
  is_active?: boolean;
  profile_image?: string;
  bio?: string;
  expertise?: string;
  created_at?: string;
}