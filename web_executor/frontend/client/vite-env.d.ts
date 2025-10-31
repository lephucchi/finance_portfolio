/// <reference types="vite/client" />

interface ImportMetaEnv {
  // API Configuration
  readonly VITE_API_BASE_URL: string;
  
  // Data Range
  readonly VITE_DATA_START_DATE: string;
  readonly VITE_DATA_END_DATE: string;
  
  // App Configuration
  readonly VITE_APP_NAME: string;
  readonly VITE_APP_VERSION: string;
  
  // Feature Flags
  readonly VITE_ENABLE_RAG_CHAT: string;
  readonly VITE_ENABLE_ANALYTICS: string;
  readonly VITE_ENABLE_EXPORT: string;
  
  // API Settings
  readonly VITE_API_TIMEOUT: string;
  
  // Pagination
  readonly VITE_DEFAULT_PAGE_SIZE: string;
  readonly VITE_MAX_PAGE_SIZE: string;
  
  // Vite built-in
  readonly DEV: boolean;
  readonly PROD: boolean;
  readonly MODE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
