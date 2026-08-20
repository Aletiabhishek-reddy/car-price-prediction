import sqlite3
from werkzeug.security import generate_password_hash


DATABASE = "database.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Predictions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            present_price REAL NOT NULL,
            driven_kms REAL NOT NULL,
            fuel_type TEXT NOT NULL,
            selling_type TEXT NOT NULL,
            transmission TEXT NOT NULL,
            owner INTEGER NOT NULL,
            predicted_price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def create_user(name, email, username, password):
    conn = get_connection()

    hashed_password = generate_password_hash(password)

    try:
        conn.execute("""
            INSERT INTO users
            (name, email, username, password)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            username,
            hashed_password
        ))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def get_user_by_username(username):
    conn = get_connection()

    user = conn.execute("""
        SELECT *
        FROM users
        WHERE username = ?
    """, (username,)).fetchone()

    conn.close()

    return user


def get_user_by_id(user_id):
    conn = get_connection()

    user = conn.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (user_id,)).fetchone()

    conn.close()

    return user


def save_prediction(
    user_id,
    year,
    present_price,
    driven_kms,
    fuel_type,
    selling_type,
    transmission,
    owner,
    predicted_price
):
    conn = get_connection()

    conn.execute("""
        INSERT INTO predictions (
            user_id,
            year,
            present_price,
            driven_kms,
            fuel_type,
            selling_type,
            transmission,
            owner,
            predicted_price
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        year,
        present_price,
        driven_kms,
        fuel_type,
        selling_type,
        transmission,
        owner,
        predicted_price
    ))

    conn.commit()
    conn.close()

def delete_prediction(prediction_id, user_id):
    conn = get_connection()

    conn.execute(
        """
        DELETE FROM predictions
        WHERE id = ? AND user_id = ?
        """,
        (prediction_id, user_id)
    )

    conn.commit()
    conn.close()


def get_user_predictions(user_id):
    conn = get_connection()

    predictions = conn.execute("""
        SELECT *
        FROM predictions
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,)).fetchall()

    conn.close()

    return predictions


def get_prediction_count(user_id):
    conn = get_connection()

    result = conn.execute("""
        SELECT COUNT(*) AS total
        FROM predictions
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    conn.close()

    return result["total"]


def get_latest_prediction(user_id):
    conn = get_connection()

    prediction = conn.execute("""
        SELECT *
        FROM predictions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id,)).fetchone()

    conn.close()

    return prediction
def delete_prediction(prediction_id, user_id):
    conn = get_connection()

    cursor = conn.execute("""
        DELETE FROM predictions
        WHERE id = ? AND user_id = ?
    """, (
        prediction_id,
        user_id
    ))

    conn.commit()

    deleted = cursor.rowcount > 0

    conn.close()

    return deleted