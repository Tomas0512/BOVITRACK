export interface RegisterRequest {
  email: string;
  first_name: string;
  last_name: string;
  document_type: 'CC' | 'CE' | 'TI' | 'PP' | 'NIT';
  document_number: string;
  phone: string;
  password: string;
  accept_terms: boolean;
  accept_data_policy: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface UserResponse {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  document_type: string;
  document_number: string;
  phone: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface MessageResponse {
  message: string;
}