# COMPASS Ethical Framework

## Overview

COMPASS is a modular, real-time ethical reasoning and governance framework for AI systems, implementing:

- Ethical Reasoning Engine
- Ethical Constraint Enforcement
- Monitoring & Feedback Loops
- Governance & Oversight
- Transparency & Explainability

## Usage

1. **Run the API:**
   ```
   python -m frameworks.ethics.compass_api
   ```

2. **API Endpoints:**
   - `GET /api/compass/info` — Framework info and directives
   - `POST /api/compass/decide` — Submit actions and context, receive ethical decision and explanation
   - `GET /api/compass/logs` — Retrieve decision logs
   - `GET /api/compass/metrics` — Retrieve monitoring metrics

3. **Integration:**
   - Import `COMPASSFramework` in your Python code for direct use.
   - Use the REST API for language-agnostic integration.

## Deployment

- Requires Python 3.8+, Flask, flask-cors.
- Designed for containerized and cloud-native deployment.
- All decisions and actions are logged and explainable.
