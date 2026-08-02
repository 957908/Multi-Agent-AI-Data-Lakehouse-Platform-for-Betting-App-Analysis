# 👩‍💻 SentinelX Trust AI — Developer Onboarding Guide

**Version:** 1.0.0  

---

## 🛠️ Local Environment Setup

1. **Clone & Virtual Environment:**
   ```bash
   git clone https://github.com/957908/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis.git
   cd Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r backend/app/requirements.txt
   ```

3. **Run Unit & Integration Test Suite:**
   ```bash
   python -m unittest backend/tests/test_ai_services.py backend/tests/test_api.py backend/tests/test_full_integration.py backend/tests/run_e2e_simulation.py backend/tests/benchmark_performance.py
   ```

4. **Start REST API Server:**
   ```bash
   python backend/app/server.py
   ```

---

## 🌿 Git Branching Workflow

- **`main`**: Production stable release branch.
- **`develop`**: Integration branch for upcoming sprint deliverables.
- **Feature Branches:** `feature/<engineer-name>-<feature-description>`
- **Docs Branches:** `docs/<sprint-name>`

### Commit Conventions
- `feat(backend): add Gold layer REST API router`
- `fix(ai): update trust engine default score fallback`
- `docs(api): update OpenAPI endpoints reference`
- `test(integration): add E2E data lifecycle simulation`
