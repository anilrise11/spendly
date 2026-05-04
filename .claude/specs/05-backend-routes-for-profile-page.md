# Spec: Backend Routes for Profile Page

## Overview
Add the ability for logged-in users to update their profile information and change their password. Step 4 built the read-only profile dashboard; this step adds the write side — a GET/POST pair at `/profile/edit` that lets users update their name and email, and a separate POST at `/profile/password` for changing their password. Both routes follow the same auth-guard pattern established in Step 4.

## Depends on
- Step 1 — Database setup (`users` table must exist)
- Step 2 — Registration (user accounts must exist)
- Step 3 — Login/Logout (session `user_id` must be set)
- Step 4 — Profile page design (`profile.html` and profile CSS classes must exist)

## Routes
- `GET /profile/edit` — render the edit-profile form pre-filled with current name and email — logged-in only
- `POST /profile/edit` — process name/email update, write to DB, redirect back to `/profile` — logged-in only
- `POST /profile/password` — process password change (current + new + confirm), update DB — logged-in only

## Database changes
No new tables or columns. All writes go to the existing `users` table:
- Name/email update: `UPDATE users SET name = ?, email = ? WHERE id = ?`
- Password change: `UPDATE users SET password_hash = ? WHERE id = ?`

## Templates
- **Create:** `templates/profile_edit.html` — edit form extending `base.html`
- **Modify:** `templates/profile.html` — add an "Edit Profile" link/button pointing to `/profile/edit`

## Files to change
- `app.py` — add three route handlers: `GET /profile/edit`, `POST /profile/edit`, `POST /profile/password`
- `templates/profile.html` — add "Edit Profile" button in the profile header action area
- `static/css/style.css` — add CSS for the edit form layout

## Files to create
- `templates/profile_edit.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw SQL via `get_db()`
- Parameterised queries only — never interpolate values into SQL strings
- Passwords hashed with werkzeug `generate_password_hash`; verified with `check_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Auth guard on every route: if `session.get('user_id')` is falsy, redirect to `/login`
- Close every DB connection in a `finally` block
- After a successful name/email update, refresh `session['user_name']` so the navbar shows the new name immediately
- Email uniqueness: catch `sqlite3.IntegrityError` on update and render the form again with an error message
- Password change must verify the current password before writing a new hash
- New password must be at least 8 characters; new password and confirm must match
- Flash a success message on successful update, then redirect to `/profile`
- Never expose or echo `password_hash` to any template

## Edit Profile form layout (profile_edit.html)

```
[Page header]
  ← Back to Profile          ← small link back to /profile

  Edit Profile               ← font-display heading

[Form: POST /profile/edit]
  Name        [text input, pre-filled]
  Email       [email input, pre-filled]
  [Save Changes]  button

[Divider]

[Form: POST /profile/password]
  Current Password   [password input]
  New Password       [password input, min 8 chars]
  Confirm Password   [password input]
  [Update Password]  button
```

## CSS classes to add to style.css

```
.edit-page         — outer padding wrapper matching .profile-page
.edit-inner        — max-width container, margin 0 auto
.edit-header       — margin-bottom 2rem
.edit-back         — small muted link, font-size 0.85rem, margin-bottom 0.75rem, display block
.edit-title        — font-display, 2rem, var(--ink)

.edit-section      — white card, border, border-radius var(--radius-md), padding 1.5rem 2rem, margin-bottom 1.5rem
.edit-section-title — 1rem, font-weight 600, var(--ink), margin-bottom 1.25rem, padding-bottom 0.75rem, border-bottom

.form-group        — margin-bottom 1.25rem (reuse if already defined, else create)
.form-label        — 0.85rem, font-weight 500, var(--ink), display block, margin-bottom 0.4rem
.form-input        — full-width, border, border-radius var(--radius-sm), padding 0.6rem 0.85rem, font-size 0.95rem
.form-input:focus  — outline none, border-color var(--accent), box-shadow 0 0 0 3px accent at 15% opacity
.form-error        — 0.85rem, var(--error) color, margin-top 0.35rem
.form-success      — same but var(--success) or var(--accent-green)

.btn-save          — primary button style matching existing .btn-primary (or reuse it)
```

## Definition of done
- [ ] `GET /profile/edit` without a session redirects to `/login`
- [ ] `GET /profile/edit` with a valid session renders the form pre-filled with the user's current name and email
- [ ] Submitting `POST /profile/edit` with valid data updates the name and email in the DB
- [ ] After a successful update, `session['user_name']` reflects the new name and the navbar shows it
- [ ] Submitting an email already used by another account shows an inline error (no crash)
- [ ] Submitting `POST /profile/password` with wrong current password shows an error
- [ ] Submitting `POST /profile/password` where new != confirm shows an error
- [ ] Submitting `POST /profile/password` with new password shorter than 8 chars shows an error
- [ ] A successful password change redirects to `/profile` with a flash success message
- [ ] After a password change, the user can log out and log back in with the new password
- [ ] The "Edit Profile" button/link on `profile.html` navigates to `/profile/edit`
- [ ] App starts without errors (`python app.py`)
