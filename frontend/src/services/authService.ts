// Auth service for handling authentication with the backend
import { apiClient } from '@/utils/apiClient';

// Base API URL - this should point to our Jakarta EE backend
const API_URL = 'http://localhost:28081/auth-backend/api';

// Flag to enable mock authentication (for development when backend is not available)
export const USE_MOCK_AUTH = false;

// Types
export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  type: string;
  id: number;
  username: string;
  email: string;
}

// Helper to handle errors
const handleResponse = async (response: Response) => {
  if (!response.ok) {
    // Try to get error message from response
    try {
      const errorData = await response.json();
      throw new Error(errorData.message || 'An error occurred');
    } catch (e) {
      throw new Error(`Request failed with status ${response.status}`);
    }
  }
  
  return response.json();
};

// Authentication service functions
export const authService = {
  // Login user
  async login(data: LoginData): Promise<AuthResponse> {
    // For development/testing, use mock implementation when backend is not available
    if (USE_MOCK_AUTH) {
      return mockLogin(data);
    }
    
    try {
      // Use our API client to make the request
      const result = await apiClient.post<AuthResponse>('/auth/signin', data);
      
      // Store token in localStorage
      if (result.token) {
        localStorage.setItem('token', result.token);
        localStorage.setItem('isLoggedIn', 'true');
      }
      
      return result;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },
  
  // Register user
  async register(data: RegisterData): Promise<{ message: string }> {
    // For development/testing, use mock implementation when backend is not available
    if (USE_MOCK_AUTH) {
      return mockRegister(data);
    }
    
    try {
      // Use our API client to make the request
      const result = await apiClient.post<any>('/auth/signup', data);
      return { message: result.message || 'Registration successful!' };
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  },
  
  // Get current user info from token
  async getCurrentUser(): Promise<{ user: { id: number; username: string; email: string } } | null> {
    const token = localStorage.getItem('token');
    if (!token) return null;
    
    // For development/testing
    if (USE_MOCK_AUTH) {
      return mockGetCurrentUser();
    }
    
    // In a real implementation, you might want to fetch user data from the server
    // For now, we'll extract the user info from the JWT token
    try {
      // This is a simple implementation - in production you would verify the token properly
      const tokenPayload = parseJwt(token);
      
      if (!tokenPayload) {
        throw new Error('Invalid token');
      }
      
      return {
        user: {
          id: tokenPayload.id,
          username: tokenPayload.username,
          email: tokenPayload.email
        }
      };
    } catch (error) {
      console.error('Error getting current user:', error);
      this.logout(); // Clear invalid token
      return null;
    }
  },
  
  // Logout user
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('isLoggedIn');
  },
  
  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  },
  
  // Get the auth token
  getToken(): string | null {
    return localStorage.getItem('token');
  }
};

// Helper to parse JWT token
function parseJwt(token: string) {
  try {
    // Split the token and get the payload part
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    console.error('Error parsing JWT token:', e);
    return null;
  }
}

// Mock implementations for development/testing
function mockLogin(data: LoginData): Promise<AuthResponse> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Simulate basic validation
      if (data.username === 'user123' && data.password === 'password') {
        const mockToken = 'mock-jwt-token';
        localStorage.setItem('token', mockToken);
        localStorage.setItem('isLoggedIn', 'true');
        
        resolve({
          token: mockToken,
          type: 'Bearer',
          id: 1,
          username: data.username,
          email: 'user@example.com'
        });
      } else {
        reject(new Error('Invalid credentials'));
      }
    }, 800);
  });
}

function mockRegister(data: RegisterData): Promise<{ message: string }> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ message: 'Registration successful. You can now login.' });
    }, 800);
  });
}

function mockGetCurrentUser(): Promise<{ user: { id: number; username: string; email: string } }> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        user: {
          id: 1,
          username: 'user123',
          email: 'user@example.com'
        }
      });
    }, 300);
  });
} 