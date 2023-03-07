from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisIsSecret'
login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __int__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password
        self.authentificated = False

        def is_active(self):
            return self.is_active()

        def is_anonymous(self):
            return False

        def is_authenticated(self):
            return self.is_authenticated

        def is_active(self):
            return True

        def get_id(self):
            return self.id


@app.route('/enternew')
def new_student():
    return render_template('student.html')


@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            name = request.form['name']
            addr = request.form['add']
            city = request.form['city']

            with sqlite3.connect("students.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO students (name,addr,city) VALUES (?,?,?)", (name, addr, city))
                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"
        finally:
            con.close()
            return render_template("result.html", msg=msg)


@app.route('/liststudents')
def listStudents():
    con = sqlite3.connect("students.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()

    cur.execute("select * from students")

    rows = cur.fetchall()
    return render_template("studentlist.html", rows=rows)


@app.route('/')
def home():
    return render_template('home.html')


@app.route("/complete", methods=['POST', 'GET'])
def studentdeleted():
    if request.method == 'POST':
        try:
            name = request.form['name']
            print(name)

            with sqlite3.connect("students.db") as con:

                cur = con.cursor()
                cur.execute("DELETE FROM students WHERE name = ?;", (name,))
                con.commit()
                msg = "Record successfully deleted"

        except:
            con.rollback()
            msg = "error in deletion"


        finally:
            return delStudents()


@app.route('/delstudent')
@login_required
def delStudents():
    con = sqlite3.connect("students.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select * from students")

    rows = cur.fetchall()
    con.commit()
    return render_template("delstudents.html", rows=rows)


@app.route('/login', methods=['POST'])
def login_post():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

        # do the standard database stuff and find the user with email

    con = sqlite3.connect("login.db")

    curs = con.cursor()

    email = request.form['email']

    curs.execute("SELECT * FROM login where email = (?)", [email])

    # return the first matching user then pass the details to
    # create a User object – unless there is nothing returned then flash a message

    row = curs.fetchone()

    if row == None:
        flash('Please try logging in again')

        return render_template('login.html')

    user = list(row);

    liUser = User(int(user[0]), user[1], user[2])

    password = request.form['password']

    match = liUser.password == password

    # if our password matches run the login_user method

    if match and email == liUser.email:

        login_user(liUser, remember=request.form.get('remember'))

        redirect(url_for('home'))

    else:

        flash('Please try logging in again')

        return render_template('login.html')

    return render_template('home.html')


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('login.db')
    curs = conn.cursor()
    curs.execute("SELECT * from login where user_id = (?)", [user_id])
    liUser = curs.fetchone()
    if liUser is None:
        return None
    else:
        return User(int(liUser[0]), liUser[1], liUser[2])


if __name__ == '__main__':
    app.run(debug=True)
