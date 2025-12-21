/**
 * Input Sanitization Utilities
 * Provides functions to sanitize and escape user input to prevent XSS and other attacks
 */

/**
 * HTML entity map for escaping
 */
const HTML_ENTITIES = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#x27;',
  '/': '&#x2F;',
};

/**
 * Escape HTML entities to prevent XSS
 * @param {string} str - String to escape
 * @returns {string} Escaped string
 */
export function escapeHtml(str) {
  if (typeof str !== 'string') {
    return str;
  }
  
  return str.replace(/[&<>"'/]/g, (char) => HTML_ENTITIES[char] || char);
}

/**
 * Strip HTML tags from string
 * @param {string} str - String to strip
 * @returns {string} String without HTML tags
 */
export function stripHtml(str) {
  if (typeof str !== 'string') {
    return str;
  }
  
  return str.replace(/<[^>]*>/g, '');
}

/**
 * Sanitize string for use in SQL LIKE patterns
 * @param {string} str - String to sanitize
 * @returns {string} Sanitized string
 */
export function sanitizeLike(str) {
  if (typeof str !== 'string') {
    return str;
  }
  
  // Escape special SQL LIKE characters
  return str.replace(/[%_\\]/g, '\\$&');
}

/**
 * Sanitize filename to prevent directory traversal
 * @param {string} filename - Filename to sanitize
 * @returns {string} Safe filename
 */
export function sanitizeFilename(filename) {
  if (typeof filename !== 'string') {
    return '';
  }
  
  // Remove path separators and null bytes
  return filename
    .replace(/[/\\]/g, '')
    .replace(/\0/g, '')
    .replace(/\.\./g, '')
    .trim();
}

/**
 * Sanitize URL to prevent javascript: and data: URLs
 * @param {string} url - URL to sanitize
 * @returns {string} Safe URL or empty string if unsafe
 */
export function sanitizeUrl(url) {
  if (typeof url !== 'string') {
    return '';
  }
  
  const trimmed = url.trim().toLowerCase();
  
  // Block dangerous protocols
  const dangerousProtocols = ['javascript:', 'data:', 'vbscript:'];
  if (dangerousProtocols.some(protocol => trimmed.startsWith(protocol))) {
    return '';
  }
  
  return url;
}

/**
 * Sanitize attribute value for HTML attributes
 * @param {string} value - Attribute value to sanitize
 * @returns {string} Safe attribute value
 */
export function sanitizeAttribute(value) {
  if (typeof value !== 'string') {
    return '';
  }
  
  // Escape quotes and angle brackets
  return value
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

/**
 * Sanitize CSS value to prevent CSS injection
 * @param {string} value - CSS value to sanitize
 * @returns {string} Safe CSS value
 */
export function sanitizeCss(value) {
  if (typeof value !== 'string') {
    return '';
  }
  
  // Remove potentially dangerous CSS
  return value
    .replace(/javascript:/gi, '')
    .replace(/expression\(/gi, '')
    .replace(/import/gi, '')
    .replace(/@import/gi, '')
    .replace(/behavior:/gi, '');
}

/**
 * Sanitize JSON string to prevent injection
 * @param {string} jsonStr - JSON string to sanitize
 * @returns {string} Safe JSON string or empty object
 */
export function sanitizeJson(jsonStr) {
  if (typeof jsonStr !== 'string') {
    return '{}';
  }
  
  try {
    // Parse and re-stringify to ensure it's valid JSON
    const parsed = JSON.parse(jsonStr);
    return JSON.stringify(parsed);
  } catch (e) {
    return '{}';
  }
}

/**
 * Sanitize email address
 * @param {string} email - Email to sanitize
 * @returns {string} Sanitized email
 */
export function sanitizeEmail(email) {
  if (typeof email !== 'string') {
    return '';
  }
  
  // Remove whitespace and convert to lowercase
  return email.trim().toLowerCase();
}

/**
 * Sanitize phone number
 * @param {string} phone - Phone number to sanitize
 * @returns {string} Sanitized phone (digits, +, -, (, ), and spaces only)
 */
export function sanitizePhone(phone) {
  if (typeof phone !== 'string') {
    return '';
  }
  
  // Keep only valid phone characters
  return phone.replace(/[^0-9+\-() ]/g, '');
}

/**
 * Sanitize integer input
 * @param {any} value - Value to sanitize
 * @param {number} [defaultValue=0] - Default value if invalid
 * @returns {number} Sanitized integer
 */
export function sanitizeInt(value, defaultValue = 0) {
  const parsed = parseInt(value, 10);
  return isNaN(parsed) ? defaultValue : parsed;
}

/**
 * Sanitize float input
 * @param {any} value - Value to sanitize
 * @param {number} [defaultValue=0] - Default value if invalid
 * @returns {number} Sanitized float
 */
export function sanitizeFloat(value, defaultValue = 0) {
  const parsed = parseFloat(value);
  return isNaN(parsed) ? defaultValue : parsed;
}

/**
 * Sanitize boolean input
 * @param {any} value - Value to sanitize
 * @param {boolean} [defaultValue=false] - Default value if invalid
 * @returns {boolean} Sanitized boolean
 */
export function sanitizeBoolean(value, defaultValue = false) {
  if (typeof value === 'boolean') {
    return value;
  }
  
  if (typeof value === 'string') {
    const lower = value.toLowerCase().trim();
    if (lower === 'true' || lower === '1' || lower === 'yes') {
      return true;
    }
    if (lower === 'false' || lower === '0' || lower === 'no') {
      return false;
    }
  }
  
  return defaultValue;
}

/**
 * Sanitize array input
 * @param {any} value - Value to sanitize
 * @param {Function} [itemSanitizer] - Function to sanitize each item
 * @returns {Array} Sanitized array
 */
export function sanitizeArray(value, itemSanitizer = null) {
  if (!Array.isArray(value)) {
    return [];
  }
  
  if (itemSanitizer && typeof itemSanitizer === 'function') {
    return value.map(itemSanitizer);
  }
  
  return value;
}

/**
 * Sanitize object by applying sanitizers to each property
 * @param {Object} obj - Object to sanitize
 * @param {Object} schema - Schema with sanitizer functions for each property
 * @returns {Object} Sanitized object
 */
export function sanitizeObject(obj, schema) {
  if (typeof obj !== 'object' || obj === null) {
    return {};
  }
  
  const sanitized = {};
  
  for (const key in schema) {
    if (Object.prototype.hasOwnProperty.call(schema, key)) {
      const sanitizer = schema[key];
      if (typeof sanitizer === 'function') {
        sanitized[key] = sanitizer(obj[key]);
      } else {
        sanitized[key] = obj[key];
      }
    }
  }
  
  return sanitized;
}

/**
 * Create a sanitizer function with custom rules
 * @param {Function[]} rules - Array of sanitization functions
 * @returns {Function} Combined sanitizer function
 */
export function createSanitizer(...rules) {
  return (value) => {
    let sanitized = value;
    for (const rule of rules) {
      if (typeof rule === 'function') {
        sanitized = rule(sanitized);
      }
    }
    return sanitized;
  };
}

// Export default object
export default {
  escapeHtml,
  stripHtml,
  sanitizeLike,
  sanitizeFilename,
  sanitizeUrl,
  sanitizeAttribute,
  sanitizeCss,
  sanitizeJson,
  sanitizeEmail,
  sanitizePhone,
  sanitizeInt,
  sanitizeFloat,
  sanitizeBoolean,
  sanitizeArray,
  sanitizeObject,
  createSanitizer,
};
