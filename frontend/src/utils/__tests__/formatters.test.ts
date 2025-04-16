import { 
  formatNumber, 
  formatPercentage, 
  formatBytes, 
  formatTimeAgo,
  formatDate,
  formatDateTime,
  formatDuration
} from '../formatters';

describe('formatters', () => {
  describe('formatNumber', () => {
    test('should format numbers with default options', () => {
      expect(formatNumber(1000)).toBe('1,000');
      expect(formatNumber(1000.5)).toBe('1,000.5');
    });
    
    test('should format numbers with custom options', () => {
      expect(formatNumber(1000, { maximumFractionDigits: 0 })).toBe('1,000');
      expect(formatNumber(1000.5, { maximumFractionDigits: 0 })).toBe('1,001');
      expect(formatNumber(0.5, { style: 'percent' })).toBe('50%');
      expect(formatNumber(1000, { style: 'currency', currency: 'USD' })).toBe('$1,000.00');
    });
  });
  
  describe('formatPercentage', () => {
    test('should format numbers as percentages', () => {
      expect(formatPercentage(50)).toBe('50.0%');
      expect(formatPercentage(50.55)).toBe('50.6%');
      expect(formatPercentage(50, 0)).toBe('50%');
      expect(formatPercentage(50.55, 2)).toBe('50.55%');
    });
  });
  
  describe('formatBytes', () => {
    test('should format bytes with appropriate units', () => {
      expect(formatBytes(0)).toBe('0 Bytes');
      expect(formatBytes(1023)).toBe('1023 Bytes');
      expect(formatBytes(1024)).toBe('1 KB');
      expect(formatBytes(1024 * 1024)).toBe('1 MB');
      expect(formatBytes(1024 * 1024 * 1024)).toBe('1 GB');
      expect(formatBytes(1536 * 1024)).toBe('1.5 MB');
    });
    
    test('should respect decimal places parameter', () => {
      expect(formatBytes(1536 * 1024, 0)).toBe('2 MB');
      expect(formatBytes(1536 * 1024, 1)).toBe('1.5 MB');
      expect(formatBytes(1536 * 1024, 3)).toBe('1.500 MB');
    });
  });
  
  describe('formatTimeAgo', () => {
    test('should format time differences in seconds', () => {
      const now = new Date();
      const seconds10Ago = new Date(now.getTime() - 10 * 1000);
      expect(formatTimeAgo(seconds10Ago)).toBe('10 seconds ago');
      
      const second1Ago = new Date(now.getTime() - 1 * 1000);
      expect(formatTimeAgo(second1Ago)).toBe('1 second ago');
    });
    
    test('should format time differences in minutes', () => {
      const now = new Date();
      const minutes10Ago = new Date(now.getTime() - 10 * 60 * 1000);
      expect(formatTimeAgo(minutes10Ago)).toBe('10 minutes ago');
      
      const minute1Ago = new Date(now.getTime() - 1 * 60 * 1000);
      expect(formatTimeAgo(minute1Ago)).toBe('1 minute ago');
    });
    
    test('should format time differences in hours', () => {
      const now = new Date();
      const hours10Ago = new Date(now.getTime() - 10 * 60 * 60 * 1000);
      expect(formatTimeAgo(hours10Ago)).toBe('10 hours ago');
      
      const hour1Ago = new Date(now.getTime() - 1 * 60 * 60 * 1000);
      expect(formatTimeAgo(hour1Ago)).toBe('1 hour ago');
    });
    
    test('should format time differences in days', () => {
      const now = new Date();
      const days2Ago = new Date(now.getTime() - 2 * 24 * 60 * 60 * 1000);
      expect(formatTimeAgo(days2Ago)).toBe('2 days ago');
      
      const day1Ago = new Date(now.getTime() - 1 * 24 * 60 * 60 * 1000);
      expect(formatTimeAgo(day1Ago)).toBe('1 day ago');
    });
  });
  
  describe('formatDate', () => {
    test('should format date to ISO format', () => {
      const date = new Date('2023-01-15T12:30:45Z');
      expect(formatDate(date)).toBe('2023-01-15');
    });
  });
  
  describe('formatDateTime', () => {
    test('should format date and time', () => {
      // This test is locale-dependent, so just check that it returns a string
      const date = new Date('2023-01-15T12:30:45Z');
      expect(typeof formatDateTime(date)).toBe('string');
      expect(formatDateTime(date).length).toBeGreaterThan(0);
    });
  });
  
  describe('formatDuration', () => {
    test('should format durations appropriately', () => {
      expect(formatDuration(500)).toBe('0s');
      expect(formatDuration(1500)).toBe('1s');
      expect(formatDuration(60 * 1000 + 30 * 1000)).toBe('1m 30s');
      expect(formatDuration(2 * 60 * 60 * 1000 + 30 * 60 * 1000)).toBe('2h 30m');
      expect(formatDuration(2 * 24 * 60 * 60 * 1000 + 5 * 60 * 60 * 1000)).toBe('2d 5h');
    });
  });
});
