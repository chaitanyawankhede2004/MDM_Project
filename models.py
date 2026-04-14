from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    enr = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    stdrank = db.Column(db.Integer, nullable=False)

class College(db.Model):
    __tablename__ = 'colleges'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    institute_name = db.Column(db.String(255), nullable=False)
    course = db.Column(db.String(255), nullable=False)
    opening_rank = db.Column(db.Integer, nullable=False)
    closing_rank = db.Column(db.Integer, nullable=False)
