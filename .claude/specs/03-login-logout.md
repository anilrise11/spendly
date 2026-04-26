# Spec: Login and Logout

## Overview
Implement session-based authentication so registered users can sign in and sign out of Spendly. This step wires the existing `login.html` form to a `POST /login` handler that verifies credentials with werkzeug, stores the user identity in a Flask server-side session cookie, and redirects to `/profile`. It also implements `GET /logout`, which clears the session and redirects to the landing page. Finally, `base.html`'s navbar is made session-aware so logged-in users see their name and a "Sign out" link instead of the public "Sign in / Get started" links.

## Depends on
- Step 1 — Database setup (`users` table, `get_db()` must be working)
- Step 2 — Registration (user accounts must exist to log into)

## Routes
- `GET /login` — render login form — public (already exists, no change to GET)
- `POST /login` — verify credentials, set session, redirect to `/profile` — public
- `GET /logout` — clear session, redirect to `/` — logged-in (no hard guard needed yet; clearing an empty session is harmless)

## Database changes
No database changes. Reads from the existing `users` table only.

## Templates
- **Modify:** `templates/login.html` — no structural changes needed; error display already in place
- **Modify:** `templates/base.html` — update navbar to branch on `session.get('user_id')`:
  - **Logged out:** show "Sign in" and "Get started" links (current behaviour)
  - **Logged in:** show the user's name (non-clickable or linked to `/profile`) and a "Sign out" link pointing to `/logout`

## Files to change
- `app.py` — import `session` and `check_password_hash`; convert `/login` to GET+POST; implement `/logout`
- `templates/base.html` — session-aware navbar

## Files to create
No new files.

## New dependencies
No new dependencies. `check_password_hash` is already available from `werkzeug.security` (werkzeug is pinned in `requirements.txt`).

## Rules for implementation
- No SQLAlchemy or ORMs — use raw SQL with `get_db()`
- Parameterised queries only — never interpolate values into SQL strings
- Passwords verified with `werkzeug.security.check_password_hash` — never compare plaintext
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Store only `user_id` (int) and `user_name` (str) in the session — never store the password hash
- `session.permanent` does not need to be set; default session lifetime is fine for now
- On wrong credentials: re-render `login.html` with `error="Invalid email or password."` — use the same message for both bad email and bad password to avoid user enumeration
- On success: `session['user_id'] = user['id']`, `session['user_name'] = user['name']`, then `redirect(url_for('profile'))`
- Logout: `session.clear()` then `redirect(url_for('landing'))`
- Close the DB connection in a `finally` block in the login handler

## Definition of done
- [ ] `GET /login` renders the form without errors
- [ ] Signing in with `demo@spendly.com` / `demo123` sets the session and redirects to `/profile`
- [ ] Signing in with a wrong password re-renders the form with "Invalid email or password." (no redirect, no crash)
- [ ] Signing in with a non-existent email re-renders the form with the same error message
- [ ] After login, the navbar shows the user's name and a "Sign out" link (not "Sign in / Get started")
- [ ] Visiting `/logout` clears the session and redirects to `/`
- [ ] After logout, the navbar reverts to showing "Sign in" and "Get started"
- [ ] Refreshing the page after login keeps the user logged in (session persists across requests)
- [ ] App starts without errors (`python app.py`)
