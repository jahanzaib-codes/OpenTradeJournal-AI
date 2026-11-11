# 🤝 Contributing to OpenTradeJournal-AI

Thank you for your interest in contributing to **OpenTradeJournal-AI**! We welcome contributions from quantitative developers, algorithmic traders, and behavioral finance researchers.

## 📋 Code of Conduct
We are dedicated to providing a respectful, professional, and harassment-free experience for everyone.

## 🛠️ Development Setup
1. **Fork and Clone:**
   ```bash
   git clone https://github.com/<your-username>/OpenTradeJournal-AI.git
   cd OpenTradeJournal-AI
   ```
2. **Environment Setup:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Branching Model:**
   * Feature branch: `feature/your-feature-name`
   * Bug fix: `fix/issue-description`
   * New parser: `parser/broker-name`

## 📏 Code Style Guidelines
* Follow **PEP 8** style conventions.
* Include strict docstrings and typing annotations (`typing.List`, `typing.Optional`, etc.).
* Verify linting before opening a PR: `flake8 . --count --select=E9,F63,F7,F82`.

## 🚀 Pull Request Process
1. Test your broker parser or analytics metric against sample statements.
2. Update technical documentation in `README.md` and document changes in `CHANGELOG.md`.
3. Submit your PR against `main`.
