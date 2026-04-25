# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (localhost:5001, debug mode)
python app.py

# Run tests
pytest

# Run a single test file
pytest tests/test_app.py

# Run a single test
pytest tests/test_app.py::test_name
```

## Architecture

**Spendly** is a Flask monolith with server-side rendering. No frontend framework, no build step.

### Key files
- `app.py` — all routes and Flask app config; runs on port 5001 with `debug=True`
- `database/db.py` — SQLite utilities placeholder (`get_db`, `init_db`, `seed_db` to be implemented)
- `templates/base.html` — shared layout (navbar, footer); all other templates extend this
- `static/css/style.css` — custom CSS only, no Tailwind or framework

### Routing
Routes are defined in `app.py`. Several routes (`/logout`, `/profile`, expense CRUD) are stubs awaiting implementation alongside the database layer.

### Database
Uses SQLite (`expense_tracker.db`, gitignored). The `database/db.py` module will expose `get_db()` (connection with `row_factory` and foreign keys), `init_db()`, and `seed_db()`. No ORM — raw SQL expected.

### Design system
- Fonts: DM Serif Display (headings), DM Sans (body) via Google Fonts
- Colors: ink `#0f0f0f`, paper `#f7f6f3`, accent-green `#1a472a`, accent-orange `#c17f24`
- Currency: Indian rupee (₹) throughout
