/**
 * Validation utility functions
 */

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Validate phone number (basic)
 */
export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^\+?[\d\s\-()]+$/
  return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10
}

/**
 * Validate URL format
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * Check if string is empty or whitespace only
 */
export function isEmpty(text: string): boolean {
  return !text || text.trim().length === 0
}

/**
 * Validate password strength
 */
export function isStrongPassword(password: string): boolean {
  const rules = [
    password.length >= 8, // at least 8 chars
    /[A-Z]/.test(password), // has uppercase
    /[a-z]/.test(password), // has lowercase
    /\d/.test(password), // has number
    /[^A-Za-z\d]/.test(password), // has special char
  ]
  return rules.filter(Boolean).length >= 4
}
