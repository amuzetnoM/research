# Communication Architecture Refactor & DataService Abstraction Checklist

## 1. Audit & Clean Up Communication Code
- [x] Identify all protocol usage (WebSockets, REST, SSE, SSH) in frontend services and hooks
- [x] Remove or isolate unnecessary WebSocket code (unless for real-time collaboration)
- [x] Refactor metrics/dashboard updates to use REST (polling) or SSE

## 2. Fix Module Exports & Imports
- [x] Ensure all UI components (Card, Button, etc.) are properly exported/imported
- [x] Ensure all services are properly exported/imported
- [x] Remove dead code and unused WebSocket utilities
- [x] Standardize service exports (barrel files where appropriate)

## 3. Abstract the Communication Layer
- [x] Design and scaffold `dataService` (or `serviceEngine`) module
- [x] Implement protocol routing (REST, SSE, WebSocket) in dataService
- [x] Integrate context protocol (MCP or similar) for HTML/data fetching
- [x] Add configuration for protocol selection per feature/module

## 4. Standardize Protocol Usage by Feature
- [x] Map each feature/module to its protocol in dataService
- [x] Update all feature modules to use dataService abstraction
- [x] Refactor monitoringService to use dataService
- [x] Update metrics hooks to use the dataService abstraction
- [x] Implement dashboard-specific hooks with dataService

## 5. Document the Architecture
- [x] Add/Update section in technical_architecture.md (or new communication_architecture.md)
- [x] Document unified data service layer and protocol mapping
- [x] Document context protocol integration
- [x] Add summary table for protocol usage
- [x] Create dataService usage guide for developers
- [x] Update audit report to reflect integration improvements

## 6. Test & Validate
- [ ] Test all features for correct protocol usage and performance
- [ ] Write unit tests for dataService
- [ ] Create integration tests for service interactions
- [ ] Implement E2E tests for critical user flows

## 7. Performance Optimization
- [x] Implement request caching in dataService
  - [x] Configure TTL-based caching for read-only endpoints
  - [x] Add cache invalidation for write operations
  - [x] Implement stale-while-revalidate strategy
- [x] Add request debouncing for frequently called endpoints
  - [x] Implement for search and filter operations
  - [x] Configure customizable debounce intervals
- [x] Set up data prefetching for common user flows
  - [x] Add prefetching for dashboard widgets
  - [x] Implement lazy loading for visualization data
- [x] Add performance tracking for API calls
  - [x] Integrate with app performance monitoring
  - [x] Add timing metrics for all service requests
  - [x] Track request/response sizes
- [x] Set up error logging for failed requests
  - [x] Implement centralized error handler in dataService
  - [x] Add retry mechanism with exponential backoff
  - [x] Log detailed error context information

## 8. Backend Coordination (Optional)
- [x] Ensure backend endpoints support REST and SSE for all relevant data
  - [x] Verify REST endpoints for metrics and monitoring
  - [x] Implement SSE endpoints for real-time updates
  - [x] Add proper error handling for all endpoints
- [x] Add/validate context protocol endpoints
  - [x] Implement MCP session management endpoints
  - [x] Set up model interaction endpoints
  - [x] Configure system information endpoints
  - [x] Test with frontend dataService integration

---

_This checklist will be updated as we progress through each step of the refactor and abstraction process._
