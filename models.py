from flask import Flask, request
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mrinalandmutahar'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aptest.db'
app.config['CSRF_ENABLED'] = True
app.config['USER_ENABLE_EMAIL'] = True
app.config['USER_APP_NAME'] = 'AP_TEST'
app.config['USER_SEND_PASSWORD_CHANGED_EMAIL'] = False
app.config['USER_SEND_REGISTERED_EMAIL'] = False
app.config['USER_SEND_USERNAME_CHANGED_EMAIL'] = False
app.config['USER_ENABLE_CONFIRM_EMAIL'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
photos = UploadSet('photos',IMAGES)
configure_uploads(app, photos)

db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')	
    email = db.Column(db.String(255), nullable = False, unique=True)
    bio = db.Column(db.String(500), default="")
    dob = db.Column(db.String(11), server_default='-----------')
    role = db.Column(db.Boolean(), default=False)

class Answers(db.Model):
    Q_id = db.Column(db.Integer, primary_key = True)
    answer_option = db.Column(db.Integer)

class Score(db.Model, UserMixin):
    username = db.Column(db.String(50), primary_key = True)
    arithmetic_reasoning_score = db.Column(db.Integer, nullable=False, default=0)
    logical_reasoning_score = db.Column(db.Integer, nullable=False, default=0)
    english_score = db.Column(db.Integer, nullable=False, default=0)
    technical_score = db.Column(db.Integer, nullable=False, default=0)

class Questions(db.Model):
    Q_id = db.Column(db.Integer, primary_key=True)
    Question_name = db.Column(db.String(10000), nullable=False, unique=True)
    option1 = db.Column(db.String(1000), nullable=False)
    option2 = db.Column(db.String(1000), nullable=False)
    option3 = db.Column(db.String(1000), nullable=False)
    option4 = db.Column(db.String(1000), nullable=False)
    Topic_id = db.Column(db.Integer, nullable=False)

class Topic(db.Model):
    Topic_id = db.Column(db.Integer, primary_key=True)
    Topic_name = db.Column(db.String(100), nullable=False, unique=True)

class States(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    Topic_name = db.Column(db.String(100), nullable=False, server_default='tech')
    mainflag = db.Column(db.Boolean(), nullable=False, server_default='0')
    partialscore = db.Column(db.String(10), nullable=False, server_default='0')
    numofinc = db.Column(db.Integer, nullable=False, default=0)
    for i in range(10):
    	for j in range(4):
    		locals()['Q{}A{}'.format(i, j)] = db.Column(db.Boolean(), nullable=False, server_default='0')
    	locals()['Q{}'.format(i)] = db.Column(db.Boolean(), nullable=False, server_default='0') 

class MyModelView(ModelView):
	def is_accessible(self):
		if current_user.is_anonymous is not True:
			if current_user.role == True:
				return True
			return False
		return False

class MyAdminIndexView(AdminIndexView):
	def is_accessible(self):
		if current_user.is_anonymous is not True:
			if current_user.role == True:	
				return True
			return False
		return False

admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Questions, db.session))
admin.add_view(MyModelView(Answers, db.session))
admin.add_view(MyModelView(Score, db.session))

db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)

def init_db():
	db.init_app(app)
	db.drop_all()
	db.create_all()

def sortscore(category):
	result1 = db.engine.execute('SELECT username FROM Score')
	resultArithmetic = db.engine.execute('SELECT arithmetic_reasoning_score FROM Score')
	resultLogical = db.engine.execute('SELECT logical_reasoning_score  FROM Score')
	resultEnglish = db.engine.execute('SELECT english_score FROM Score')
	resultTechnical = db.engine.execute('SELECT technical_score FROM Score')
	dictionary={}
	name=[]
	for i in result1:
		name.append(i[0])

	score=[]	
	if category == 'globalrank':
		for i in resultArithmetic:
			score.append(i[0])

		j=0
		for i in resultLogical:
			score[j]+=i[0]
			j+=1
		j=0
		for i in resultEnglish:
			score[j]+=i[0]
			j+=1
		j=0
		for i in resultTechnical:
			score[j]+=i[0]
			j+=1
		for i in range(len(name)):
			dictionary[name[i]] = score[i]

		sorted_tuple = sorted(dictionary.items(), key=lambda x: (x[1], x[0]), reverse=True)
		return sorted_tuple
	
	else:
		for i in locals()['result' + str(category)]:
			score.append(i[0])

		for i in range(len(name)):
			dictionary[name[i]] = score[i]

		sorted_tuple = sorted(dictionary.items(), key=lambda x: (x[1], x[0]), reverse=True)
		return sorted_tuple

def addUsertoScore(user):
	if not Score.query.filter_by(username=user).first():
	    new_user_score = Score(username=user)
	    db.session.add(new_user_score)
	    db.session.commit()

def scoreupdate(scoredata):
	row = States.query.filter_by(username=current_user.username).first()
	if row != None:
		row.mainflag = False
	row = Score.query.filter_by(username=current_user.username).first()
	if scoredata['Topic_name'] == 'Arithmetic_reasoning':
		row.arrays_score += scoredata['score']
	elif scoredata['Topic_name'] == 'Logical_reasoning':
		row.linkedlist_score += scoredata['score']
	elif scoredata['Topic_name'] == 'English':
		row.trees_score += scoredata['score']
	elif scoredata['Topic_name'] == 'Technical':
		row.graphs_score += scoredata['score']
	db.session.commit()

def addstate(data):
	if not States.query.filter_by(username=current_user.username).first():
		new_user_state = States(username=current_user.username)
		db.session.add(new_user_state)
		db.session.commit()
	user_data = States.query.filter_by(username=current_user.username).first()
	for key, value in data.items():
		setattr(user_data, key, value)
		db.session.commit()
	user_data.mainflag=1
	db.session.commit()

def getdetails(username):
	rank = 0
	sorted_tuple = sortscore('globalrank')
	for i in sorted_tuple:
		rank = rank + 1	
		if i[0] == username:
			score = i[1]
			break
	
	return score, rank

def generateplay(category):
	result = db.engine.execute("SELECT * FROM Questions Q join Answers A on A.Q_id = Q.Q_id WHERE Topic_id in (Select Topic_id from Topic where Topic_name = '" + str(category) + "');")
	arr = []
	for i in result:
		arr.append(i)
	return arr

def update(request):
	newdob = request.form['newdob']
	newbio = request.form['newbio']
	if newdob!=None:
		current_user.dob=newdob
	if newbio!=None:
		current_user.bio=newbio
	db.session.commit() 
