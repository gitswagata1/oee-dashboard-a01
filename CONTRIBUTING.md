# Contributing to OEE Dashboard

Thanks for your interest in contributing!

## Getting Started

### Prerequisites

- Python 3.10+

### Development Setup

```bash
# Fork and clone
git clone https://github.com/<your-username>/oee-dashboard-a01.git
cd oee-dashboard-a01

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run the dashboard
streamlit run app.py
```

The dashboard opens at `http://localhost:8501` with sample data from Cell A01.

## How to Contribute

### Reporting Bugs

1. Check [existing issues](https://github.com/gitswagata1/oee-dashboard-a01/issues) first
2. Use the **Bug Report** issue template
3. Include steps to reproduce, expected vs. actual behavior, and your environment

### Suggesting Features

1. Open an issue using the **Feature Request** template
2. Describe the problem it solves and the proposed solution

### Submitting Code

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/my-feature
   ```
3. **Make your changes** — keep commits focused and atomic
4. **Lint** your code: `make lint`
5. **Push** and open a Pull Request against `main`

## Coding Standards

- Follow [PEP 8](https://peps.python.org/pep-0008/) style
- Add type hints to function signatures
- Use `@st.cache_data` for expensive computations
- Keep Plotly chart functions self-contained

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `refactor:` code restructuring

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
