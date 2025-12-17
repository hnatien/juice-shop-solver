# OWASP Juice Shop Solver

This is an automated solver for the OWASP Juice Shop challenges.

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [Google Chrome](https://www.google.com/chrome/) (for browser-based challenges)
- A running instance of OWASP Juice Shop (default: `http://localhost:3000`)

## Setup & Run

Open your terminal (PowerShell or Command Prompt) in this directory and run the following commands:

```powershell
# 1. Create a virtual environment
# 1. Create a virtual environment
# Note: Use 'py' on Windows to ensure the official Python is used, avoiding conflicts with MinGW/Mysys64 versions.
py -m venv .venv

# 2. Activate the virtual environment
.\.venv\Scripts\Activate.ps1
# OR (if using Command Prompt):
# .\.venv\Scripts\activate.bat

# 3. Install dependencies
pip install requests selenium pyyaml hashids

# 4. Run the solver
python solutions.py
```

The solver will automatically attempt to solve all implemented challenges against the target server.
