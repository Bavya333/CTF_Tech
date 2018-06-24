from flask import Flask, render_template, request, flash, redirect, session, logging, url_for
from flask_mysqldb import MySQL
from wtforms import Form, StringField, PasswordField, TextAreaField, validators
from passlib.hash import sha256_crypt
#from MySQLdb import escape_string as thwart
from functools import wraps
import datetime
import time

app=Flask(__name__)

#config MySQL
app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] ='root'
app.config['MYSQL_PASSWORD'] ='******'
app.config['MYSQL_DB'] ='Project_1'
app.config['MYSQL_CURSORCLASS'] ='DictCursor'

#init MySQL
mysql= MySQL(app)

@app.route('/')
def home():
	return render_template('home.html')

class RegisterForm(Form):
	name = StringField('Name',[validators.Length(min=1,max=50)])
	username = StringField('UserName',[validators.Length(min=4,max=25)])
	email = StringField('Email',[validators.Length(min=10,max=50)])
	contact = StringField('Contact',[validators.Length(min=10,max=50)])
	password = PasswordField('Password',
		 [validators.DataRequired(),
		 validators.EqualTo('confirm',message='Passwords do not match')]
	)
	confirm = PasswordField('Confirm Password')

@app.route('/register/',methods=['GET','POST'])
def register():
	form =RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name=form.name.data
		username=form.username.data
		email=form.email.data
		contact=form.contact.data
		password=sha256_crypt.encrypt(str(form.password.data))

		cur=mysql.connection.cursor()
		x = cur.execute("SELECT * FROM user WHERE username = (%s)",
                          [username])

        	if int(x) > 0:
			flash("That username is already taken, please choose another")
		else:
			cur.execute("INSERT INTO user(name,username,password,email,contact_no) values(%s,%s,%s,%s,%s)",(name,username,password,email,contact))
			mysql.connection.commit()
			cur.close()
			flash("You are now registered and can now login!")
			return redirect(url_for('login'))
	return render_template('register.html',form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
        	# Get Form Fields
        	username = request.form['username']
        	password_candidate = request.form['password']

        	# Create cursor
        	cur = mysql.connection.cursor()

        	# Get user by username
        	result = cur.execute("SELECT * FROM user WHERE username = %s", [username])

        	if result > 0:
        		# Get stored hash
        	    	data = cur.fetchone()
            		password = data['password']

            		# Compare Passwords
            		if sha256_crypt.verify(password_candidate, password):
                		# Passed
                		session['logged_in'] = True
                		session['username'] = username
				flash('You are now logged in', 'success')
				result=cur.execute("SELECT qns_completed FROM user WHERE username = %s", [username])
				data=cur.fetchone()
				qns=data['qns_completed']
				qns=int(qns)+1
				if qns>4:
					return redirect(url_for('finish'))
				s1='qn'
			        return redirect(url_for(s1+`qns`))
          		else:
                		error = 'Invalid login'
               			return render_template('login.html', error=error)
            		# Close connection
            		cur.close()
        	else:
            		error = 'Username not found'
            		return render_template('login.html', error=error)

    	return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
	@wraps(f)
    	def wrap(*args, **kwargs):
	        if 'logged_in' in session:
        		return f(*args, **kwargs)
        	else:
            		flash('Unauthorized, Please login', 'danger')
        	    	return redirect(url_for('login'))
    	return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
    	flash('You are now logged out', 'success')
	return redirect(url_for('login'))

@app.route('/qn1', methods=['GET','POST'])
@is_logged_in
def qn1():
  	if request.method == 'POST':
		ans=request.form['ans1']
		s1="Mariana Trench"
		if ans == s1:
			cur = mysql.connection.cursor()
			cur.execute('update user set qns_completed = %s where username = %s',(1,session['username']))
			now = datetime.datetime.now()
			cur.execute('update user set submission_date = %s where username=%s',(now.strftime("%Y-%m-%d %H:%M:%S"),session['username']))

			cur.execute('update user set submission_time=%s where username=%s',(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),session['username']))

			mysql.connection.commit()
			return redirect(url_for('qn2'))
		else:
			flash('Wrong Answer!','danger')
	return render_template('qn1.html')

@app.route('/qn2', methods=['GET','POST'])
@is_logged_in
def qn2():
	if request.method == 'POST':
		ans=request.form['ans2']
		s1="Pamukkale"
		if ans == s1:
			cur = mysql.connection.cursor()
			cur.execute('update user set qns_completed = %s where username = %s',(2,session['username']))
			cur.execute('update user set submission_time=%s where username=%s',(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),session['username']))
			mysql.connection.commit()
			return redirect(url_for('qn3'))
		else:
			flash('Wrong Answer!','danger')
	return render_template('qn2.html')

@app.route('/qn3',methods=['GET','POST'])
@is_logged_in
def qn3():
	if request.method == 'POST':
		ans=request.form['ans3']
		s1="Hollywood"
		if ans == s1:
			cur = mysql.connection.cursor()
			cur.execute('update user set qns_completed = %s where username = %s',(3,session['username']))
			cur.execute('update user set submission_time=%s where username=%s',(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),session['username']))
			mysql.connection.commit()
			return redirect(url_for('qn4'))
		else:
			flash('Wrong Answer!','danger')
	return render_template('qn3.html')

@app.route('/qn4')
@is_logged_in
def qn4():
	return render_template('qn4.html')

@app.route('/taylorswift',methods=['GET'])
@is_logged_in
def taylor():
		cur = mysql.connection.cursor()
		cur.execute('update user set qns_completed = %s where username = %s',(4,session['username']))
		cur.execute('update user set submission_time=%s where username=%s',(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),session['username']))
		mysql.connection.commit()
		return redirect(url_for('finish'))

@app.route('/finish')
@is_logged_in
def finish():
	return render_template('finish.html')

@app.route('/dashboard')
@is_logged_in
def dashboard():
	cur=mysql.connection.cursor()
	result=cur.execute("SELECT qns_completed FROM user WHERE username = %s",[session['username']])
	data=cur.fetchone()
	qns=data['qns_completed']
	return render_template('dashboard.html',data=qns)

@app.route('/leaderboard')
@is_logged_in
def leaderboard(methods=['GET','POST']):
	cur=mysql.connection.cursor()
	result=cur.execute('Select * from user order by qns_completed desc,submission_time asc');
	data=cur.fetchall();
	return render_template('leaderboard.html', data=data)

if '__main__'==__name__:
	app.secret_key='secret123'
	app.run(debug=True)
