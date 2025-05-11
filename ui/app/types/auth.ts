export enum UserRole {
  USER = "user",
  ADMIN = "admin",
}

export interface User {
  username: string;
  email: string;
  full_name?: string;
  role: UserRole;
  created_at: string;
  is_active: boolean;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface DecodedToken {
  sub: string;
  role: UserRole;
  exp: number;
} 