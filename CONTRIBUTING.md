# 🤝 Contributing to SentinelX Trust AI

Thank you for your interest in contributing to **SentinelX Trust AI**!

---

## 📜 Code of Conduct & Guidelines

1. **Keep Code Decoupled:** Maintain separation between Data Acquisition (`scrapers/`), Lakehouse ETL (`etl/`), REST API (`backend/app/api/`), AI Services (`backend/app/services/ai/`), and DevOps configurations.
2. **Preserve Response Envelopes:** All new REST endpoints must return payloads wrapped in `APIResponse[T]`.
3. **Add Tests:** Every new endpoint, service class, or helper function must include unit or integration tests in `backend/tests/`.
4. **Update Documentation:** Any change to schemas, endpoints, environment variables, or architecture must be updated in `docs/`.

---

## 🌿 How to Submit a Pull Request

1. **Fork & Branch:** Create a feature branch off `develop`:
   ```bash
   git checkout -b feature/your-name-feature-description
   ```
2. **Commit Changes:** Use semantic commit messages (`feat:`, `fix:`, `docs:`, `test:`).
3. **Verify Tests:** Ensure all unit & integration tests pass cleanly:
   ```bash
   python -m unittest discover -s backend/tests -p "test_*.py"
   ```
4. **Open Pull Request:** Open a PR targeting the `develop` branch with a summary of changes and verification evidence.
