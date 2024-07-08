import datetime

from bson import ObjectId
from flask import Flask, render_template, request, session, redirect, flash
import pymongo

WEEK_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

myClient = pymongo.MongoClient('mongodb://localhost:27017')
mydb = myClient["Course_Management_System"]
professor_collection = mydb['professors']
student_collection = mydb['student']
sections_collection = mydb['sections']
department_collection = mydb['department']
course_materials_collection = mydb['course_materials']
course_collection = mydb['course']
enrolment_collection = mydb['enrolments']
assignments_collection = mydb['assignments']
assignment_submission_collection = mydb['assignment_submission']
room_collection = mydb['room_collection']


import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = APP_ROOT + "/static/picture"

app = Flask(__name__)
app.secret_key = "yedghbnikulhn"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin_login1",methods=['post'])
def aLogin1():
    Username = request.form.get("Username")
    Password = request.form.get("Password")
    if Username == 'admin' and Password == 'admin':
        session['role'] = 'admin'
        return render_template("admin_home.html", Username=Username)
    else:
        return render_template("msg.html", msg='Invalid Login Details',color='text-danger')


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/logout")
def logout():
    return render_template("index.html")


@app.route("/professor_login")
def professor_login():
    return render_template("professor_login.html")


@app.route("/add_professor")
def add_professor():
    professor_id = request.args.get("professor_id")
    professor = {}
    if professor_id != None:
        professor = professor_collection.find_one({"_id":ObjectId(professor_id)})
    professors = professor_collection.find({})
    return render_template("add_professor.html",professors=professors, professor=professor)


@app.route("/add_professor_action",methods=['post'])
def add_professor_action():
    Professor_id = request.form.get('Professor_id')
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    experience = request.form.get("experience")
    age = request.form.get("age")
    gender = request.form.get("gender")
    ssn = request.form.get("ssn")
    date_of_birth = request.form.get("date_of_birth")
    zipcode = request.form.get("zipcode")
    city = request.form.get("city")
    state = request.form.get("state")
    address = request.form.get("address")
    picture = request.files.get("picture")
    print(picture.filename)
    if picture.filename !="":
        path = APP_ROOT + "/" + picture.filename
        picture.save(path)

    password = request.form.get("password")
    password2 = request.form.get("password2")
    if password != password2:
        flash("Confirm password and New Password Not Matched")
        return render_template("msg.html", msg="confirm password must be same")
    if Professor_id == "":
        total_count = professor_collection.count_documents({'$or': [{"email": email}, {"phone": phone}]})
        if total_count > 0:
            return render_template("msg2.html", msg='Details Already exists', color='text-danger')
        else:
            professor_collection.insert_one( {"first_name": first_name,"last_name":last_name,"ssn":ssn,"date_of_birth":date_of_birth,"zipcode":zipcode,"address":address,"city":city, "email": email, "phone": phone,"picture":picture.filename,"password": password, "experience": experience,"age":age,"gender":gender,"is_password_changed": False,"state":state})
            return redirect("/add_professor")
    else:
        query1 = {"_id": ObjectId(Professor_id)}
        if picture.filename == "":
            query2 = {"$set": {"first_name": first_name, "last_name": last_name, "ssn": ssn, "state": state,
                               "date_of_birth": date_of_birth, "zipcode": zipcode, "address": address, "city": city,
                               "email": email, "phone": phone, "password": password,
                               "experience": experience, "age": age, "gender": gender}}
        else:
            query2 = {"$set": {"first_name": first_name,"last_name":last_name,"ssn":ssn,"state":state,"date_of_birth":date_of_birth,"zipcode":zipcode,"address":address,"city":city, "email": email, "phone": phone,"picture":picture.filename,"password": password, "experience": experience,"age":age,"gender":gender}}
        professor_collection.update_one(query1, query2)
        return redirect("/add_professor")


@app.route("/professor_login1",methods=['post'])
def professor_login1():
    email = request.form.get("email")
    password = request.form.get("password")
    myquery = {"email": email, "password": password}
    total_count = professor_collection.count_documents(myquery)
    if total_count > 0:
        results = professor_collection.find(myquery)
        for result in results:
            if result['is_password_changed']:
                session['Professor_id'] = str(result['_id'])
                session['role'] = 'Professor'
                return redirect("/professor_home")
            else:
                return render_template("change_password.html", Professor_id=result['_id'])
    else:
        return render_template("msg.html", msg="Invalid login details", color='text-danger')


@app.route("/change_password_action")
def change_password_action():
    password = request.args.get("password")
    password2 = request.args.get("password2")
    Professor_id = request.args.get('Professor_id')
    if password != password2:
        flash("Confirm password and New Password Not Matched")
        return render_template("msg.html", msg="confirm password must be same")
    query = {"_id": ObjectId(Professor_id)}
    query2 = {"$set": {"password": password, "is_password_changed": True}}
    professor_collection.update_one(query, query2)
    Professor = professor_collection.find_one({"_id": ObjectId(Professor_id)})
    session['Professor_id'] = str(Professor['_id'])
    session['role'] = 'Professor'
    return redirect('/professor_home')



@app.route("/view_professor")
def view_professor():
    if session['role'] != 'Professor':
        professors = professor_collection.find({})
    else:
        professors = professor_collection.find({"_id": ObjectId(session['Professor_id'])})
    return render_template("view_professor.html",professors=professors)


@app.route("/professor_home")
def professor_home():
    Professor_id = session['Professor_id']
    query = {"_id": ObjectId(Professor_id)}
    Professor = professor_collection.find_one(query)
    return render_template("professor_home.html", Professor=Professor)


@app.route("/student_home")
def student_home():
    return render_template("student_home.html")


@app.route("/student_login")
def student_login():
    return render_template("student_login.html")


@app.route("/student_registration")
def student_registration():
    return render_template("student_registration.html")


@app.route("/student_reg1",methods=['post'])
def student_reg1():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    age = request.form.get("age")
    gender = request.form.get("gender")
    date_of_birth = request.form.get("date_of_birth")
    zipcode = request.form.get("zipcode")
    city = request.form.get("city")
    state = request.form.get("state")
    address = request.form.get("address")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    if password != password2:
        flash("Confirm password and New Password Not Matched")
        return render_template("msg.html", msg="confirm password must be same")
    total_count = student_collection.count_documents({'$or': [{"email": email}, {"phone": phone}]})
    if total_count > 0:
        return render_template("msg2.html", msg='Details Already exists', color='text-danger')
    else:
        student_collection.insert_one(
            {"first_name": first_name, "last_name": last_name, "date_of_birth": date_of_birth,
             "zipcode": zipcode, "address": address, "city": city,"state":state ,"email": email, "phone": phone,
             "password": password,"age": age,
             "gender": gender})
        return render_template('msg.html', msg='Student Registered Successfully', color='text-success')


@app.route("/student_login1",methods=['post'])
def student_login1():
    email = request.form.get("email")
    password = request.form.get("password")
    myquery = {"email": email, "password": password}
    total_count = student_collection.count_documents(myquery)
    if total_count > 0:
        results = student_collection.find(myquery)
        for result in results:
            session['student_id'] = str(result['_id'])
            session['role'] = 'student'
            return redirect('/student_home')
    else:
        return render_template("msg.html", msg="Invalid login details", color='text-danger')


@app.route("/view_professors")
def view_professors():
    return render_template("view_professors.html")


@app.route("/add_room")
def add_room():
    rooms = room_collection.find()
    return render_template("add_room.html",rooms=rooms)


@app.route("/add_room1",methods=['post'])
def add_room1():
    room_number = request.form.get("room_number")
    room_capacity = request.form.get("room_capacity")
    total_count = room_collection.count_documents({'$or': [{"room_number": room_number}]})
    if total_count > 0:
        return render_template("msg2.html", msg='Details Already exists', color='text-danger')
    else:
        room_collection.insert_one({"room_capacity": room_capacity,"room_number":room_number})
        return redirect("/add_room")

@app.route("/get_rooms")
def get_rooms():
    room_id = request.args.get("room_id")
    query = {"_id": ObjectId(room_id)}
    room = room_collection.find_one(query)
    room['_id'] =str(room['_id'])
    return room


@app.route("/department")
def department():
    departments = department_collection.find({})
    return render_template("department.html",departments=departments)


@app.route('/department_action', methods=['post'])
def department_action():
    department_id = request.form.get('department_id')
    department_name = request.form.get('department_name')
    if department_id == None or department_id == "":
        total_count = department_collection.count_documents({'$or': [{"department_name": department_name}]})
        if total_count > 0:
            return render_template("msg2.html", msg='Details Already exists', color='text-danger')
        else:
            department_collection.insert_one({"department_name": department_name})
            return redirect("/department")
    else:
        query1 = {"_id" : ObjectId(department_id)}
        query2 = {"$set": {"department_name": department_name}}
        department_collection.update_one(query1, query2)
        return redirect("/department")


@app.route("/add_course")
def add_course():
    return render_template("add_course.html")


@app.route("/add_course_action",methods=['post'])
def add_course_action():
    course_name = request.form.get("course_name")
    description = request.form.get("description")
    picture = request.files.get("picture")
    path = APP_ROOT + "/" + picture.filename
    picture.save(path)
    total_count = course_collection.count_documents({'$or': [{"course_name": course_name}]})
    if total_count > 0:
        return render_template("msg.html", msg='Details Already exists', color='text-danger')
    else:
        course_collection.insert_one({"course_name": course_name,"picture":picture.filename,"description":description})
        return render_template('msg2.html', msg='Course Added Successfully', color='text-success')


@app.route("/view_courses")
def view_courses():
    courses = course_collection.find()
    courses = list(courses)
    print(courses)
    return render_template("view_courses.html",courses=courses)


@app.route("/add_course_material")
def add_course_material():
    section_id = request.args.get("section_id")
    query = {"_id": ObjectId(section_id)}
    sections = sections_collection.find(query)
    course_materials = course_materials_collection.find({})
    return render_template("add_course_material.html",course_materials=course_materials,section_id=section_id,sections=sections)


@app.route("/add_course_material_action",methods=['post'])
def add_course_material_action():
    section_id = request.form.get("section_id")
    material_title = request.form.get("material_title")
    material_description = request.form.get("material_description")
    material_pdf = request.files.get("material_pdf")
    path = APP_ROOT + "/" + material_pdf.filename
    material_pdf.save(path)
    course_materials_collection.insert_one({"material_title": material_title,"material_pdf":material_pdf.filename,"material_description":material_description,"section_id":ObjectId(section_id)})
    return redirect("/add_course_material")


@app.route("/view_course_materials")
def view_course_materials():
    course_materials = course_materials_collection.find()
    return render_template("view_course_materials.html",course_materials=course_materials)


@app.route("/add_section")
def add_section():
    section_id = request.args.get("section_id")
    section = {}
    options = []


    course_id = request.args.get("course_id")
    query = {"_id": ObjectId(course_id)}
    courses = course_collection.find(query)
    rooms = room_collection.find({})
    departments = department_collection.find({})
    professors =  professor_collection.find({})
    if session['role'] == 'Professor':
        Professors_id = {"_id": 'Professors_id'}
        professors = professor_collection.find(Professors_id)
    return render_template("add_section.html",courses=courses, section=section, options=options ,course_id=course_id,rooms=rooms,departments=departments,professors=professors, str=str)


@app.route("/add_section1")
def add_section1():
    section_id = request.args.get("section_id")
    course_id = request.args.get("course_id")
    room_id = request.args.get("room_id")
    department_id = request.args.get("department_id")
    Professor_id = request.args.get("Professor_id")
    if session['role'] == 'Professor':
        Professor_id = session['Professor_id']
    CRN_number = request.args.get("CRN_number")
    section_start_time = request.args.get("section_start_time")
    section_end_time = request.args.get("section_end_time")
    room_number = request.args.get("room_number")
    Enrolment_start_date = request.args.get("Enrolment_start_date")
    Enrolment_end_date = request.args.get("Enrolment_end_date")
    Number_of_students = request.args.get("Number_of_students")
    day = request.args.getlist("day")
    total_count = sections_collection.count_documents({'$or': [{"CRN_number": CRN_number}]})
    section_start_time = datetime.datetime.strptime(section_start_time,"%H:%M")
    section_end_time = datetime.datetime.strptime(section_end_time,"%H:%M")
    Enrolment_start_date = datetime.datetime.strptime(Enrolment_start_date,"%Y-%m-%d")
    Enrolment_end_date = datetime.datetime.strptime(Enrolment_end_date,"%Y-%m-%d")
    query = {"Professor_id":ObjectId(Professor_id)}
    sections = sections_collection.find(query)
    section_ids=[]
    for section in sections:
        if section_id=="":
            section_ids.append(section['_id'])
        else:
            if str(section['_id']) != section_id:
                section_ids.append(section['_id'])
    print(section_ids)

    query = {"$or": [
        {"section_start_time": {"$gte": section_start_time, "$lte": section_end_time}, "section_end_time": {"$gte": section_start_time, "$gte": section_end_time},"_id": {"$in":section_ids},"day":{"$in":day}},
        {"section_start_time": {"$lte": section_start_time, "$lte": section_end_time}, "section_end_time": {"$gte": section_start_time, "$lte": section_end_time},"_id": {"$in":section_ids},"day":{"$in":day}},
        {"section_start_time": {"$lte": section_start_time, "$lte": section_end_time}, "section_end_time": {"$gte": section_start_time, "$gte": section_end_time},"_id": {"$in":section_ids},"day":{"$in":day}},
        {"section_start_time": {"$gte": section_start_time, "$lte": section_start_time}, "section_end_time": {"$gte": section_start_time, "$lte": section_end_time},"_id": {"$in":section_ids},"day":{"$in":day}}
    ]}
    count = sections_collection.count_documents(query)
    if count > 0:
        return render_template('msg2.html', msg='There is a Time collision for this Section')
    if total_count > 0 and section_id == "":
        return render_template('msg2.html', msg='Duplicate CRN')
    else:
        if section_id == "":
            sections_collection.insert_one({"CRN_number": CRN_number, "section_start_time": section_start_time,"section_end_time": section_end_time,"room_number": room_number,"Enrolment_start_date": Enrolment_start_date,"Enrolment_end_date": Enrolment_end_date,"Number_of_students": Number_of_students, "day": day,"course_id": ObjectId(course_id),"Professor_id": ObjectId(Professor_id), "department_id": ObjectId(department_id),"room_id":ObjectId(room_id)})
            return render_template('msg2.html', msg='Section Added Successfully')
        else:
            query1= {"_id": ObjectId(section_id)}
            query2 = {"$set": {"CRN_number": CRN_number, "section_start_time": section_start_time,"section_end_time": section_end_time,"room_number": room_number,"Enrolment_start_date": Enrolment_start_date,"Enrolment_end_date": Enrolment_end_date,"Number_of_students": Number_of_students, "day": day,"course_id": ObjectId(course_id),"Professor_id": ObjectId(Professor_id), "department_id": ObjectId(department_id),"room_id":ObjectId(room_id)}}
            sections_collection.update_one(query1, query2)
            return render_template('msg2.html', msg='Section Updated Successfully')


@app.route("/view_sections")
def view_sections():

    course_id = request.args.get("course_id")
    query = {"course_id": ObjectId(course_id)}
    if session['role'] == 'Professor':
        Professor_id = session['Professor_id']
        query = {"course_id": ObjectId(course_id),"Professor_id":ObjectId(Professor_id)}
    # department_id = request.args.get("department_id")
    # query ={"course_id":ObjectId(course_id),"department_id":ObjectId(department_id)}
    sections = sections_collection.find(query)
    sections = list(sections)
    return render_template("view_sections.html",sections=sections,course_id=course_id,get_course_by_course_id = get_course_by_course_id,get_department_by_department_id = get_department_by_department_id,get_enrolment_by_student_id_section_id=get_enrolment_by_student_id_section_id,get_enrolment_by_student_id=get_enrolment_by_student_id, datetime=datetime,is_course_enrolled=is_course_enrolled,get_professor_by_Professor_id=get_professor_by_Professor_id,get_room_by_room_id=get_room_by_room_id)

def get_professor_by_Professor_id(Professor_id):
    query = {"_id":ObjectId(Professor_id)}
    Professor = professor_collection.find_one(query)
    return Professor

def get_room_by_room_id(room_id):
    query = {"_id":ObjectId(room_id)}
    rooms = room_collection.find_one(query)
    return rooms


def get_room_by_room_id(room_id):
    query = {"_id":room_id}
    rooms = room_collection.find_one(query)
    return rooms

def get_course_by_course_id(course_id):
    query= {"_id":ObjectId(course_id)}
    courses = course_collection.find_one(query)
    return courses


def get_department_by_department_id(department_id):
    query = {"_id":ObjectId(department_id)}
    departments = department_collection.find_one(query)
    return departments


def get_enrolment_by_student_id_section_id(section_id):
    student_id = session["student_id"]
    query = {"student_id":ObjectId(student_id),"section_id":ObjectId(section_id),"status":'Enrolled'}
    enrolments=enrolment_collection.find(query)
    return enrolments[0]



def is_course_enrolled(section_id):
    student_id = session['student_id']
    query  = {"_id":section_id}
    section= sections_collection.find_one(query)
    course_id = section['course_id']
    section_ids =[]
    query = {"course_id":course_id}
    sections = sections_collection.find(query)
    for section in sections:
        section_ids.append(section['_id'])
    query ={"student_id":ObjectId(student_id),"section_id":{"$in":section_ids}}
    count = enrolment_collection.count_documents(query)
    if count >0:
        return True
    else :
        return False


def get_enrolment_by_student_id(section_id):
    student_id = session["student_id"]
    query = {"student_id":ObjectId(student_id),"section_id":ObjectId(section_id),"status":'Enrolled'}
    count = enrolment_collection.count_documents(query)
    if count == 0:
        return False
    else:
        return True


@app.route("/enrol")
def enrol():
    section_id = request.args.get("section_id")
    student_id = session['student_id']
    date =datetime.datetime.now()
    status = request.args.get("status")
    query = {"section_id": ObjectId(section_id), 'student_id': ObjectId(student_id)}
    count = enrolment_collection.count_documents(query)
    if count < 0:
        return render_template("msg2.html",msg="You already enrolled for this section")
    query3 = {'student_id': ObjectId(student_id)}
    print(query3)
    count = enrolment_collection.count_documents(query3)
    print(count)
    if count >= 3:
        return render_template("msg2.html",msg="You can not enroll More then three section")
    enrolment_collection.find(query3)
    query = {"_id": ObjectId(section_id)}
    section = sections_collection.find_one(query)
    section_start_time = section['section_start_time']
    section_end_time = section['section_end_time']
    day = section['day']
    query = {"student_id": ObjectId(student_id), "status": {"$ne": 'Dropped'}}
    enrolments = enrolment_collection.find(query)
    section_ids = []
    for enrolment in enrolments:
        section_ids.append(enrolment['section_id'])
    print(section_ids)
    query = {"$or": [
        {"section_start_time": {"$gte": section_start_time, "$lte": section_end_time},"section_end_time": {"$gte": section_start_time, "$gte": section_end_time}, "_id": {"$in": section_ids}, "day": day},
        {"section_start_time": {"$lte": section_start_time, "$lte": section_end_time},"section_end_time": {"$gte": section_start_time, "$lte": section_end_time}, "_id": {"$in": section_ids},"day": day},
        {"section_start_time": {"$lte": section_start_time, "$lte": section_end_time},"section_end_time": {"$gte": section_start_time, "$gte": section_end_time}, "_id": {"$in": section_ids},"day": day},
        {"section_start_time": {"$gte": section_start_time, "$lte": section_start_time},"section_end_time": {"$gte": section_start_time, "$lte": section_end_time}, "_id": {"$in": section_ids},"day": day}
    ]}
    count = sections_collection.count_documents(query)
    if count > 0:
        return render_template('msg2.html', msg='There is a Time collision for this Section')
    query = {"section_id": ObjectId(section_id), 'student_id': ObjectId(student_id), "date": date, "status": "Enrolled"}
    enrolment_collection.insert_one(query)
    return render_template("msg2.html", msg="Your Enrollment Successful")


@app.route("/view_enrolled")
def view_enrolled():
    section_id = request.args.get("section_id")
    print(section_id)
    query= {}
    if session['role'] == 'Professor':
        query = {"section_id": ObjectId(section_id)}
    elif session['role']== 'student':
        student_id = session['student_id']
        if section_id is None:
            query = {'student_id': ObjectId(student_id)}
        else:
           query = {'student_id': ObjectId(student_id), "section_id": ObjectId(section_id)}
    elif session['role'] =='admin':
        query = {"section_id": ObjectId(section_id)}
    enrolments = enrolment_collection.find(query)
    enrolments = list(enrolments)
    if len(list(enrolments)) == 0:
        return render_template("msg2.html",msg="You Did Not Enrolled Any Section",color='text-primary')
    return render_template('view_enrolled.html', enrolments=enrolments,get_departments_by_section_id=get_departments_by_section_id,get_student_by_student_id=get_student_by_student_id,get_sections_by_section_id=get_sections_by_section_id,get_professor_by_section_id=get_professor_by_section_id,get_room_by_section_id=get_room_by_section_id)


def get_student_by_student_id(student_id):
    query = {"_id": ObjectId(student_id)}
    students = student_collection.find_one(query)
    return students

def get_room_by_section_id(section_id):
    query = {"_id":ObjectId(section_id)}
    print(section_id)
    sections = sections_collection.find_one(query)
    print(sections)
    room_id = sections['room_id']
    room = room_collection.find_one(room_id)
    return room

def get_departments_by_section_id(section_id):
    query = {"_id": ObjectId(section_id)}
    print(section_id)
    sections = sections_collection.find_one(query)
    print(sections)
    department_id = sections['department_id']
    departments = department_collection.find_one(department_id)
    return departments


def get_sections_by_section_id(section_id):
    query = {"_id": ObjectId(section_id)}
    sections = sections_collection.find_one(query)
    return sections


def get_department_by_section_id(department_id):
    departments = department_collection.find({"_id":department_id})
    return departments


def get_assignment_submission_by_assignment_id(assignment_id):
    query = {"_id": ObjectId(assignment_id)}
    assignment = assignments_collection.find_one(query)
    print(assignment)
    assignment_submission = assignment_submission_collection.find_one({"assignment_submission_id":'assignment_submission_id'})
    return assignment_submission



def get_professor_by_section_id(Professor_id):
    professor = professor_collection.find_one({"_id":ObjectId(Professor_id)})
    return professor


@app.route("/drop_enrol")
def drop_enrol():
    enrolment_id = request.args.get("enrolment_id")
    query = {"_id":ObjectId(enrolment_id)}
    query2 ={"$set":{"enrolment_id": ObjectId(enrolment_id),"status":"Dropped"}}
    enrolment_collection.update_one(query,query2)
    return render_template("msg2.html", msg = "Enroll dropped successfully")


@app.route("/give_grade")
def give_grade():
    enrolment_id = request.args.get("enrolment_id")
    return render_template("give_grade.html",enrolment_id=enrolment_id)


@app.route("/give_grade_action",methods=['post'])
def give_grade_action():
    enrolment_id = request.form.get("enrolment_id")
    grade =  request.form.get("grade")
    query = {"_id": ObjectId(enrolment_id)}
    query2 = {"$set": {"enrolment_id": ObjectId(enrolment_id), "grade": grade,"status":'Grade Given'}}
    enrolment_collection.update_one(query, query2)
    return render_template("msg2.html", msg="Grade Given Successfully")


@app.route("/assignments")
def assignments():
    section_id = request.args.get("section_id")
    query = {}
    if section_id is None:
        Professor_id = session['Professor_id']
        query = {"Professor_id":ObjectId(Professor_id)}
        sections = sections_collection.find(query)
        sectionsIds = []
        for section in sections:
            sectionsIds.append(section['_id'])
        query = {"section_id":{"$in":sectionsIds}}
    else:
        query = {"section_id":ObjectId(section_id)}
    sections = sections_collection.find({})
    enrolment_id = request.args.get("enrolment_id")
    assignments = assignments_collection.find(query)
    submission_date = datetime.datetime.now()
    return render_template("assignments.html",str=str,submission_date=submission_date, assignments=assignments,datetime=datetime,enrolment_id=enrolment_id,sections=sections,section_id=section_id,get_section_by_section_id=get_section_by_section_id,is_student_submitted=is_student_submitted,get_assignment_submission_by_assignment_id=get_assignment_submission_by_assignment_id)


@app.route("/assign_assignment_marks")
def assign_assignment_marks():
    assignment_submission_id = request.args.get('assignment_submission_id')
    print(assignment_submission_id)
    return render_template("assign_assignment_marks.html", assignment_submission_id=ObjectId(assignment_submission_id))



def get_section_by_section_id(section_id):
    query = {"_id": ObjectId(section_id)}
    sections = sections_collection.find_one(query)
    return sections


# def get_professor_by_section_id(section_id):
#     query = {"_id": ObjectId(section_id)}
#     section = sections_collection.find_one(query)
#     print(section)
#     professors = professor_collection.find_one({"_id": ObjectId(section['Professor_id'])})
#     return professors


@app.route("/assignments1", methods=['post'])
def assignments1():
    section_id = request.form.get("section_id")
    assignment_title = request.form.get("assignment_title")
    assignment_pdf = request.files.get('assignment_pdf')
    path = APP_ROOT + "/" + assignment_pdf.filename
    assignment_pdf.save(path)
    submission_date = request.form.get("submission_date")
    submission_date = datetime.datetime.strptime(submission_date, "%Y-%m-%dT%H:%M")
    description = request.form.get('description')
    query = {'assignment_title': assignment_title, 'assignment_pdf': assignment_pdf.filename, 'submission_date': submission_date,'description': description ,"section_id": ObjectId(section_id),"status":'Assigned'}
    assignments_collection.insert_one(query)
    return redirect("assignments?section_id="+str(section_id))


@app.route("/assignment_submission", methods=['post'])
def assignment_submission():
    enrolment_id = request.form.get("enrolment_id")
    print(enrolment_id)
    assignment_id = request.form.get("assignment_id")
    assignment_upload = request.files.get("assignment_upload")
    path3 = APP_ROOT + "/" + assignment_upload.filename
    assignment_upload.save(path3)
    query = {'enrolment_id': ObjectId(enrolment_id), 'assignment_id': ObjectId(assignment_id)}
    assignment_submission_collection.delete_one(query)
    query = {'assignment_upload': assignment_upload.filename,  'date': datetime.datetime.now(),'enrolment_id': ObjectId(enrolment_id), 'assignment_id': ObjectId(assignment_id),'status': 'submitted'}
    assignment_submission_collection.insert_one(query)
    return render_template("msg2.html", msg="Assignment Uploaded Successful")


def is_student_submitted(assignment_id):
    student_id = session['student_id']
    query = {"assignment_id": assignment_id, "student_id": ObjectId(student_id),"status": 'submitted'}
    count = assignment_submission_collection.count_documents(query)
    if count == 0:
        return False
    else:
        return True


@app.route("/view_assignments")
def view_assignments():
    assignment_id = request.args.get('assignment_id')
    query = {'assignment_id': ObjectId(assignment_id)}
    if session['role'] == 'Student':
        query = {'assignment_id': ObjectId(assignment_id), "student_id": ObjectId(session['Student_id'])}
    assignment_submissions = assignment_submission_collection.find(query)
    return render_template("view_assignments.html", assignment_submissions=assignment_submissions, get_student_by_enrolment_id=get_student_by_enrolment_id)


def get_student_by_enrolment_id(enrolment_id):
    print(enrolment_id)
    query = {"_id":ObjectId(enrolment_id)}
    enrloments = enrolment_collection.find_one(query)
    print(enrloments)
    student_id = enrloments['student_id']
    students = student_collection.find_one(student_id)
    return students

@app.route("/assign_assignment_marks")
def assign_marks():
    assignment_submission_id = request.args.get('assignment_submission_id')
    print(assignment_submission_id)
    return render_template("assign_assignment_marks.html", assignment_submission_id=ObjectId(assignment_submission_id))


@app.route("/assign_assignment_marks1")
def assign_marks4():
    assignment_submission_id = request.args.get('assignment_submission_id')
    assign_marks = request.args.get('assign_marks')
    query = {"_id": ObjectId(assignment_submission_id)}
    query2 = {"$set": {'submission_id': ObjectId(assignment_submission_id), 'assign_marks': assign_marks,"status": "Marks Assigned"}}
    assignment_submission_collection.update_one(query, query2)
    return render_template("msg2.html", msg="Marks Added Successfully")

@app.route("/get_days")
def get_days():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    print(end_date)
    print(start_date)
    start_date  = datetime.datetime.strptime(start_date,"%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date,"%Y-%m-%d")
    days = []
    while start_date <= end_date:
        day = WEEK_DAYS[start_date.weekday()]
        if day not in days:  # Check for uniqueness
            days.append(day)
        start_date = start_date+datetime.timedelta(days=1)
    days = set(days)
    return render_template("get_days.html",days=days)


app.run(debug=True)

