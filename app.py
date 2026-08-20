from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import pickle
import pandas as pd
import numpy as np
from datetime import datetime

app = Flask(__name__)

app.secret_key = "carpredict_secret_key_2026"

DATABASE = "carpredict.db"
MODEL_PATH = os.path.join("model", "car_price_model.pkl")


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            present_price REAL NOT NULL,
            kms_driven REAL NOT NULL,
            fuel_type TEXT NOT NULL,
            seller_type TEXT NOT NULL,
            transmission TEXT NOT NULL,
            owner INTEGER NOT NULL,
            predicted_price REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# MODEL
# =========================================================

model = None

if os.path.exists(MODEL_PATH):
    try:
        with open(MODEL_PATH, "rb") as file:
            model = pickle.load(file)
        print("Car price ML model loaded successfully.")
    except Exception as e:
        print("Model loading error:", e)


def predict_car_price(
    year,
    present_price,
    kms_driven,
    fuel_type,
    seller_type,
    transmission,
    owner
):
    """
    Uses the trained model if model/car_price_model.pkl exists.

    Expected typical dataset encoding:
        Fuel_Type:
            Petrol = 0
            Diesel = 1
            CNG = 2

        Seller_Type:
            Dealer = 0
            Individual = 1

        Transmission:
            Manual = 0
            Automatic = 1
    """

    fuel_mapping = {
        "Petrol": 0,
        "Diesel": 1,
        "CNG": 2
    }

    seller_mapping = {
        "Dealer": 0,
        "Individual": 1
    }

    transmission_mapping = {
        "Manual": 0,
        "Automatic": 1
    }

    fuel_value = fuel_mapping.get(fuel_type, 0)
    seller_value = seller_mapping.get(seller_type, 0)
    transmission_value = transmission_mapping.get(transmission, 0)

    car_age = datetime.now().year - int(year)

    # -----------------------------------------------------
    # Try trained ML model first
    # -----------------------------------------------------

    if model is not None:

        # Typical CarDekho dataset feature order:
        # Year, Present_Price, Kms_Driven,
        # Fuel_Type, Seller_Type, Transmission, Owner

        try:
            features = np.array([[
                int(year),
                float(present_price),
                float(kms_driven),
                fuel_value,
                seller_value,
                transmission_value,
                int(owner)
            ]])

            prediction = model.predict(features)[0]

            return max(float(prediction), 0)

        except Exception as e:
            print("Prediction error:", e)

    # -----------------------------------------------------
    # Fallback estimate if model is unavailable
    # -----------------------------------------------------

    depreciation = max(0.15, 1 - (car_age * 0.08))

    mileage_factor = max(
        0.65,
        1 - (float(kms_driven) / 300000)
    )

    owner_factor = max(
        0.75,
        1 - (int(owner) * 0.05)
    )

    estimated = (
        float(present_price)
        * depreciation
        * mileage_factor
        * owner_factor
    )

    return max(estimated, 0.10)


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required():
    return "user_id" in session


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return redirect(url_for("login"))

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["name"] = user["name"]

            flash(
                f"Welcome back, {user['name']}!",
                "success"
            )

            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not username or not password:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash(
                "Password must contain at least 6 characters.",
                "error"
            )
            return redirect(url_for("register"))

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "error"
            )
            return redirect(url_for("register"))

        conn = get_db()

        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if existing:
            conn.close()

            flash(
                "Username already exists.",
                "error"
            )

            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        conn.execute(
            """
            INSERT INTO users
            (name, username, password, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                username,
                hashed_password,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        conn.commit()
        conn.close()

        flash(
            "Account created successfully. Please login.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("register.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(url_for("login"))


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if not login_required():
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db()

    total_predictions = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM predictions
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()["count"]

    latest = conn.execute(
        """
        SELECT *
        FROM predictions
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,)
    ).fetchone()

    recent_predictions = conn.execute(
        """
        SELECT *
        FROM predictions
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 5
        """,
        (user_id,)
    ).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_predictions=total_predictions,
        latest=latest,
        recent_predictions=recent_predictions
    )


# =========================================================
# PREDICT
# =========================================================

@app.route("/predict", methods=["GET", "POST"])
def predict():

    if not login_required():
        return redirect(url_for("login"))

    if request.method == "POST":

        try:

            year = int(request.form.get("year"))
            present_price = float(
                request.form.get("present_price")
            )
            kms_driven = float(
                request.form.get("kms_driven")
            )

            fuel_type = request.form.get("fuel_type")
            seller_type = request.form.get("seller_type")
            transmission = request.form.get("transmission")

            owner = int(
                request.form.get("owner")
            )

            current_year = datetime.now().year

            if year < 1980 or year > current_year:
                flash(
                    "Please enter a valid manufacturing year.",
                    "error"
                )
                return redirect(url_for("predict"))

            if present_price <= 0:
                flash(
                    "Present price must be greater than 0.",
                    "error"
                )
                return redirect(url_for("predict"))

            if kms_driven < 0:
                flash(
                    "Kilometers driven cannot be negative.",
                    "error"
                )
                return redirect(url_for("predict"))

            if fuel_type not in [
                "Petrol",
                "Diesel",
                "CNG"
            ]:
                flash(
                    "Please select a valid fuel type.",
                    "error"
                )
                return redirect(url_for("predict"))

            if seller_type not in [
                "Dealer",
                "Individual"
            ]:
                flash(
                    "Please select a valid seller type.",
                    "error"
                )
                return redirect(url_for("predict"))

            if transmission not in [
                "Manual",
                "Automatic"
            ]:
                flash(
                    "Please select a valid transmission.",
                    "error"
                )
                return redirect(url_for("predict"))

            if owner not in [0, 1, 2, 3]:
                flash(
                    "Please select a valid number of previous owners.",
                    "error"
                )
                return redirect(url_for("predict"))

            predicted_price = predict_car_price(
                year,
                present_price,
                kms_driven,
                fuel_type,
                seller_type,
                transmission,
                owner
            )

            conn = get_db()

            conn.execute(
                """
                INSERT INTO predictions
                (
                    user_id,
                    year,
                    present_price,
                    kms_driven,
                    fuel_type,
                    seller_type,
                    transmission,
                    owner,
                    predicted_price,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    year,
                    present_price,
                    kms_driven,
                    fuel_type,
                    seller_type,
                    transmission,
                    owner,
                    predicted_price,
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
            )

            conn.commit()
            conn.close()

            return render_template(
                "predict.html",
                prediction=predicted_price,
                form_data=request.form
            )

        except (ValueError, TypeError):

            flash(
                "Please enter valid car information.",
                "error"
            )

            return redirect(url_for("predict"))

    return render_template(
        "predict.html",
        prediction=None,
        form_data={}
    )


# =========================================================
# HISTORY
# =========================================================

@app.route("/history")
def history():

    if not login_required():
        return redirect(url_for("login"))

    conn = get_db()

    predictions = conn.execute(
        """
        SELECT *
        FROM predictions
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "history.html",
        predictions=predictions
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
def profile():

    if not login_required():
        return redirect(url_for("login"))

    conn = get_db()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return render_template(
        "profile.html",
        user=user
    )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    init_db()

    print("----------------------------------------")
    print("       CarPredict Application")
    print("----------------------------------------")
    print("Open: http://127.0.0.1:5000")
    print("----------------------------------------")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )