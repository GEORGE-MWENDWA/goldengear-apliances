from flask import Flask, render_template, request
import random
import string
from db_config import get_db

app = Flask(__name__)

# Generate 7-character referral code
def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()

        # Server-side validation
        if not name or not phone or not email:
            return render_template("register.html", error="All fields are required.")

        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            # Check if user already exists
            cursor.execute("SELECT * FROM users WHERE phone=%s OR email=%s", (phone, email))
            existing_user = cursor.fetchone()
            if existing_user:
                return render_template("register.html", error="User with this phone or email already exists.")

            # Insert new user
            code = generate_code()
            cursor.execute(
                "INSERT INTO users (full_name, phone, email, referral_code) VALUES (%s, %s, %s, %s)",
                (name, phone, email, code)
            )
            db.commit()
            return render_template("success.html", code=code)

        except Exception as e:
            db.rollback()
            return render_template("register.html", error=f"Database error: {e}")

        finally:
            cursor.close()

    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)
