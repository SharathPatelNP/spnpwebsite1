from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import re
import os

app = Flask(__name__)
app.secret_key = "1234567"  # replace with a strong secret key
app.config['TEMPLATES_AUTO_RELOAD'] = True  # auto reload templates

# ===== MySQL Database Connection (Render) =====
# For Render, add these environment variables in your Dashboard -> Environment tab:
# DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'VendorDB'),
}

def get_db_connection():
    print("Connecting to MySQL...")
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn

# ===== Simple validators =====
PHONE_RE = re.compile(r'^[0-9+\-\s]{7,20}$')

def validate_vendor(name, city, state, phone):
    errors = []
    if not name or len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters.")
    if not city or len(city.strip()) < 2:
        errors.append("City must be at least 2 characters.")
    if not state or len(state.strip()) < 2:
        errors.append("State must be at least 2 characters.")
    if not phone or not PHONE_RE.match(phone.strip()):
        errors.append("Phone must be 7–20 digits (may include +, - or spaces).")
    return errors

# ===== Routes =====
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        phone = request.form.get("phone", "").strip()

        errors = validate_vendor(name, city, state, phone)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("index.html", form=request.form)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Vendors (Name, City, State, Phone) VALUES (%s, %s, %s, %s)",
                (name, city, state, phone)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for("success"))
        except Exception as ex:
            flash(f"Database error: {ex}", "error")
            return render_template("index.html", form=request.form)

    # GET request
    return render_template("index.html", form={})

@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    # Render automatically sets PORT as an environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
