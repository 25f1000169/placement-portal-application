from datetime import datetime
from .database import db

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    pwd = db.Column(db.String(), nullable=False)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), unique=True, nullable=False)
    pwd = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(), nullable=False)
    hr_name = db.Column(db.String())
    phone = db.Column(db.String(10))
    website = db.Column(db.String())
    about = db.Column(db.Text)
    status = db.Column(db.String(), default='Pending') # Approved , Blocked, Rejected
    
    drives = db.relationship('Drive', backref='company')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), unique=True, nullable=False)
    pwd = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String(10))
    rollno = db.Column(db.String(), unique=True, nullable=False)
    dept = db.Column(db.String())
    year = db.Column(db.Integer)
    cgpa = db.Column(db.Float)
    skills = db.Column(db.Text)
    resume = db.Column(db.String())
    status = db.Column(db.String(), default='Active') # Blocked
    
    applications = db.relationship('Application', backref='student')

class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    title = db.Column(db.String(), nullable=False)
    drive_name = db.Column(db.String())
    description = db.Column(db.Text)
    eligibility = db.Column(db.Text)
    location = db.Column(db.String())
    salary = db.Column(db.String())
    mode = db.Column(db.String())
    deadline = db.Column(db.String())
    status = db.Column(db.String(), default='Active') # Closed
    
    applications = db.relationship('Application', backref='drive')

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable=False)
    status = db.Column(db.String(), default='Applied') # Shortlist, Waiting, Selected, Reject
    remarks = db.Column(db.Text)
    applied_on = db.Column(db.String(), default=str(datetime.now().date()))
    
    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='_student_drive_uc'),)
