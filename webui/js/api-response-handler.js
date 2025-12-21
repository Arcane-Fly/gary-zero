/**
 * Centralized API Response Handler
 * Implements DRY principles for API error handling and response parsing
 */

/**
 * Standard API response structure
 * @typedef {Object} ApiResponse
 * @property {boolean} success - Indicates if the request was successful
 * @property {*} data - Response data
 * @property {string} [error] - Error message if request failed
 * @property {*} [detail] - Additional error details
 */

/**
 * API Error class for consistent error handling
 */
export class ApiError extends Error {
  constructor(message, statusCode, details = null) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.details = details;
  }
}

/**
 * Centralized API response handler
 * Handles success and error responses consistently across the application
 * 
 * @param {Response} response - Fetch API response object
 * @returns {Promise<*>} Parsed response data
 * @throws {ApiError} If the response indicates an error
 */
export async function handleApiResponse(response) {
  const contentType = response.headers.get('content-type');
  const isJson = contentType && contentType.includes('application/json');

  // Parse response body
  let data;
  try {
    if (isJson) {
      data = await response.json();
    } else {
      data = await response.text();
    }
  } catch (parseError) {
    throw new ApiError(
      'Failed to parse response',
      response.status,
      { parseError: parseError.message }
    );
  }

  // Handle successful responses
  if (response.ok) {
    // If response follows standard format
    if (data && typeof data === 'object' && 'success' in data) {
      if (data.success) {
        return data.data !== undefined ? data.data : data;
      } else {
        // Standard format but success: false
        throw new ApiError(
          data.error || 'Request failed',
          response.status,
          data.detail
        );
      }
    }
    // Non-standard successful response
    return data;
  }

  // Handle error responses
  let errorMessage = 'An error occurred';
  let errorDetails = null;

  if (typeof data === 'object' && data !== null) {
    errorMessage = data.error || data.message || errorMessage;
    errorDetails = data.detail || data.details || data;
  } else if (typeof data === 'string') {
    errorMessage = data;
  }

  throw new ApiError(errorMessage, response.status, errorDetails);
}

/**
 * Makes an API request with consistent error handling
 * 
 * @param {string} url - API endpoint URL
 * @param {RequestInit} [options] - Fetch options
 * @returns {Promise<*>} Response data
 */
export async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    return await handleApiResponse(response);
  } catch (error) {
    // Re-throw ApiError instances
    if (error instanceof ApiError) {
      throw error;
    }

    // Wrap network errors and other exceptions
    throw new ApiError(
      error.message || 'Network request failed',
      0,
      { originalError: error }
    );
  }
}

/**
 * GET request helper
 * @param {string} url - API endpoint URL
 * @param {RequestInit} [options] - Additional fetch options
 * @returns {Promise<*>} Response data
 */
export async function apiGet(url, options = {}) {
  return apiRequest(url, { ...options, method: 'GET' });
}

/**
 * POST request helper
 * @param {string} url - API endpoint URL
 * @param {*} data - Request body data
 * @param {RequestInit} [options] - Additional fetch options
 * @returns {Promise<*>} Response data
 */
export async function apiPost(url, data, options = {}) {
  return apiRequest(url, {
    ...options,
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * PUT request helper
 * @param {string} url - API endpoint URL
 * @param {*} data - Request body data
 * @param {RequestInit} [options] - Additional fetch options
 * @returns {Promise<*>} Response data
 */
export async function apiPut(url, data, options = {}) {
  return apiRequest(url, {
    ...options,
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * DELETE request helper
 * @param {string} url - API endpoint URL
 * @param {RequestInit} [options] - Additional fetch options
 * @returns {Promise<*>} Response data
 */
export async function apiDelete(url, options = {}) {
  return apiRequest(url, { ...options, method: 'DELETE' });
}

/**
 * PATCH request helper
 * @param {string} url - API endpoint URL
 * @param {*} data - Request body data
 * @param {RequestInit} [options] - Additional fetch options
 * @returns {Promise<*>} Response data
 */
export async function apiPatch(url, data, options = {}) {
  return apiRequest(url, {
    ...options,
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

/**
 * Helper to handle API errors with user-friendly messages
 * @param {Error} error - Error object
 * @param {string} [defaultMessage] - Default message if no specific error message
 * @returns {string} User-friendly error message
 */
export function getApiErrorMessage(error, defaultMessage = 'An unexpected error occurred') {
  if (error instanceof ApiError) {
    return error.message;
  }
  
  if (error && error.message) {
    return error.message;
  }
  
  return defaultMessage;
}

// Export default object with all functions
export default {
  handleApiResponse,
  apiRequest,
  apiGet,
  apiPost,
  apiPut,
  apiDelete,
  apiPatch,
  getApiErrorMessage,
  ApiError,
};
