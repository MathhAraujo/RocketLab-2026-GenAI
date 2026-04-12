export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  is_admin: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface AuthUser {
  username: string;
  is_admin: boolean;
}
