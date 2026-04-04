from flask import Flask, render_template, request, redirect, session, url_for
from db import get_connection

app = Flask(__name__)
app.secret_key = "secret123"

# HOME
@app.route("/")
def home():
    return render_template("index.html")

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        enr = request.form["enr"]
        name = request.form["name"]
        password = request.form["password"]
        rank = request.form["rank"]

        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("INSERT INTO students (enr, name, password, stdrank) VALUES (%s,%s,%s,%s)",
                        (enr, name, password, rank))
            con.commit()
            con.close()
            return redirect(url_for("login"))
        except Exception as e:
            # In a real app, you'd flash an error message here
            print(f"Error: {e}")
            return "Registration failed. Database error."

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        enr = request.form["enr"]
        password = request.form["password"]

        con = get_connection()
        cur = con.cursor()
        cur.execute("SELECT name, stdrank FROM students WHERE enr=%s AND password=%s",
                    (enr, password))
        user = cur.fetchone()
        con.close()

        if user:
            session["name"] = user[0]
            session["rank"] = user[1]
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Credentials. <a href='/login'>Try again</a>"

    return render_template("login.html")

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "name" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html",
                           name=session["name"],
                           rank=session["rank"])

# PREDICT
@app.route("/predict")
def predict():
    if "rank" not in session:
        return redirect(url_for("login"))
        
    rank = session["rank"]
    con = get_connection()
    cur = con.cursor()

    # Query matching rank between opening and closing
    cur.execute("""
        SELECT institute_name, course, opening_rank, closing_rank
        FROM colleges
        WHERE %s BETWEEN opening_rank AND closing_rank
        ORDER BY closing_rank ASC
        LIMIT 20
    """, (rank,))

    data = cur.fetchall()
    con.close()

    return render_template("result.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
