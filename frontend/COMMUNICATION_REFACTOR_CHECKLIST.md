# Communication Architecture Refactor & DataService Abstraction Checklist

## 1. Audit & Clean Up Communication Code
- [x] Identify all protocol usage (WebSockets, REST, SSE, SSH) in frontend services and hooks
- [x] Remove or isolate unnecessary WebSocket code (unless for real-time collaboration)
- [x] Refactor metrics/dashboard updates to use REST (polling) or SSE

## 2. Fix Module Exports & Imports
- [ ] Ensure all UI components (Card, Button, etc.) are properly exported/imported
- [ ] Ensure all services are properly exported/imported
- [ ] Remove dead code and unused WebSocket utilities
- [ ] Standardize service exports (barrel files where appropriate)

## 3. Abstract the Communication Layer
- [ ] Design and scaffold `dataService` (or `serviceEngine`) module
- [ ] Implement protocol routing (REST, SSE, WebSocket) in dataService
- [ ] Integrate context protocol (MCP or similar) for HTML/data fetching
- [ ] Add configuration for protocol selection per feature/module

## 4. Standardize Protocol Usage by Feature
- [ ] Map each feature/module to its protocol in dataService
- [ ] Update all feature modules to use dataService abstraction

## 5. Document the Architecture
- [ ] Add/Update section in technical_architecture.md (or new communication_architecture.md)
- [ ] Document unified data service layer and protocol mapping
- [ ] Document context protocol integration
- [ ] Add summary table for protocol usage

## 6. Test & Validate
- [ ] Test all features for correct protocol usage and performance
- [ ] Validate fallback and error handling

## 7. Backend Coordination (Optional)
- [ ] Ensure backend endpoints support REST and SSE for all relevant data
- [ ] Add/validate context protocol endpoints

---

_This checklist will be updated as we progress through each step of the refactor and abstraction process._
