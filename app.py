import datetime
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import get_db, init_db, seed_db

app = Flask(__name__)
app.secret_key = "dev-secret-change-in-prod"


@app.template_filter('rupees')
def rupees_filter(amount):
    return f"₹{amount:,.2f}"


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    if session.get('user_id'):
        return redirect(url_for('profile'))
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get('user_id'):
        return redirect(url_for('profile'))

    if request.method == "GET":
        return render_template("register.html")

    name     = request.form.get("name", "").strip()
    email    = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not name:
        return render_template("register.html", error="Name is required.")
    if not email:
        return render_template("register.html", error="Email is required.")
    if len(password) < 8:
        return render_template("register.html", error="Password must be at least 8 characters.")

    password_hash = generate_password_hash(password)

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return render_template("register.html", error="An account with that email already exists.")
    finally:
        conn.close()

    flash("Account created — please sign in.")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get('user_id'):
        return redirect(url_for('profile'))

    if request.method == "GET":
        return render_template("login.html")

    email    = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id, name, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    finally:
        conn.close()

    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid email or password.")

    session["user_id"]   = user["id"]
    session["user_name"] = user["name"]
    return redirect(url_for("profile"))


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session['user_id']
    current_month = datetime.date.today().strftime('%Y-%m')
    month_label   = datetime.date.today().strftime('%B %Y')

    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        total_spend = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]

        month_spend = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses "
            "WHERE user_id = ? AND strftime('%Y-%m', date) = ?",
            (user_id, current_month)
        ).fetchone()[0]

        tx_count = conn.execute(
            "SELECT COUNT(*) FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]

        top_cat_row = conn.execute(
            "SELECT category FROM expenses WHERE user_id = ? "
            "GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            (user_id,)
        ).fetchone()
        top_category = top_cat_row[0] if top_cat_row else None

        recent_expenses = conn.execute(
            "SELECT id, date, category, description, amount "
            "FROM expenses WHERE user_id = ? "
            "ORDER BY date DESC, id DESC LIMIT 10",
            (user_id,)
        ).fetchall()
    finally:
        conn.close()

    return render_template(
        "profile.html",
        user=user,
        total_spend=total_spend,
        month_spend=month_spend,
        tx_count=tx_count,
        top_category=top_category,
        recent_expenses=recent_expenses,
        month_label=month_label,
    )


@app.route("/profile/edit")
def edit_profile():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (session['user_id'],)
        ).fetchone()
    finally:
        conn.close()
    return render_template("profile_edit.html", user=user)


@app.route("/profile/edit", methods=["POST"])
def update_profile():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    name  = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    if not name:
        return render_template("profile_edit.html", user={"name": name, "email": email},
                               profile_error="Name is required.")
    if not email:
        return render_template("profile_edit.html", user={"name": name, "email": email},
                               profile_error="Email is required.")
    conn = get_db()
    try:
        conn.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            (name, email, session['user_id'])
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return render_template("profile_edit.html", user={"name": name, "email": email},
                               profile_error="That email is already in use.")
    finally:
        conn.close()
    session['user_name'] = name
    flash("Profile updated.", "success")
    return redirect(url_for('profile'))


@app.route("/profile/password", methods=["POST"])
def update_password():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT name, email, password_hash FROM users WHERE id = ?",
            (session['user_id'],)
        ).fetchone()
    finally:
        conn.close()
    current = request.form.get("current_password", "")
    new_pw  = request.form.get("new_password", "")
    confirm = request.form.get("confirm_password", "")
    if not check_password_hash(user["password_hash"], current):
        return render_template("profile_edit.html", user=user,
                               password_error="Current password is incorrect.")
    if len(new_pw) < 8:
        return render_template("profile_edit.html", user=user,
                               password_error="New password must be at least 8 characters.")
    if new_pw != confirm:
        return render_template("profile_edit.html", user=user,
                               password_error="Passwords do not match.")
    conn = get_db()
    try:
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (generate_password_hash(new_pw), session['user_id'])
        )
        conn.commit()
    finally:
        conn.close()
    flash("Password updated.", "success")
    return redirect(url_for('profile'))


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


with app.app_context():
    init_db()
    seed_db()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
