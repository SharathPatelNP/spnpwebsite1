from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc
import re

app = Flask(__name__)
app.secret_key = "1234567"  # replace with something random/secure
app.config['TEMPLATES_AUTO_RELOAD'] = True  # auto reload templates

# ===== SQL Server Connection String =====
CONN_STR = (
    r'DRIVER={ODBC Driver 18 for SQL Server};'
    r'SERVER=LAPTOP-064GCCCV\SQLEXPRESS;'       # change if needed
    r"DATABASE=VendorDB;"
    r"Trusted_Connection=yes;"
    r"Encrypt=no;"
)

def get_db_connection():
    print("S500")
    print(CONN_STR)
    return pyodbc.connect(CONN_STR, autocommit=True)

# ===== Simple validators =====
PHONE_RE = re.compile(r'^[0-9+\-\s]{7,20}$')

def validate_vendor(name, city, state, phone):
    print("S400") #..............................................................................400
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
            print("S300") #.......................................................................300
            return render_template("index.html", form=request.form)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Vendors (Name, City, State, Phone) VALUES (?, ?, ?, ?)",
                (name, city, state, phone)
            )
            cursor.close()
            conn.close()
            return redirect(url_for("success"))
        except Exception as ex:
            flash(f"Database error: {ex}", "error")
            print("S100") #.......................................................................100
            return render_template("index.html", form=request.form)

    # GET request
    return render_template("index.html", form={})

@app.route("/success")
def success():
    print("S200") #..............................................................................200
    return render_template("success.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)


