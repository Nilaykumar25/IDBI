/**
 * API client for MSME Financial Health Score backend.
 * Handles authentication token injection, error handling, and retry logic.
 */
import axios from 'axios'
import { supabase } from '../config/supabase'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

// Maximum number of retry attempts for transient failures
const MAX_RETRIES = 2
// Delay between retries (ms)
const RETRY_DELAY = 1000

/**
 * Determines if an error is a transient network error that should be retried
 */
const isTransientError = (error) => {
  // Network errors (no response received)
  if (!error.response) {
    return true
  }

  // Server errors (5xx) are typically transient
  const status = error.response.status
  if (status >= 500 && status < 600) {
    return true
  }

  // 408 Request Timeout
  if (status === 408) {
    return true
  }

  // 429 Too Many Requests (rate limiting)
  if (status === 429) {
    return true
  }

  return false
}

/**
 * Sleep utility for retry delay
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * Transforms backend errors into user-friendly messages
 */
export const transformError = (error) => {
  // Network error (no response received)
  if (!error.response) {
    return {
      message: 'Unable to connect to the server. Please check your internet connection.',
      severity: 'error',
      retryable: true,
      technical: error.message
    }
  }

  const status = error.response.status
  const data = error.response.data

  // Authentication errors
  if (status === 401) {
    return {
      message: 'Your session has expired. Please log in again.',
      severity: 'error',
      retryable: false,
      technical: 'Authentication required'
    }
  }

  // Authorization errors
  if (status === 403) {
    return {
      message: 'You do not have permission to access this resource.',
      severity: 'error',
      retryable: false,
      technical: data?.error || 'Access forbidden'
    }
  }

  // Not found errors
  if (status === 404) {
    return {
      message: data?.error || 'The requested resource was not found.',
      severity: 'warning',
      retryable: false,
      technical: 'Resource not found'
    }
  }

  // Validation errors
  if (status === 400) {
    return {
      message: data?.error || 'Invalid request. Please check your input and try again.',
      severity: 'warning',
      retryable: false,
      technical: data?.error || 'Bad request'
    }
  }

  // Rate limiting
  if (status === 429) {
    return {
      message: 'Too many requests. Please wait a moment and try again.',
      severity: 'warning',
      retryable: true,
      technical: 'Rate limit exceeded'
    }
  }

  // Server errors
  if (status >= 500) {
    return {
      message: 'A server error occurred. Please try again in a few moments.',
      severity: 'error',
      retryable: true,
      technical: data?.error || `Server error (${status})`
    }
  }

  // Generic error
  return {
    message: data?.error || 'An unexpected error occurred. Please try again.',
    severity: 'error',
    retryable: false,
    technical: data?.error || error.message
  }
}

// Create axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
})

// Request interceptor - inject auth token
apiClient.interceptors.request.use(
  async (config) => {
    // Get current session
    const { data: { session } } = await supabase.auth.getSession()
    
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`
    }
    
    // Add retry attempt tracking
    config._retryCount = config._retryCount || 0
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors and retries
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config

    // Authentication errors - redirect to login
    if (error.response?.status === 401) {
      window.location.href = '/login'
      return Promise.reject(error)
    }

    // Check if error is retryable and we haven't exceeded max retries
    if (isTransientError(error) && config && config._retryCount < MAX_RETRIES) {
      config._retryCount += 1

      // Wait before retrying (exponential backoff)
      const delay = RETRY_DELAY * Math.pow(2, config._retryCount - 1)
      await sleep(delay)

      // Retry the request
      return apiClient(config)
    }

    return Promise.reject(error)
  }
)

/**
 * Wrapper function to call API with enhanced error handling
 * Returns standardized response format
 */
export const callAPI = async (apiFunction) => {
  try {
    const response = await apiFunction()
    return {
      success: true,
      data: response.data,
      error: null
    }
  } catch (error) {
    const transformedError = transformError(error)
    return {
      success: false,
      data: null,
      error: transformedError
    }
  }
}

// Export API client and utilities
export default apiClient
