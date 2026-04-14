from flask import Flask, render_template, request, redirect, session, url_for
from models import db, Student, College

app = Flask(__name__)
app.secret_key = "secret123"

# Setup SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

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
            # Check if student already exists
            existing = Student.query.filter_by(enr=enr).first()
            if existing:
                return "Student with this enrollment number already exists. <a href='/register'>Try again</a>"
            
            new_student = Student(enr=enr, name=name, password=password, stdrank=int(rank))
            db.session.add(new_student)
            db.session.commit()
            return redirect(url_for("login"))
        except Exception as e:
            print(f"Error: {e}")
            return "Registration failed. Database error."

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        enr = request.form["enr"]
        password = request.form["password"]

        user = Student.query.filter_by(enr=enr, password=password).first()

        if user:
            session["name"] = user.name
            session["rank"] = user.stdrank
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
        
    user_rank = session["rank"]
    
    # Query matching rank between opening and closing, ascending by closing_rank
    data = College.query.filter(
        (College.opening_rank <= user_rank) & 
        (College.closing_rank >= user_rank)
    ).order_by(College.closing_rank.asc()).limit(20).all()

    # The template expects a list of tuples like (institute_name, course, opening_rank, closing_rank)
    # SQLAlchemy objects need to be formatted the way the original template consumed them
    formatted_data = [(item.institute_name, item.course, item.opening_rank, item.closing_rank) for item in data]

    return render_template("result.html", data=formatted_data)

# SEARCH
@app.route("/search")
def search():
    if "name" not in session:
        return redirect(url_for("login"))
        
    query = request.args.get("q", "").strip()
    data = []
    
    if query:
        # Perform Case-insensitive search on institute_name or course
        search_term = f"%{query}%"
        data = College.query.filter(
            College.institute_name.ilike(search_term) | 
            College.course.ilike(search_term)
        ).order_by(College.institute_name.asc(), College.course.asc()).limit(50).all()
        
    return render_template("search.html", query=query, data=data)

if __name__ == "__main__":
    app.run(debug=True)
