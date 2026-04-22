from flask import Flask, render_template, redirect, url_for, request, session

from flask import current_app as app
from .models import *

# login check 
def admin_required():
    return session.get('role') == 'admin'

def company_required(company_id):
    return session.get('role') == 'company' and session.get('user_id') == company_id

def student_required(student_id):
    return session.get('role') == 'student' and session.get('user_id') == student_id

@app.route('/')
def home():
    return redirect(url_for('login'))

#  authentication 

@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get("username")
        pwd = request.form.get("pwd")
        role = request.form.get("role")
        if role == "admin":
            this_admin = Admin.query.filter_by(username=username).first()
            if this_admin and this_admin.pwd == pwd:
                session['role'] = 'admin'
                session['user_id'] = this_admin.id
                return redirect("/admin")
            else:
                error = "Invalid username or password. Please try again."
        elif role == "company":
            this_company = Company.query.filter_by(email=username).first()
            if this_company and this_company.pwd == pwd:
                if this_company.status == "Approved":
                    session['role'] = 'company'
                    session['user_id'] = this_company.id
                    return redirect(f"/company/{this_company.id}")
                elif this_company.status == "Pending":
                    error = "Please Wait. Your account is not approved yet."
                else:
                    error = "Your account is blocked."
            else:
                error = "Invalid username or password. Please try again."
        elif role == "student":
            this_student = Student.query.filter_by(email=username).first()
            if this_student and this_student.pwd == pwd:
                if this_student.status == "Active":
                    session['role'] = 'student'
                    session['user_id'] = this_student.id
                    return redirect(f"/student/{this_student.id}")
                else:
                    error = "Your account is blocked."
            else:
                error = "Invalid username or password. Please try again."

    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/login')

@app.route("/register/company", methods=['GET', 'POST'])
def register_company():
    info = None
    if request.method == "POST":
        email = request.form.get("email")
        this_company = Company.query.filter_by(email=email).first()
        if this_company:
            info = "Company Already exist."
        else:
            name = request.form.get("name")
            pwd = request.form.get("pwd")
            hr_name = request.form.get("hr_name")
            phone = request.form.get("phone")
            website = request.form.get("website")
            about = request.form.get("about")
            new_company = Company(
                email=email, name=name, pwd=pwd,
                hr_name=hr_name, phone=phone, website=website, about=about
            )
            db.session.add(new_company)
            db.session.commit()
            return redirect("/login")
    return render_template("register_company.html", info=info)

@app.route("/register/student", methods=['GET', 'POST'])
def register_student():
    info = None
    if request.method == "POST":
        email = request.form.get("email")
        this_student = Student.query.filter_by(email=email).first()
        if this_student:
            info = "Student Already exist."
        else:
            name = request.form.get("name")
            pwd = request.form.get("pwd")
            phone = request.form.get("phone")
            rollno = request.form.get("rollno")
            dept = request.form.get("dept")
            year = request.form.get("year")
            cgpa = request.form.get("cgpa")
            skills = request.form.get("skills")
            resume = request.form.get("resume")
            new_student = Student(
                email=email, name=name, pwd=pwd, phone=phone,
                rollno=rollno, dept=dept, year=year, cgpa=cgpa,
                skills=skills, resume=resume
            )
            db.session.add(new_student)
            db.session.commit()
            return redirect("/login")
    return render_template("register_student.html", info=info)

# ---- Admin Dashboard ----

@app.route("/admin")
def admin():
    if not admin_required():
        return redirect("/login")
    this_admin = Admin.query.filter_by(username="admin").first()
    registered_companies = Company.query.filter_by(status="Approved").all()
    registered_students = Student.query.filter_by(status="Active").all()
    company_applications = Company.query.filter_by(status="Pending").all()
    ongoing_drives = Drive.query.filter_by(status="Active").all()
    pending_drives = Drive.query.filter_by(status="Pending").all()
    student_applications = Application.query.all()
    total_students = Student.query.filter_by(status="Active").count()
    total_companies = Company.query.filter_by(status="Approved").count()
    total_drives = Drive.query.count()
    total_applications = Application.query.count()
    return render_template(
        "admin_dashboard.html",
        this_admin=this_admin,
        registered_companies=registered_companies,
        registered_students=registered_students,
        company_applications=company_applications,
        ongoing_drives=ongoing_drives,
        pending_drives=pending_drives,
        student_applications=student_applications,
        total_students=total_students,
        total_companies=total_companies,
        total_drives=total_drives,
        total_applications=total_applications
    )

@app.route("/admin/search")
def admin_search():
    if not admin_required():
        return redirect("/login")
    query = request.args.get("query")
    search_type = request.args.get("type")
    results_students = []
    results_companies = []
    if query:
        if search_type == "student":
            results_students = Student.query.filter(
                (Student.name.ilike(f"%{query}%")) |
                (Student.email.ilike(f"%{query}%")) |
                (Student.rollno.ilike(f"%{query}%")) |
                (Student.phone.ilike(f"%{query}%"))
            ).all()
        else:
            results_companies = Company.query.filter(
                (Company.name.ilike(f"%{query}%")) |
                (Company.email.ilike(f"%{query}%"))
            ).all()
    return render_template(
        "admin_search.html", 
        results_students=results_students,
        results_companies=results_companies, 
        query=query, 
        search_type=search_type
        )

@app.route('/blacklist_reg_company/<int:company_id>')
def blacklist_company(company_id):
    if not admin_required():
        return redirect("/login")
    comp = Company.query.filter_by(id=company_id).first()
    if comp:
        comp.status = "Blocked"
        db.session.commit()
        drives = Drive.query.filter_by(company_id=comp.id).all()
        for drive in drives:
            drive.status = "Closed"
        db.session.commit()
    return redirect("/admin")

@app.route('/blacklist_student/<int:student_id>')
def blacklist_student(student_id):
    if not admin_required():
        return redirect("/login")
    stu = Student.query.filter_by(id=student_id).first()
    if stu:
        stu.status = "Blocked"
        db.session.commit()
    return redirect("/admin")

@app.route('/approved_comp_application/<int:company_id>')
def approved_comp_application(company_id):
    if not admin_required():
        return redirect("/login")
    comp = Company.query.filter_by(id=company_id).first()
    if comp:
        comp.status = "Approved"
        db.session.commit()
    return redirect("/admin")

@app.route('/reject_comp_application/<int:company_id>')
def reject_comp_application(company_id):
    if not admin_required():
        return redirect("/login")
    comp = Company.query.filter_by(id=company_id).first()
    if comp:
        comp.status = "Rejected"
        db.session.commit()
    return redirect("/admin")

@app.route('/approve_drive/<int:drive_id>')
def approve_drive(drive_id):
    if not admin_required():
        return redirect("/login")
    drive = Drive.query.filter_by(id=drive_id).first()
    if drive:
        drive.status = "Active"
        db.session.commit()
    return redirect("/admin")

@app.route('/close_drive/<int:drive_id>')
def close_drive(drive_id):
    if not admin_required():
        return redirect("/login")
    drive = Drive.query.filter_by(id=drive_id).first()
    if drive:
        drive.status = "Closed"
        db.session.commit()
    return redirect("/admin")

@app.route('/view_ongoing_drive/<int:drive_id>')
def view_ongoing_drive(drive_id):
    if not admin_required():
        return redirect("/login")
    drive = Drive.query.filter_by(id=drive_id).first()
    return render_template("view_ongoing_drive.html", drive=drive)

@app.route('/view_student_application/<int:application_id>')
def view_student_application(application_id):
    if not admin_required():
        return redirect("/login")
    stu_app = Application.query.filter_by(id=application_id).first()
    return render_template("view_student_application.html", stu_app=stu_app)

# ---- Company Dashboard ----

@app.route("/company/<int:company_id>")
def company_dashboard(company_id):
    if not company_required(company_id):
        return redirect("/login")
    company = Company.query.filter_by(id=company_id).first()
    active_drives = Drive.query.filter_by(company_id=company_id, status="Active").all()
    closed_drives = Drive.query.filter_by(company_id=company_id, status="Closed").all()
    pending_drives = Drive.query.filter_by(company_id=company_id, status="Pending").all()
    return render_template(
        "company_dashboard.html", 
        company=company,
        active_drives=active_drives, 
        closed_drives=closed_drives,
        pending_drives=pending_drives, 
        company_id=company_id
        )

@app.route("/create_drive/<int:company_id>", methods=['GET', 'POST'])
def create_drive(company_id):
    if not company_required(company_id):
        return redirect("/login")
    if request.method == "POST":
        drive_name = request.form.get("drive_name")
        title = request.form.get("title")
        description = request.form.get("description")
        eligibility = request.form.get("eligibility")
        location = request.form.get("location")
        salary = request.form.get("salary")
        mode = request.form.get("mode")
        deadline = request.form.get("deadline")
        new_drive = Drive(
            company_id=company_id, drive_name=drive_name, title=title,
            description=description, eligibility=eligibility, location=location,
            salary=salary, mode=mode, deadline=deadline,
            status="Pending"
        )
        db.session.add(new_drive)
        db.session.commit()
        return redirect(f"/company/{company_id}")
    return render_template("create_drive.html", company_id=company_id)

@app.route('/close_comp_drive/<int:company_id>/<int:drive_id>')
def close_comp_drive(company_id, drive_id):
    if not company_required(company_id):
        return redirect("/login")
    drive = Drive.query.filter_by(id=drive_id).first()
    if drive:
        drive.status = "Closed"
        db.session.commit()
    return redirect(f"/company/{company_id}")

# ---- Student Dashboard ----

@app.route("/student/<int:student_id>")
def student_dashboard(student_id):
    if not student_required(student_id):
        return redirect("/login")
    student = Student.query.filter_by(id=student_id).first()
    organizations = Company.query.filter_by(status="Approved").all()
    applied_drives = Application.query.filter_by(student_id=student_id).order_by(Application.applied_on).all()
    return render_template("student_dashboard.html", organizations=organizations,
                           applied_drives=applied_drives, student=student)

@app.route('/updates_on_drive/<int:drive_id>')
def updates_on_drive(drive_id):
    if not (session.get('role') == 'company'):
        return redirect("/login")
    drive = Drive.query.filter_by(id=drive_id).first()
    applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template("updates_on_drive.html", applications=applications, drive=drive)

@app.route("/review_stu_appl/<int:drive_id>/<int:student_id>", methods=['GET', 'POST'])
def review_stu_appl(drive_id, student_id):
    if not (session.get('role') == 'company'):
        return redirect("/login")
    stu_app = Application.query.filter_by(drive_id=drive_id, student_id=student_id).first()
    if request.method == 'POST':
        result = request.form.get("result")
        remarks = request.form.get("remarks")
        if result != "":
            stu_app.status = result
            stu_app.remarks = remarks
            db.session.commit()
        return redirect(f"/updates_on_drive/{drive_id}")
    return render_template("review_stu_appl.html", stu_app=stu_app)

@app.route("/view_company_details/<int:company_id>/<int:student_id>")
def view_company_details(company_id, student_id):
    if not student_required(student_id):
        return redirect("/login")
    company = Company.query.filter_by(id=company_id).first()
    student = Student.query.filter_by(id=student_id).first()
    current_drives = Drive.query.filter_by(company_id=company_id, status="Active").all()
    return render_template("view_company_details.html", current_drives=current_drives,
                           company=company, student=student)

@app.route("/apply_current_drive/<int:drive_id>/<int:student_id>", methods=['GET', 'POST'])
def apply_current_drive(drive_id, student_id):
    if not student_required(student_id):
        return redirect("/login")
    drive = Drive.query.filter_by(id=drive_id).first()
    info = None
    if request.method == 'POST':
        this_appl = Application.query.filter_by(drive_id=drive_id, student_id=student_id).first()
        if this_appl:
            info = "Already Applied!"
        else:
            new_application = Application(student_id=student_id, drive_id=drive_id)
            db.session.add(new_application)
            db.session.commit()
            return redirect(f"/view_company_details/{drive.company_id}/{student_id}")
    return render_template("apply_current_drive.html", drive=drive, info=info, student_id=student_id)

@app.route("/student_history/<int:student_id>")
def student_history(student_id):
    if not student_required(student_id):
        return redirect("/login")
    student = Student.query.filter_by(id=student_id).first()
    applications = Application.query.filter_by(student_id=student_id).all()
    return render_template("student_history.html", student=student, applications=applications)

@app.route("/edit_student/<int:student_id>", methods=['GET', 'POST'])
def edit_student(student_id):
    if not student_required(student_id):
        return redirect("/login")
    student = Student.query.filter_by(id=student_id).first()
    if request.method == 'POST':
        student.name = request.form.get("name")
        student.phone = request.form.get("phone")
        student.dept = request.form.get("dept")
        student.year = request.form.get("year")
        student.cgpa = request.form.get("cgpa")
        student.skills = request.form.get("skills")
        student.resume = request.form.get("resume")
        db.session.commit()
        return redirect(f"/student/{student_id}")
    return render_template("edit_student.html", student=student)
