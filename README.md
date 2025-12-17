# OWASP Juice Shop Solver

Python solver for OWASP Juice Shop challenges.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Usage

```bash
python solutions.py
```

## Structure

- `solutions.py` - Main entry point
- `authentication.py` - Login/session management
- `users.py` - User-related challenges
- `products.py` - Product-related challenges  
- `misc.py` - Miscellaneous challenges
- `feedback.py` - Feedback challenges
- `filehandling.py` - File upload challenges
- `advanced.py` - Advanced challenges
- `browser.py` - Browser automation challenges

## Server Configuration

Default server: `http://localhost:3000`

Edit `solutions.py` to change server URL.
