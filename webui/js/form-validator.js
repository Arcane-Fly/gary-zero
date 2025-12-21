/**
 * Form Validation Utilities
 * Provides reusable validation functions for form inputs
 * Implements DRY principles for common validation patterns
 */

/**
 * Validation result structure
 * @typedef {Object} ValidationResult
 * @property {boolean} valid - Whether the validation passed
 * @property {string} [error] - Error message if validation failed
 */

/**
 * Email validation regex (RFC 5322 simplified)
 */
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * URL validation regex
 */
const URL_REGEX = /^https?:\/\/.+/;

/**
 * Validation rules registry
 */
export const ValidationRules = {
  /**
   * Validate required field
   * @param {any} value - Value to validate
   * @returns {ValidationResult}
   */
  required(value) {
    const isEmpty = value === null || value === undefined || value === '' || 
                    (Array.isArray(value) && value.length === 0);
    
    return {
      valid: !isEmpty,
      error: isEmpty ? 'This field is required' : undefined
    };
  },

  /**
   * Validate email format
   * @param {string} value - Email to validate
   * @returns {ValidationResult}
   */
  email(value) {
    if (!value) {
      return { valid: true }; // Empty is valid, use required() for required validation
    }

    const isValid = EMAIL_REGEX.test(value);
    return {
      valid: isValid,
      error: isValid ? undefined : 'Please enter a valid email address'
    };
  },

  /**
   * Validate URL format
   * @param {string} value - URL to validate
   * @returns {ValidationResult}
   */
  url(value) {
    if (!value) {
      return { valid: true };
    }

    const isValid = URL_REGEX.test(value);
    return {
      valid: isValid,
      error: isValid ? undefined : 'Please enter a valid URL'
    };
  },

  /**
   * Validate minimum length
   * @param {number} min - Minimum length
   * @returns {Function} Validator function
   */
  minLength(min) {
    return (value) => {
      if (!value) {
        return { valid: true };
      }

      const length = typeof value === 'string' ? value.length : 
                     Array.isArray(value) ? value.length : 0;
      const isValid = length >= min;

      return {
        valid: isValid,
        error: isValid ? undefined : `Must be at least ${min} characters`
      };
    };
  },

  /**
   * Validate maximum length
   * @param {number} max - Maximum length
   * @returns {Function} Validator function
   */
  maxLength(max) {
    return (value) => {
      if (!value) {
        return { valid: true };
      }

      const length = typeof value === 'string' ? value.length : 
                     Array.isArray(value) ? value.length : 0;
      const isValid = length <= max;

      return {
        valid: isValid,
        error: isValid ? undefined : `Must be no more than ${max} characters`
      };
    };
  },

  /**
   * Validate numeric value
   * @param {any} value - Value to validate
   * @returns {ValidationResult}
   */
  numeric(value) {
    if (!value) {
      return { valid: true };
    }

    const isValid = !isNaN(parseFloat(value)) && isFinite(value);
    return {
      valid: isValid,
      error: isValid ? undefined : 'Must be a valid number'
    };
  },

  /**
   * Validate minimum value
   * @param {number} min - Minimum value
   * @returns {Function} Validator function
   */
  min(min) {
    return (value) => {
      if (!value) {
        return { valid: true };
      }

      const numValue = parseFloat(value);
      const isValid = !isNaN(numValue) && numValue >= min;

      return {
        valid: isValid,
        error: isValid ? undefined : `Must be at least ${min}`
      };
    };
  },

  /**
   * Validate maximum value
   * @param {number} max - Maximum value
   * @returns {Function} Validator function
   */
  max(max) {
    return (value) => {
      if (!value) {
        return { valid: true };
      }

      const numValue = parseFloat(value);
      const isValid = !isNaN(numValue) && numValue <= max;

      return {
        valid: isValid,
        error: isValid ? undefined : `Must be no more than ${max}`
      };
    };
  },

  /**
   * Validate pattern match
   * @param {RegExp} pattern - Regular expression pattern
   * @param {string} [message] - Custom error message
   * @returns {Function} Validator function
   */
  pattern(pattern, message = 'Invalid format') {
    return (value) => {
      if (!value) {
        return { valid: true };
      }

      const isValid = pattern.test(value);
      return {
        valid: isValid,
        error: isValid ? undefined : message
      };
    };
  },

  /**
   * Validate that value matches another field
   * @param {string} otherFieldName - Name of field to match
   * @param {Function} getFieldValue - Function to get other field value
   * @returns {Function} Validator function
   */
  matches(otherFieldName, getFieldValue) {
    return (value) => {
      const otherValue = getFieldValue(otherFieldName);
      const isValid = value === otherValue;

      return {
        valid: isValid,
        error: isValid ? undefined : `Must match ${otherFieldName}`
      };
    };
  }
};

/**
 * Form validator class
 */
export class FormValidator {
  /**
   * Create a new form validator
   * @param {Object} schema - Validation schema
   */
  constructor(schema) {
    this.schema = schema;
    this.errors = {};
  }

  /**
   * Validate a single field
   * @param {string} fieldName - Field name
   * @param {any} value - Field value
   * @returns {ValidationResult}
   */
  validateField(fieldName, value) {
    const fieldRules = this.schema[fieldName];
    
    if (!fieldRules) {
      return { valid: true };
    }

    // Ensure rules is an array
    const rules = Array.isArray(fieldRules) ? fieldRules : [fieldRules];

    // Run all validators for this field
    for (const rule of rules) {
      const result = typeof rule === 'function' ? rule(value) : rule;
      
      if (!result.valid) {
        return result;
      }
    }

    return { valid: true };
  }

  /**
   * Validate entire form
   * @param {Object} formData - Form data object
   * @returns {Object} Validation result with errors object
   */
  validate(formData) {
    this.errors = {};
    let isValid = true;

    // Validate each field in schema
    for (const fieldName in this.schema) {
      const value = formData[fieldName];
      const result = this.validateField(fieldName, value);

      if (!result.valid) {
        this.errors[fieldName] = result.error;
        isValid = false;
      }
    }

    return {
      valid: isValid,
      errors: this.errors
    };
  }

  /**
   * Clear all errors
   */
  clearErrors() {
    this.errors = {};
  }

  /**
   * Get error for specific field
   * @param {string} fieldName - Field name
   * @returns {string|undefined} Error message
   */
  getError(fieldName) {
    return this.errors[fieldName];
  }

  /**
   * Check if field has error
   * @param {string} fieldName - Field name
   * @returns {boolean}
   */
  hasError(fieldName) {
    return !!this.errors[fieldName];
  }
}

/**
 * Create a form validator with schema
 * @param {Object} schema - Validation schema
 * @returns {FormValidator}
 */
export function createValidator(schema) {
  return new FormValidator(schema);
}

/**
 * Validate a form instantly
 * @param {Object} formData - Form data
 * @param {Object} schema - Validation schema
 * @returns {Object} Validation result
 */
export function validateForm(formData, schema) {
  const validator = new FormValidator(schema);
  return validator.validate(formData);
}

// Export default object
export default {
  ValidationRules,
  FormValidator,
  createValidator,
  validateForm
};
