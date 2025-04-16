/**
 * Application initializer
 * Sets up global configurations, error handlers, and other initialization logic
 */

import { setupGlobalErrorHandlers, createError, ErrorCategory, ErrorSeverity, OperationalStatus } from '@utils/errorHandler';
import { logger } from '@utils/logger';
import { configService } from '@utils/configService';

// Initialize application
export const initializeApp = (): void => {
  try {
    logger.info('Initializing application', {
      version: configService.get('version'),
      environment: configService.get('environment'),
    });

    // Setup global error handlers
    setupGlobalErrorHandlers();
    logger.info('Global error handlers configured');

    // Set up document theme based on saved preferences or system defaults
    configureTheme();

    // Log initialization complete
    logger.info('Application initialized successfully');
  } catch (error) {
    const enhancedError = createError.internal(
      'Failed to initialize application',
      {
        severity: ErrorSeverity.CRITICAL,
        operational: OperationalStatus.NON_OPERATIONAL,
        context: { phase: 'initialization' }
      },
      error instanceof Error ? error : undefined
    );
    
    logger.error('Application initialization failed', enhancedError.toJSON());
    throw enhancedError;
  }
};

/**
 * Configure application theme based on user settings or system preferences
 */
const configureTheme = (): void => {
  const defaultTheme = configService.getSetting('defaultTheme');
  const isDarkMode = 
    defaultTheme === 'dark' || 
    (defaultTheme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  
  if (isDarkMode) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
  
  // Listen for system theme changes if using system preference
  if (defaultTheme === 'system') {
    const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleThemeChange = (event: MediaQueryListEvent): void => {
      if (event.matches) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    };
    
    darkModeMediaQuery.addEventListener('change', handleThemeChange);
    
    // Store cleanup function for potential future use
    // This could be exposed via a cleanup function if needed
    const removeListener = (): void => {
      darkModeMediaQuery.removeEventListener('change', handleThemeChange);
    };
  }
};

// Run performance monitoring
export const monitorPerformance = (): void => {
  try {
    // Measure load time
    reportLoadTime();
    
    // Monitor memory usage 
    reportMemoryUsage();
    
    // Performance metrics
    if (window.PerformanceObserver) {
      reportFirstContentfulPaint();
      reportLargestContentfulPaint();
      reportCumulativeLayoutShift();
      reportFirstInputDelay();
    }
  } catch (error) {
    const enhancedError = createError.internal(
      'Error monitoring performance',
      {
        severity: ErrorSeverity.MEDIUM,
        category: ErrorCategory.INTERNAL,
        context: { component: 'performanceMonitoring' }
      },
      error instanceof Error ? error : undefined
    );
    
    logger.error('Performance monitoring failed', enhancedError.toJSON());
  }
};

/**
 * Report page load time metrics
 */
const reportLoadTime = (): void => {
  if (!window.performance || !window.performance.timing) {
    logger.warn('Performance timing API not available');
    return;
  }
  
  const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
  logger.info('Page loaded', { loadTime: `${loadTime}ms` });
};

/**
 * Report memory usage if available
 */
const reportMemoryUsage = (): void => {
  if (!performance || !(performance as any).memory) {
    return;
  }
  
  const memoryInfo = (performance as any).memory;
  const heapSizeLimit = Math.round(memoryInfo.jsHeapSizeLimit / (1024 * 1024));
  const totalHeapSize = Math.round(memoryInfo.totalJSHeapSize / (1024 * 1024));
  const usedHeapSize = Math.round(memoryInfo.usedJSHeapSize / (1024 * 1024));
  
  logger.debug('Memory usage', {
    jsHeapSizeLimit: `${heapSizeLimit} MB`,
    totalJSHeapSize: `${totalHeapSize} MB`,
    usedJSHeapSize: `${usedHeapSize} MB`,
    heapUsagePercentage: `${Math.round((usedHeapSize / heapSizeLimit) * 100)}%`
  });
  
  // Alert on high memory usage (over 80%)
  if (usedHeapSize / heapSizeLimit > 0.8) {
    logger.warn('High memory usage detected', {
      usedPercent: `${Math.round((usedHeapSize / heapSizeLimit) * 100)}%`,
      available: `${heapSizeLimit - usedHeapSize} MB`
    });
  }
};

/**
 * Report First Contentful Paint metric
 */
const reportFirstContentfulPaint = (): void => {
  const perfEntries = performance.getEntriesByType('paint');
  const fcpEntry = perfEntries.find(entry => entry.name === 'first-contentful-paint');
  if (fcpEntry) {
    const fcp = Math.round(fcpEntry.startTime);
    logger.info('First Contentful Paint', { fcp: `${fcp}ms` });
  }
};

/**
 * Report Largest Contentful Paint metric
 */
const reportLargestContentfulPaint = (): void => {
  try {
    new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries();
      if (entries.length > 0) {
        const lastEntry = entries[entries.length - 1];
        const lcp = Math.round(lastEntry.startTime);
        logger.info('Largest Contentful Paint', { lcp: `${lcp}ms` });
      }
    }).observe({ type: 'largest-contentful-paint', buffered: true });
  } catch (error) {
    logger.warn('Failed to observe Largest Contentful Paint', { error });
  }
};

/**
 * Report Cumulative Layout Shift metric
 */
const reportCumulativeLayoutShift = (): void => {
  let cumulativeLayoutShift = 0;
  
  try {
    new PerformanceObserver((entryList) => {
      for (const entry of entryList.getEntries()) {
        if (!entry.hadRecentInput) {
          // @ts-ignore - layout shift value property
          cumulativeLayoutShift += entry.value;
        }
      }
      logger.info('Cumulative Layout Shift', { cls: cumulativeLayoutShift.toFixed(3) });
    }).observe({ type: 'layout-shift', buffered: true });
  } catch (error) {
    logger.warn('Failed to observe Cumulative Layout Shift', { error });
  }
};

/**
 * Report First Input Delay metric
 */
const reportFirstInputDelay = (): void => {
  try {
    new PerformanceObserver((entryList) => {
      const firstInput = entryList.getEntries()[0];
      if (firstInput) {
        // @ts-ignore - processingStart property
        const fid = Math.round(firstInput.processingStart - firstInput.startTime);
        logger.info('First Input Delay', { fid: `${fid}ms` });
      }
    }).observe({ type: 'first-input', buffered: true });
  } catch (error) {
    logger.warn('Failed to observe First Input Delay', { error });
  }
};

/**
 * Application cleanup on unload
 */
export const cleanupApp = (): void => {
  try {
    logger.info('Application cleanup initiated');
    
    // Save any unsaved state
    const pendingWrites = checkForPendingWrites();
    
    // Execute any other cleanup tasks here
    
    // Flush any unsent logs
    logger.info('Application terminated');
  } catch (error) {
    logger.error('Error during application cleanup', { 
      error: error instanceof Error ? { message: error.message, stack: error.stack } : String(error)
    });
  }
};

/**
 * Check for any pending writes that need to be saved
 * @returns Number of elements with unsaved changes
 */
const checkForPendingWrites = (): number => {
  if (!configService.isFeatureEnabled('enableLocalStorage')) {
    return 0;
  }
  
  const pendingWrites = document.querySelectorAll('[data-unsaved-changes="true"]');
  if (pendingWrites.length > 0) {
    logger.warn('Unsaved changes detected during application cleanup', { 
      elementsCount: pendingWrites.length
    });
  }
  
  return pendingWrites.length;
};

/**
 * Detect system capabilities for feature adaptation
 */
export const detectCapabilities = (): Record<string, boolean> => {
  const capabilities = {
    webGL: false,
    webGL2: false,
    webWorkers: false,
    localStorage: false,
    sessionStorage: false,
    indexedDB: false,
    webSockets: false,
    webRTC: false,
    serviceWorkers: false,
  };
  
  try {
    // Check WebGL support
    detectWebGLSupport(capabilities);
    
    // Check Web Workers support
    capabilities.webWorkers = !!window.Worker;
    
    // Check storage support
    detectStorageSupport(capabilities);
    
    // Check WebSockets support
    capabilities.webSockets = !!window.WebSocket;
    
    // Check WebRTC support
    capabilities.webRTC = !!(window.RTCPeerConnection || 
      window.webkitRTCPeerConnection || 
      window.mozRTCPeerConnection);
    
    // Check Service Workers support
    capabilities.serviceWorkers = !!navigator.serviceWorker;
    
    logger.info('System capabilities detected', capabilities);
  } catch (error) {
    logger.error('Error detecting system capabilities', { 
      error: error instanceof Error ? error.message : String(error) 
    });
  }
  
  return capabilities;
};

/**
 * Detect WebGL support
 */
const detectWebGLSupport = (capabilities: Record<string, boolean>): void => {
  try {
    const canvas = document.createElement('canvas');
    capabilities.webGL = !!window.WebGLRenderingContext && 
      !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
    capabilities.webGL2 = !!window.WebGL2RenderingContext && 
      !!(canvas.getContext('webgl2'));
  } catch (error) {
    logger.warn('Error checking WebGL support', { error });
  }
};

/**
 * Detect storage APIs support
 */
const detectStorageSupport = (capabilities: Record<string, boolean>): void => {
  try {
    // We use a function to safely check for storage APIs
    const checkStorage = (storageType: 'localStorage' | 'sessionStorage'): boolean => {
      try {
        const storage = window[storageType];
        const testKey = `__test_${Date.now()}`;
        storage.setItem(testKey, testKey);
        storage.removeItem(testKey);
        return true;
      } catch (e) {
        return false;
      }
    };
    
    capabilities.localStorage = checkStorage('localStorage');
    capabilities.sessionStorage = checkStorage('sessionStorage');
    capabilities.indexedDB = !!window.indexedDB;
  } catch (error) {
    logger.warn('Error checking storage support', { error });
  }
};

/**
 * Preload essential assets for better performance
 */
export const preloadAssets = async (): Promise<void> => {
  logger.info('Preloading essential assets');
  
  const preloadImages = [
    '/logo.png',
    '/background.jpg',
    '/icons/dashboard.svg',
    '/icons/settings.svg',
    '/icons/monitoring.svg',
  ];
  
  try {
    const results = await Promise.allSettled(
      preloadImages.map(src => preloadImage(src))
    );
    
    const succeeded = results.filter(result => result.status === 'fulfilled').length;
    const failed = results.filter(result => result.status === 'rejected').length;
    
    logger.info('Assets preloaded', { 
      total: preloadImages.length,
      succeeded,
      failed
    });
  } catch (error) {
    logger.error('Error preloading assets', { 
      error: error instanceof Error ? error.message : String(error)
    });
  }
};

/**
 * Preload a single image
 */
const preloadImage = (src: string): Promise<void> => {
  return new Promise<void>((resolve, reject) => {
    const img = new Image();
    
    img.onload = () => resolve();
    img.onerror = () => {
      logger.warn(`Failed to preload image: ${src}`);
      reject(new Error(`Failed to load image: ${src}`));
    };
    
    img.src = src;
  });
};

// Initialize and export main functions
export default {
  initializeApp,
  monitorPerformance,
  cleanupApp,
  detectCapabilities,
  preloadAssets,
};
