/**
 * CSS/Tailwind Utility Classes
 * Consolidates repeated class combinations for better maintainability
 */

/**
 * Common utility class combinations
 */
export const UtilityClasses = {
  // Layout
  flexCenter: 'flex items-center justify-center',
  flexBetween: 'flex items-center justify-between',
  flexCol: 'flex flex-col',
  flexColCenter: 'flex flex-col items-center justify-center',
  
  // Spacing
  p4: 'p-4',
  px4: 'px-4',
  py4: 'py-4',
  m4: 'm-4',
  mx4: 'mx-4',
  my4: 'my-4',
  gap4: 'gap-4',
  
  // Borders
  border: 'border border-gray-300',
  borderRounded: 'border border-gray-300 rounded-lg',
  roundedFull: 'rounded-full',
  roundedLg: 'rounded-lg',
  
  // Shadows
  shadowSm: 'shadow-sm',
  shadowMd: 'shadow-md',
  shadowLg: 'shadow-lg',
  shadowCard: 'shadow-md hover:shadow-lg transition-shadow',
  
  // Text
  textSm: 'text-sm',
  textBase: 'text-base',
  textLg: 'text-lg',
  textXl: 'text-xl',
  text2xl: 'text-2xl',
  textCenter: 'text-center',
  textBold: 'font-bold',
  textSemibold: 'font-semibold',
  textMuted: 'text-gray-500',
  
  // Buttons
  btnPrimary: 'px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors',
  btnSecondary: 'px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors',
  btnDanger: 'px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors',
  btnSuccess: 'px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors',
  btnDisabled: 'px-4 py-2 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed',
  
  // Cards
  card: 'bg-white rounded-lg shadow-md p-4',
  cardHover: 'bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow',
  
  // Forms
  input: 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
  inputError: 'w-full px-4 py-2 border border-red-500 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
  label: 'block text-sm font-semibold mb-2',
  
  // Loading
  spinner: 'animate-spin rounded-full border-2 border-gray-300 border-t-blue-500',
  
  // Transitions
  transitionAll: 'transition-all duration-200 ease-in-out',
  transitionColors: 'transition-colors duration-200 ease-in-out',
  transitionOpacity: 'transition-opacity duration-200 ease-in-out',
  
  // Visibility
  hidden: 'hidden',
  visible: 'visible',
  invisible: 'invisible',
  
  // Positioning
  absolute: 'absolute',
  relative: 'relative',
  fixed: 'fixed',
  
  // Width/Height
  wFull: 'w-full',
  hFull: 'h-full',
  wScreen: 'w-screen',
  hScreen: 'h-screen',
  
  // Overflow
  overflowHidden: 'overflow-hidden',
  overflowAuto: 'overflow-auto',
  overflowScroll: 'overflow-scroll',
};

/**
 * Dark mode variants
 */
export const DarkModeClasses = {
  // Backgrounds
  bgPrimary: 'bg-white dark:bg-gray-900',
  bgSecondary: 'bg-gray-50 dark:bg-gray-800',
  bgTertiary: 'bg-gray-100 dark:bg-gray-700',
  
  // Text
  textPrimary: 'text-gray-900 dark:text-gray-100',
  textSecondary: 'text-gray-700 dark:text-gray-300',
  textMuted: 'text-gray-500 dark:text-gray-400',
  
  // Borders
  borderPrimary: 'border-gray-300 dark:border-gray-700',
  borderSecondary: 'border-gray-200 dark:border-gray-600',
  
  // Inputs
  input: 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100',
  
  // Cards
  card: 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700',
};

/**
 * Responsive utility classes
 */
export const ResponsiveClasses = {
  // Containers
  container: 'container mx-auto px-4 sm:px-6 lg:px-8',
  
  // Grid
  grid1: 'grid grid-cols-1',
  grid2: 'grid grid-cols-1 md:grid-cols-2',
  grid3: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
  grid4: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
  
  // Hide/Show
  showOnMobile: 'block md:hidden',
  showOnTablet: 'hidden md:block lg:hidden',
  showOnDesktop: 'hidden lg:block',
  hideOnMobile: 'hidden md:block',
  hideOnDesktop: 'block lg:hidden',
};

/**
 * Combine multiple utility classes
 * @param  {...string} classes - Class names or class combinations
 * @returns {string} Combined class string
 */
export function cn(...classes) {
  return classes.filter(Boolean).join(' ');
}

/**
 * Apply utility classes conditionally
 * @param {Object} conditions - Object with condition-class pairs
 * @returns {string} Combined class string
 */
export function classNames(conditions) {
  return Object.keys(conditions)
    .filter(key => conditions[key])
    .join(' ');
}

/**
 * Get button classes based on variant
 * @param {string} variant - Button variant (primary, secondary, danger, success)
 * @param {boolean} disabled - Whether button is disabled
 * @returns {string} Button classes
 */
export function getButtonClasses(variant = 'primary', disabled = false) {
  if (disabled) {
    return UtilityClasses.btnDisabled;
  }
  
  const variants = {
    primary: UtilityClasses.btnPrimary,
    secondary: UtilityClasses.btnSecondary,
    danger: UtilityClasses.btnDanger,
    success: UtilityClasses.btnSuccess,
  };
  
  return variants[variant] || variants.primary;
}

/**
 * Get input classes based on error state
 * @param {boolean} hasError - Whether input has error
 * @returns {string} Input classes
 */
export function getInputClasses(hasError = false) {
  return hasError ? UtilityClasses.inputError : UtilityClasses.input;
}

// Export default object
export default {
  UtilityClasses,
  DarkModeClasses,
  ResponsiveClasses,
  cn,
  classNames,
  getButtonClasses,
  getInputClasses,
};
