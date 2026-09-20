# Contributing to TwinQ-Map

Thank you for contributing to TwinQ-Map! Please adhere to the following developer guidelines.

## 1. Code Quality & Linting
- All python code must comply with PEP8 standards.
- Run linters before submitting a Pull Request:
  ```bash
  flake8 backend/
  ```

## 2. Testing Protocols
- Ensure that any new feature includes complete unit or integration tests under `backend/tests/`.
- Ensure all tests execute successfully before pushing code:
  ```bash
  pytest backend/tests/
  ```

## 3. Pull Request Guidelines
1. Fork the repository and create your branch from `main`.
2. Document all mathematical equations introduced.
3. Ensure no placeholder TODO comments are included.
