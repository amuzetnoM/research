/**
 * Configuration service for the Research Dashboard
 * Centralizes application configuration and environment settings
 */

import { logger } from './logger';

// Environment types
export enum Environment {
  DEVELOPMENT = 'development',
  TESTING = 'testing',
  STAGING = 'staging',
  PRODUCTION = 'production',
}

// Feature flags interface
export interface FeatureFlags {
  enableGrafanaIntegration: boolean;
  enablePrometheusDirectAccess: boolean;
  enableSelfAwareness: boolean;
  enableContainerComparison: boolean;
  enableAIAnalysis: boolean;
  enableRealTimeUpdates: boolean;
  enableLocalStorage: boolean;
  enableDarkMode: boolean;
  enableAdvancedCharts: boolean;
  enableExperimentalFeatures: boolean;
}

// Dashboard settings interface
export interface DashboardSettings {
  refreshInterval: number; // in milliseconds
  defaultTimeRange: string;
  maxDataPoints: number;
  defaultTheme: 'light' | 'dark' | 'system';
  dateFormat: string;
  timeFormat: string;
  decimalPrecision: number;
}

// Application config interface
export interface AppConfig {
  environment: Environment;
  version: string;
  buildDate: string;
  apiBaseUrl: string;
  metricsEndpoint: string;
  grafanaUrl: string;
  prometheusUrl: string;
  featureFlags: FeatureFlags;
  dashboardSettings: DashboardSettings;
  errorReportingEnabled: boolean;
  analyticsEnabled: boolean;
  logLevel: string;
  maxLogEntries: number;
  container1Url: string;
  container2Url: string;
}

// Default configuration
const defaultConfig: AppConfig = {
  environment: process.env.NODE_ENV === 'production' 
    ? Environment.PRODUCTION 
    : Environment.DEVELOPMENT,
  version: process.env.REACT_APP_VERSION || '0.1.0',
  buildDate: process.env.REACT_APP_BUILD_DATE || new Date().toISOString(),
  apiBaseUrl: '/api',
  metricsEndpoint: '/metrics',
  grafanaUrl: '/grafana',
  prometheusUrl: '/prometheus',
  featureFlags: {
    enableGrafanaIntegration: true,
    enablePrometheusDirectAccess: true,
    enableSelfAwareness: true,
    enableContainerComparison: true,
    enableAIAnalysis: true,
    enableRealTimeUpdates: true,
    enableLocalStorage: true,
    enableDarkMode: true,
    enableAdvancedCharts: true,
    enableExperimentalFeatures: process.env.NODE_ENV !== 'production',
  },
  dashboardSettings: {
    refreshInterval: 30000, // 30 seconds
    defaultTimeRange: '24h',
    maxDataPoints: 1000,
    defaultTheme: 'system',
    dateFormat: 'YYYY-MM-DD',
    timeFormat: 'HH:mm:ss',
    decimalPrecision: 2,
  },
  errorReportingEnabled: true,
  analyticsEnabled: process.env.NODE_ENV === 'production',
  logLevel: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  maxLogEntries: 1000,
  container1Url: '/api/container1',
  container2Url: '/api/container2',
};

class ConfigService {
  private config: AppConfig;
  private readonly storageKey = 'research_dashboard_config';

  constructor(initialConfig: Partial<AppConfig> = {}) {
    // Merge default config with initial config
    this.config = { ...defaultConfig, ...initialConfig };
    
    // Load saved config from localStorage
    this.loadConfigFromStorage();
    
    logger.info('ConfigService initialized', { environment: this.config.environment });
  }

  /**
   * Get full configuration
   */
  public getConfig(): AppConfig {
    return { ...this.config };
  }

  /**
   * Get specific configuration value
   */
  public get<K extends keyof AppConfig>(key: K): AppConfig[K] {
    return this.config[key];
  }

  /**
   * Get feature flag
   */
  public isFeatureEnabled(feature: keyof FeatureFlags): boolean {
    return this.config.featureFlags[feature];
  }

  /**
   * Get dashboard setting
   */
  public getSetting<K extends keyof DashboardSettings>(key: K): DashboardSettings[K] {
    return this.config.dashboardSettings[key];
  }

  /**
   * Update configuration with partial config
   */
  public update(partialConfig: Partial<AppConfig>): void {
    this.config = { ...this.config, ...partialConfig };
    this.saveConfigToStorage();
    logger.info('Configuration updated', { updatedKeys: Object.keys(partialConfig) });
  }

  /**
   * Update feature flag
   */
  public setFeatureFlag(feature: keyof FeatureFlags, enabled: boolean): void {
    this.config.featureFlags = {
      ...this.config.featureFlags,
      [feature]: enabled,
    };
    this.saveConfigToStorage();
    logger.info(`Feature flag "${feature}" set to ${enabled}`);
  }

  /**
   * Update dashboard setting
   */
  public updateSetting<K extends keyof DashboardSettings>(key: K, value: DashboardSettings[K]): void {
    this.config.dashboardSettings = {
      ...this.config.dashboardSettings,
      [key]: value,
    };
    this.saveConfigToStorage();
    logger.info(`Dashboard setting "${key}" updated`, { value });
  }

  /**
   * Reset configuration to defaults
   */
  public resetToDefaults(): void {
    this.config = { ...defaultConfig };
    this.saveConfigToStorage();
    logger.info('Configuration reset to defaults');
  }

  /**
   * Save configuration to localStorage
   */
  private saveConfigToStorage(): void {
    if (!this.config.featureFlags.enableLocalStorage) {
      return;
    }
    
    try {
      const saveableConfig = { ...this.config };
      localStorage.setItem(this.storageKey, JSON.stringify(saveableConfig));
    } catch (error) {
      logger.error('Failed to save configuration to storage', { error });
    }
  }

  /**
   * Load configuration from localStorage
   */
  private loadConfigFromStorage(): void {
    if (!this.config.featureFlags.enableLocalStorage) {
      return;
    }
    
    try {
      const storedConfig = localStorage.getItem(this.storageKey);
      if (storedConfig) {
        const parsedConfig = JSON.parse(storedConfig) as Partial<AppConfig>;
        // Only override user configurable settings
        if (parsedConfig.dashboardSettings) {
          this.config.dashboardSettings = {
            ...this.config.dashboardSettings,
            ...parsedConfig.dashboardSettings,
          };
        }
        if (parsedConfig.featureFlags) {
          // Only override non-critical feature flags
          const safeFlags = { ...parsedConfig.featureFlags };
          if (process.env.NODE_ENV === 'production') {
            safeFlags.enableExperimentalFeatures = false;
          }
          this.config.featureFlags = {
            ...this.config.featureFlags,
            ...safeFlags,
          };
        }
        logger.debug('Loaded configuration from storage');
      }
    } catch (error) {
      logger.error('Failed to load configuration from storage', { error });
    }
  }

  /**
   * Get environment-specific value
   */
  public getEnvironmentSpecific<T>(
    devValue: T,
    testValue: T,
    stagingValue: T,
    prodValue: T
  ): T {
    switch (this.config.environment) {
      case Environment.DEVELOPMENT:
        return devValue;
      case Environment.TESTING:
        return testValue;
      case Environment.STAGING:
        return stagingValue;
      case Environment.PRODUCTION:
        return prodValue;
      default:
        return devValue;
    }
  }

  /**
   * Check if running in development mode
   */
  public isDevelopment(): boolean {
    return this.config.environment === Environment.DEVELOPMENT;
  }

  /**
   * Check if running in production mode
   */
  public isProduction(): boolean {
    return this.config.environment === Environment.PRODUCTION;
  }
}

// Export singleton instance
export const configService = new ConfigService();

// Export ConfigService class for testing and extension
export default ConfigService;
