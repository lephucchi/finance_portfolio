/**
 * Environment Variables Configuration
 * 
 * This file centralizes all environment variable access with type safety and validation.
 * All environment variables must be prefixed with VITE_ to be exposed to the client.
 * 
 * @see https://vitejs.dev/guide/env-and-mode.html
 */

interface EnvConfig {
  // API Configuration
  apiBaseUrl: string;
  
  // Data Range
  dataStartDate: string;
  dataEndDate: string;
  
  // App Info
  appName: string;
  appVersion: string;
  
  // Feature Flags
  enableRagChat: boolean;
  enableAnalytics: boolean;
  enableExport: boolean;
  
  // API Settings
  apiTimeout: number;
  
  // Pagination
  defaultPageSize: number;
  maxPageSize: number;
  
  // Environment
  isDevelopment: boolean;
  isProduction: boolean;
}

/**
 * Get environment variable with fallback
 */
function getEnvVar(key: string, fallback: string = ''): string {
  return import.meta.env[key] || fallback;
}

/**
 * Get boolean environment variable
 */
function getEnvBool(key: string, fallback: boolean = false): boolean {
  const value = import.meta.env[key];
  if (value === undefined || value === '') return fallback;
  return value === 'true' || value === '1';
}

/**
 * Get number environment variable
 */
function getEnvNumber(key: string, fallback: number = 0): number {
  const value = import.meta.env[key];
  if (value === undefined || value === '') return fallback;
  const num = parseInt(value, 10);
  return isNaN(num) ? fallback : num;
}

/**
 * Validate required environment variables
 */
function validateEnv(): void {
  const required = [
    'VITE_API_BASE_URL',
    'VITE_DATA_START_DATE',
    'VITE_DATA_END_DATE',
  ];
  
  const missing = required.filter(key => !import.meta.env[key]);
  
  if (missing.length > 0) {
    console.error('❌ Missing required environment variables:', missing);
    console.error('💡 Please check your .env file');
  }
}

// Validate on module load
validateEnv();

/**
 * Environment configuration object
 * All environment variables are accessed through this object
 */
export const env: EnvConfig = {
  // API Configuration
  apiBaseUrl: getEnvVar('VITE_API_BASE_URL', 'http://localhost:8000/api/v1'),
  
  // Data Range (Backend available data: Oct 18-30, 2025)
  dataStartDate: getEnvVar('VITE_DATA_START_DATE', '2025-10-18'),
  dataEndDate: getEnvVar('VITE_DATA_END_DATE', '2025-10-30'),
  
  // App Info
  appName: getEnvVar('VITE_APP_NAME', 'Finance Portfolio'),
  appVersion: getEnvVar('VITE_APP_VERSION', '1.0.0'),
  
  // Feature Flags
  enableRagChat: getEnvBool('VITE_ENABLE_RAG_CHAT', false),
  enableAnalytics: getEnvBool('VITE_ENABLE_ANALYTICS', true),
  enableExport: getEnvBool('VITE_ENABLE_EXPORT', true),
  
  // API Settings
  apiTimeout: getEnvNumber('VITE_API_TIMEOUT', 30000),
  
  // Pagination
  defaultPageSize: getEnvNumber('VITE_DEFAULT_PAGE_SIZE', 50),
  maxPageSize: getEnvNumber('VITE_MAX_PAGE_SIZE', 100),
  
  // Environment
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
};

/**
 * Log environment configuration (development only)
 */
if (env.isDevelopment) {
  console.log('🔧 Environment Configuration:', {
    apiBaseUrl: env.apiBaseUrl,
    dataRange: `${env.dataStartDate} to ${env.dataEndDate}`,
    appName: env.appName,
    appVersion: env.appVersion,
    features: {
      ragChat: env.enableRagChat,
      analytics: env.enableAnalytics,
      export: env.enableExport,
    },
  });
}

// Export individual values for convenience
export const {
  apiBaseUrl,
  dataStartDate,
  dataEndDate,
  appName,
  appVersion,
  enableRagChat,
  enableAnalytics,
  enableExport,
  apiTimeout,
  defaultPageSize,
  maxPageSize,
  isDevelopment,
  isProduction,
} = env;

// Export default
export default env;
