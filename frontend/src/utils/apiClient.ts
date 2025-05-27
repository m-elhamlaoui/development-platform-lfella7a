// API client for making authenticated requests

// Base URL for the backend API
const API_BASE_URL = 'http://localhost:28081/auth-backend/api';

// Helper to get auth token
const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token');
  }
  return null;
};

// Generic fetch wrapper with authentication
export const apiClient = {
  /**
   * Makes an authenticated API request
   * @param endpoint API endpoint path (without the base URL)
   * @param options Fetch options
   * @returns Promise with the response
   */
  async fetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    // Prepare headers with authentication if token exists
    const token = getAuthToken();
    const headers = new Headers(options.headers);
    
    // Set content type if not already set
    if (!headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }
    
    // Add authorization header if token exists
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    
    // Prepare the request with the auth headers and CORS settings
    const requestOptions: RequestInit = {
      ...options,
      headers,
      mode: 'cors', // Enable CORS mode
      credentials: 'include', // Include credentials like cookies
    };
    
    try {
      // Make the request
      const response = await fetch(`${API_BASE_URL}${endpoint}`, requestOptions);
      
      // Handle error responses
      if (!response.ok) {
        // Try to parse error message from response
        try {
          const errorData = await response.json();
          throw new Error(errorData.message || `Error ${response.status}: ${response.statusText}`);
        } catch (parseError) {
          // If error response cannot be parsed, use status text
          throw new Error(`Request failed: ${response.status} ${response.statusText}`);
        }
      }
      
      // Parse successful response
      // For empty responses (like 204 No Content), return an empty object
      if (response.status === 204) {
        return {} as T;
      }
      
      // For other successful responses, try to parse JSON
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  },
  
  /**
   * Shorthand for GET requests
   */
  async get<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    return this.fetch<T>(endpoint, { ...options, method: 'GET' });
  },
  
  /**
   * Shorthand for POST requests
   */
  async post<T>(endpoint: string, data: any, options: RequestInit = {}): Promise<T> {
    return this.fetch<T>(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  /**
   * Shorthand for PUT requests
   */
  async put<T>(endpoint: string, data: any, options: RequestInit = {}): Promise<T> {
    return this.fetch<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },
  
  /**
   * Shorthand for DELETE requests
   */
  async delete<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    return this.fetch<T>(endpoint, { ...options, method: 'DELETE' });
  }
}; 