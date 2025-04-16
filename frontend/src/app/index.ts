/**
 * Main application entry point
 * Configures and bootstraps the application
 */

import { initializeApp, monitorPerformance, detectCapabilities, preloadAssets, cleanupApp } from './initializer';
import { logger } from '@utils/logger';

/**
 * Bootstrap the application
 */
export async function bootstrap(): Promise<void> {
  try {
    // Initialize core services
    initializeApp();
    
    // Detect system capabilities
    const capabilities = detectCapabilities();
    
    // Preload essential assets
    await preloadAssets();
    
    // Add event listeners for cleanup
    window.addEventListener('beforeunload', cleanupApp);
    
    // Set up performance monitoring
    window.addEventListener('load', () => {
      setTimeout(() => {
        monitorPerformance();
      }, 0);
    });
    
    logger.info('Application bootstrapped successfully');
    return Promise.resolve();
  } catch (error) {
    logger.error('Failed to bootstrap application', { error });
    return Promise.reject(error);
  }
}

// Export key application functions
export { 
  initializeApp,
  monitorPerformance,
  detectCapabilities,
  preloadAssets,
  cleanupApp
};

export default { bootstrap };
