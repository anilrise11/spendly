# Spec: Profile Page Design

## Overview
Implement the authenticated profile dashboard so logged-in users land on a meaningful page after signing in. The `/profile` route currently returns a plain-text stub; this step replaces it with a full server-rendered page that shows the user's account info, four summary stat tiles (total spend, this month's spend, transaction count, and top category), and a table of their ten most recent expenses. It also introduces an authentication guard pattern — unauthenticated visitors are redirected to `/login` — which all future protected routes will follow.

## Depends on
- Step 1 — Database setup (`get_db`, `users` and `expenses` tables must exist)
- Step 2 — Registration (user accounts must exist)
- Step 3 — Login/Logout (session must be set correctly: `session['user_id']` and `session['user_name']`)

## Routes
- `GET /profile` — render the profile dashboard — logged-in only (redirect to `/login` if no session)

## Database changes
No database changes. Reads from the existing `users` and `expenses` tables only.

## Templates
- **Create:** `templates/profile.html` — full profile dashboard extending `base.html`
- **Modify:** none

## Files to change
- `app.py` — replace the `/profile` stub with a real handler: auth guard, DB queries, render `profile.html`
- `static/css/style.css` — add CSS classes for the profile layout (page wrapper, stat tiles, expense table)

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw SQL via `get_db()`
- Parameterised queries only — never interpolate values into SQL strings
- Passwords hashed with werkzeug (no change needed here, just don't expose `password_hash`)
- Use CSS variables — never hardcode hex values in templates or styles
- All templates extend `base.html`
- Auth guard: if `session.get('user_id')` is falsy, `redirect(url_for('login'))`
- Close every DB connection in a `finally` block, or use a single connection for all queries then close once
- Currency must display in Indian rupees (₹) throughout
- Amounts must be formatted with a thousands separator (e.g. ₹1,200.00) — use Jinja2's `'{:,.2f}'.format(amount)` or a template filter
- The "this month" window must be computed dynamically from today's date (`datetime.date.today()`) so it stays correct as months turn over — do NOT hardcode the year/month string
- The recent expenses table must show: date, category, description (or "—" if null), and amount
- Categories must use a fixed colour dot for visual scanning (map the 7 known categories to distinct CSS classes)
- The profile page must be reachable via the Spendly logo / nav brand link when logged in, or the navbar must link the user name to `/profile`
- Do not show expense data from other users — always filter by `session['user_id']`

## Queries to implement in the route
Run all four against the authenticated user's ID:

1. **User row** — `SELECT id, name, email, created_at FROM users WHERE id = ?`
2. **All-time total** — `SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ?`
3. **This-month total** — `SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ? AND strftime('%Y-%m', date) = ?` (pass the current `YYYY-MM` string as the second `?`)
4. **Top category** — `SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC LIMIT 1`
5. **Transaction count** — `SELECT COUNT(*) FROM expenses WHERE user_id = ?`
6. **Recent 10 expenses** — `SELECT id, date, category, description, amount FROM expenses WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT 10`

## Profile page layout (profile.html)

```
[Page header]
  ◈  Welcome back, {name}         ← font-display
     Member since {created_at}    ← muted subtitle

[Stat tiles — 4 column grid]
  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
  │ Total Spend  │ │  This Month  │ │ Transactions │ │ Top Category │
  │  ₹X,XXX.00  │ │  ₹X,XXX.00  │ │     N        │ │   Shopping   │
  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘

[Recent Expenses]
  Heading: "Recent Expenses"
  Table:
    Date        Category    Description          Amount
    2026-04-22  Food        Restaurant dinner    ₹350.00
    …
  (10 rows max; if no expenses: show a friendly empty state)

[Quick action]
  "+ Add Expense" button → href="/expenses/add" (stub route, already defined)
```

## CSS classes to add to style.css

```
.profile-page          — outer padding wrapper (4rem 2rem)
.profile-inner         — max-width container (var(--max-width)), margin 0 auto
.profile-header        — flex row, space-between, align center, margin-bottom 2.5rem
.profile-header-info   — flex column, gap 0.25rem
.profile-title         — font-display, 2rem, var(--ink)
.profile-subtitle      — 0.9rem, var(--ink-muted)
.profile-header-action — (holds the add-expense CTA)

.stat-grid             — CSS grid, 4 columns, gap 1rem, margin-bottom 2.5rem
.stat-card             — white card, border, border-radius var(--radius-md), padding 1.25rem 1.5rem
.stat-label            — 0.8rem, var(--ink-muted), margin-bottom 0.35rem
.stat-value            — font-display, 1.75rem, var(--ink)
.stat-value-sm         — (for transaction count & category name) 1.5rem

.section-heading       — 1rem, font-weight 600, var(--ink), margin-bottom 1rem
.expense-table-wrap    — white card, border, border-radius var(--radius-md), overflow hidden
.expense-table         — full-width table, border-collapse collapse
.expense-table th      — 0.8rem uppercase, var(--ink-muted), padding 0.75rem 1.25rem, border-bottom
.expense-table td      — 0.9rem, var(--ink-soft), padding 0.75rem 1.25rem, border-bottom (last row: no border)
.expense-table tr:hover — background var(--paper)

.category-dot          — inline-block, 8×8px circle, margin-right 0.4rem
.cat-food              — background: a warm amber
.cat-transport         — background: a steel blue
.cat-bills             — background: a muted red
.cat-health            — background: a teal/green
.cat-entertainment     — background: a purple
.cat-shopping          — background: var(--accent-2) (orange)
.cat-other             — background: var(--ink-faint)

.empty-state           — text-align center, padding 3rem, var(--ink-muted), font-size 0.95rem
```

## Definition of done
- [ ] `GET /profile` without a session redirects to `/login`
- [ ] `GET /profile` with a valid session renders the profile page (no crash, no stub text)
- [ ] The page header shows the logged-in user's name and their `created_at` date
- [ ] All four stat tiles display correct values for the demo user (`demo@spendly.com`)
- [ ] "This Month" total reflects only April 2026 expenses for demo user (₹800 Food + ₹120 Transport + ₹1,200 Bills + ₹800 Health + ₹600 Entertainment + ₹2,500 Shopping + ₹300 Other + ₹350 Food = ₹6,670.00)
- [ ] The recent expenses table lists up to 10 rows ordered newest-first
- [ ] Amounts display with ₹ prefix and two decimal places with thousands separator
- [ ] Each category row shows the correct coloured dot
- [ ] Visiting `/profile` as a freshly-registered user with no expenses shows the empty state (no crash)
- [ ] The "+ Add Expense" button is visible and links to `/expenses/add`
- [ ] App starts without errors (`python app.py`)
- [ ] No other user's expenses are visible (data is always filtered by `session['user_id']`)
