import os
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask import Flask, render_template, request, redirect
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter, current_user
from models import *
import json

@app.route('/home')
def index():
	return render_template('home.html')

@app.route('/')
@login_required
def profile():
    addUsertoScore(current_user.username)
    return render_template('dashboard.html', currentuser=current_user.username)

@app.route('/recievefromjs', methods=['POST', 'GET'])
@login_required
def recieve():
	data = request.get_json(force=True)
	addstate(data)	
	return "Great"

@app.route('/profile/<user>')
@login_required
def userprofile(user):
    row = User.query.filter_by(username=user).first()
    score_row = Score.query.filter_by(username=user).first()
    score, rank=getdetails(user)
    return render_template('userprofile.html', username=user, rank=rank, score=score, mail=row.email, ide=row.id, dob=row.dob,
		arithmetic=score_row.arithmetic_reasoning_score, logical = score_row.logical_reasoning_score,
		english=score_row.english_score, technical=score_row.technical_score,
		currentuser=current_user.username
		)

@app.route('/edit_profile')
@login_required
def edit_profile():
	return render_template('edit_profile.html', bio=current_user.bio, dob=current_user.dob, currentuser=current_user.username)

@app.route('/submit_profile', methods=['POST'])
@login_required
def submit_profile():
	update(request)
	return redirect('/')

@app.route('/updatescore', methods=['GET', 'POST'])
@login_required
def updatescore():
	scoredata = request.get_json(force=True)
	scoreupdate(scoredata)
	return ""
    
@app.route('/quiz/<category>')
@login_required
def play(category):
	listoftuples = generateplay(category)
	dlist = [list(elem) for elem in listoftuples]
	return render_template('play.html', array=dlist, category=category, currentuser=current_user.username)	

@app.route('/upload', methods = ['GET', 'POST'])
@login_required
def upload():
	if request.method == 'POST' and 'photo' in request.files:
		filename = photos.save(request.files['photo'])
		os.rename('./static/img/'+ str(filename),
				  './static/img/' + str(current_user.id) + ".jpg")
		return redirect('/')
	else: 
		return 'please select a file'

@app.errorhandler(404)
def custom404(error):
	return render_template('custom404.html')

if __name__ == '__main__':
	if User.query.filter_by(username="Admin").first(): 
		pass
	else:
		db.session.add(User(username="Admin", password="$2b$12$fjywq4d3jXU0y3JI3Z8RHuqaKEaRutaPrfwQE25cja1h3AE6qGbda",
				email='admin@gkuiz.com', role=True, active=True)
			)
		db.session.commit()
	app.run(debug=True)
