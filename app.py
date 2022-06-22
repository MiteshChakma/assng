from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlite3
# config app and DB
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///manage.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "tznl1Mmy2douDHDD5jnp"

db = SQLAlchemy(app)
print(db.engine.table_names())
migrate = Migrate(app, db)

conn= sqlite3.connect('manage.sqlite3')
print(conn)


# homepage route
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/show_all')
def show_all():
    return render_template('show_all.html', students=Students.query.all())


student_course = db.Table('student_course',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
)


# course details db
class Courses(db.Model):
    __tablename__ = 'courses'
    id = db.Column( db.Integer, primary_key=True)
    cname = db.Column(db.String(100), )
    cnumber = db.Column(db.String(50), unique= True)
    cdetails = db.Column(db.String(100))
    sdate = db.Column(db.String(50))
    edate = db.Column(db.String(50))
    students = db.relationship("Students", secondary=student_course, back_populates='courses')

    def __init__(self, cname, cnumber, cdetails, sdate, edate):
        self.cname = cname
        self.cnumber = cnumber
        self.cdetails = cdetails
        self.sdate = sdate
        self.edate = edate


# Student details db
class Students(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.String(50))
    email = db.Column(db.String(100))
    city = db.Column(db.String(50))
    address = db.Column(db.String(500))
    courses = db.relationship("Courses", secondary=student_course, back_populates="students")
    assingment = db.Column(db.String(500))

    def __init__(self, name, age, email, city, address):
        self.name = name
        self.age = age
        self.email = email
        self.city = city
        self.address = address


# Add student details route
@app.route('/add_student_details', methods=['GET', 'POST'])
def add_student_details():
    if request.method == 'POST':
        if not request.form['name'] or not request.form['age'] or not request.form['email'] or not request.form['city'] or not request.form['addr']:
            return redirect(url_for('home'))
        else:

            student = Students(request.form['name'], request.form['age'], request.form['email'], request.form['city'], request.form['addr'])

            db.session.add(student)
            db.session.commit()

            return redirect(url_for('home'))
    return render_template('add_student_details.html')


#add course details route
@app.route('/add_course_details', methods=['GET', 'POST'])
def add_course_details():
    if request.method == 'POST':
        if not request.form['cname'] or not request.form['cnumber'] or not request.form['cdetails'] or not request.form['sdate'] or not request.form['edate']:
            return redirect(url_for('home'))
        else:

            course = Courses(request.form['cname'], request.form['cnumber'].lower(), request.form['cdetails'], request.form['sdate'], request.form['edate'])

            db.session.add(course)
            db.session.commit()

            return redirect(url_for('home'))
    return render_template('add_course_details.html')


#Enroll students
@app.route('/enroll_students/', methods=['GET', 'POST'])
def enroll_students():
    if request.method == 'POST':
        if not request.form['course'] or not request.form['student']:
            return "Not valid"
        else:
            student_id = request.form["student"]
            # print(id)
            course_id = request.form['course']
            # print(course)
            student = Students.query.get(student_id)
            course = Courses.query.get(course_id)
            course.students.append(student)
            db.session.add(course)
            db.session.commit()
            print(f'{course_id}: {course.students}')
            print(f'{student_id}: {student.courses}')
            #print(student_course.get_children())

            return redirect(url_for('home'))

    return render_template('enroll_students.html', courses=Courses.query.all(), students=Students.query.all())




@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        print(request.form)
        if (request.form['search']== 'student'):
            id = int(request.form['search_field'])
            student = Students.query.get(id)
            return render_template('search.html',  courses = student.courses)

        elif (request.form['search']== 'course'):
            id = request.form['search_field']

            course = Courses.query.filter(Courses.cnumber==id).first()
            print( course)
            return render_template('search.html',  students=course.students)


    return render_template('search.html')


@app.route('/Update_Student/<id>', methods=['GET', 'POST'])
def Update_Student(id):
    print(id)
    student = Students.query.get(id)

    if request.method == 'POST':
        if not request.form['name'] or not request.form['age'] or not request.form['email'] or not request.form['city'] or not request.form['addr']:
            return redirect(url_for('home'))
        else:

            student.name, student.age, student.email, student.city, student.addr = request.form['name'], request.form['age'], request.form['email'], request.form['city'], request.form['addr']


            course = Courses.query.get(int(request.form['course']))

            student.courses.append(course)
            db.session.add(student)
            db.session.commit()

            return redirect(url_for('home'))

    return render_template('Update_Student.html', student=student, courses = Courses.query.all())

@app.route('/delete/<sid>/<cidx>/', methods=['GET', 'POST'])
def delete(sid, cidx):
    student = Students.query.get(sid)
    # if request.method == 'POST':
    del student.courses[int(cidx)]
    print(f'courses::: {student.courses}')
    db.session.add(student)
    db.session.commit()
    return render_template('Update_Student.html', student=student, courses=Courses.query.all())



def connect_db():
 return sqlite3.connect(app.database)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
