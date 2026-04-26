# Spec: Registration

## Overview
Implement the user registration flow so new visitors can create a Spendly account. This step wires the existing `register.html` form to a `POST /register` handler that validates input, hashes the password with werkzeug, inserts the user into the `users` table, and redirects to the login page on success. It also sets `app.secret_key` (required for Flask flash messages) so the success confirmation can be surfaced on the login page. Login/session creation is deferred to Step 3.

## Depends on
- Step 1 — Database setup (`get_db`, `init_db`, `seed_db` must be working and `users` table must exist)

## Routes
- `GET /register` — render registration form — public (already exists, no change)
- `POST /register` — handle form submission; validate, insert user, redirect — public

## Database changes
No new tables or columns. The `users` table created in Step 1 already has all required fields (`id`, `name`, `email`, `password_hash`, `created_at`).

## Templates
- **Modify:** `templates/register.html` — ensure the form uses `method="POST" action="/register"` (already correct); add `{{ get_flashed_messages() }}` block is NOT needed here since errors are passed via `render_template(error=...)` which already exists in the template
- **Modify:** `templates/login.html` — add a flash message banner at the top of the card to display the "Account created — please sign in" success message

## Files to change
- `app.py` — add `secret_key`, import `redirect`, `url_for`, `request`, `flash` from flask; convert `/register` to handle both GET and POST; add POST `/register` logic
- `templates/login.html` — add flash message display block

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw SQL with `get_db()`
- Parameterised queries only — never interpolate values into SQL strings
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Use CSS variables — never hardcode hex values in any template or style
- All templates extend `base.html`
- `secret_key` must be set on the Flask app before any `flash()` call works — set it to a hard-coded dev string (e.g. `"dev-secret-change-in-prod"`) directly in `app.py` for now
- On duplicate email: catch the `sqlite3.IntegrityError` and re-render the form with `error="An account with that email already exists."`
- Validation rules (re-render form with specific `error` message if violated):
  - Name: required, non-empty after strip
  - Email: required, non-empty after strip
  - Password: required, minimum 8 characters
- On success: `flash("Account created — please sign in.")` then `redirect(url_for('login'))`
- Close the DB connection in a `finally` block

## Definition of done
- [ ] `GET /register` still renders the form without errors
- [ ] Submitting the form with valid data creates a new row in `users` with a hashed password (not plaintext)
- [ ] After successful registration the browser is redirected to `/login`
- [ ] The login page shows the flash message "Account created — please sign in."
- [ ] Submitting with an email that already exists re-renders the form with an error message (no crash, no redirect)
- [ ] Submitting with a password shorter than 8 characters re-renders the form with an error message
- [ ] Submitting with an empty name re-renders the form with an error message
- [ ] The `password_hash` stored in the DB is not the raw password string
- [ ] App starts without errors (`python app.py`)
