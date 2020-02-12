from flask import Flask,flash, render_template,request,redirect,url_for,session,Response # For flask implementation
from flask_login import login_manager, login_required, logout_user,LoginManager,current_user
from bson import ObjectId # For ObjectId to work
from pymongo import MongoClient
import os
import pandas as pd
import json
import grade
import pymongo
app = Flask(__name__)

scrt_key=os.urandom(12).hex()
app.secret_key = scrt_key

title = ""
heading = "Student Performance Prediction System"

client = MongoClient("mongodb://127.0.0.1:27017") #host uri
db = client.mymongodb    #Select the database
stu_col = db.student #Select the collection name

data = pd.read_csv('data/Edu.csv')
data_json = json.loads(data.to_json(orient='records'))
stu_col.remove()
stu_col.insert(data_json)


login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def user_loader(username):
    if username is not None:
        return User.query.get(username)
    return None

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('username', None)
    return redirect('/')

# @app.after_request
# def after_request(response):
    
    # return response

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    stu_col_l = stu_col.find({"done":"no"})
    if current_user.is_authenticated:  # already logged in
        return redirect('/index')
    if request.method == 'POST':
        
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect('/index')
    return render_template('login.html', error=error,stu_col=stu_col_l,t="Login",h=heading)
 
@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect('/')
 
def redirect_url():
    return request.args.get('next') or \
           request.referrer or \
           url_for('index')
           

@app.route("/list")
def lists ():
	#Display the all Tasks
	stu_col_l = stu_col.find()
	a1="active"
	return render_template('view_all.html',a1=a1,stu_col=stu_col_l,t="All Students",h=heading)
    
@app.route("/index")
@app.route("/uncompleted")

def tasks ():
	#Display the Uncompleted Tasks
	stu_col_l = stu_col.find({"done":"no"})
	a2="active"
	return render_template('index.html',a2=a2,stu_col=stu_col_l,t=title,h=heading)


@app.route("/at_risk")
def at_risk_chart ():
    #Pie Chart
    nums = stu_col.count()
    cursor=stu_col.aggregate([{"$group":{"_id": {"Class":  "$Class"} ,"count": { "$sum": 1 }}},{ "$project": { "count": 1 }}])
    values=[]
    legend=['Percentage of Students in each Grade Class']
    colors = ['#80aaff','#bfbfbf','#99ccff']
    labels=['Low','Medium','High']
    for result_object in cursor:
        values.append(result_object['count']) 
    stu_col_l = stu_col.find()
    c1=stu_col.aggregate([{ "$match" : { "Class" : "L" } } ,{"$group":{"_id": {"Gender":  "$Gender"} ,"count_1": { "$sum": 1 }}},{ "$project": { "count_1": 1, }}])
    values_1=[]
    labels_b=['F','M']
    colors_b = ['#ffffb3','#d9ffb3']
    for result_object in c1:
        values_1.append(result_object['count_1'])
    return render_template('at_risk.html',stu_col=stu_col_l,labels=labels,legend=legend,values=values,colors=colors,colors_b=colors_b,t="At-Risk Students",h=heading,values_1=values_1,labels_b=labels_b)


@app.route("/action", methods=['POST'])
def action ():
    #Adding a Task
    gender=request.values.get("Gender",type=str)
    nationality=request.values.get("Nationality",type=str)
    birth=request.values.get("PlaceofBirth",type=str)
    StageID=request.values.get("StageID",type=str)
    GradeID=request.values.get("GradeID",type=str)
    Section=request.values.get("SectionID",type=str)
    Topic=request.values.get("Topic",type=str)
    Semester=request.values.get("Semester",type=str)
    parent=request.values.get("Relation",type=str)
    haindraised=request.values.get("raisedhands",type=int)
    resources=request.values.get("VisitedResources",type=int)
    announcements=request.values.get("AnnouncementsView",type=int)
    discussion=request.values.get("Discussion",type=int)
    survey=request.values.get("ParentAnsweringSurvey",type=str)
    satisfy=request.values.get("ParentschoolSatisfaction",type=str)
    absent=request.values.get("StudentAbsenceDays",type=str)
    X_test = pd.DataFrame({"Gender":[gender], "Nationality":[nationality], "PlaceofBirth":[birth], "StageID":[StageID], "GradeID":[GradeID],"SectionID":[Section],"Topic":[Topic],"Semester":[Semester],"Relation":[parent],"raisedhands":[haindraised],"VisitedResources":[resources],"AnnouncementsView":[announcements],"Discussion":[discussion],"ParentAnsweringSurvey":[survey],"ParentschoolSatisfaction":[satisfy],"StudentAbsenceDays":[absent]})
    predicted_class=grade.predict_class(X_test)
    stu_col.insert({ "Gender":gender, "Nationality":nationality, "PlaceofBirth":birth, "StageID":StageID, "GradeID":GradeID,"SectionID":Section,"Topic":Topic,"Semester":Semester,"Relation":parent,"raisedhands":haindraised,"VisitedResources":resources,"AnnouncementsView":announcements,"Discussion":discussion,"ParentAnsweringSurvey":survey,"ParentschoolSatisfaction":satisfy,"StudentAbsenceDays":absent,"Class":predicted_class})
    cursor = stu_col.find({})
    # Expand the cursor and construct the DataFrame
    df =  pd.DataFrame(list(cursor))
    df.to_csv('data/Edu.csv')
    return redirect("/list")

@app.route("/remove")
def remove ():
	#Deleting a Task with various references
    key=request.values.get("_id")
    stu_col.remove({"_id":ObjectId(key)})
    cursor=stu_col.find({})
    df=pd.DataFrame(list(cursor))
    df.to_csv('data/Edu.csv')
    return redirect("/list")

@app.route("/update")
def update ():
	id=request.values.get("_id")
	task=stu_col.find({"_id":ObjectId(id)})
	return render_template('update.html',t="Update Student Information",tasks=task,h=heading)

@app.route("/action3", methods=['POST'])
def action3 ():
	#Updating a Task with various referenc
    gender=request.values.get("Gender",type=str)
    nationality=request.values.get("Nationality",type=str)
    birth=request.values.get("PlaceofBirth",type=str)
    StageID=request.values.get("StageID",type=str)
    GradeID=request.values.get("GradeID",type=str)
    Section=request.values.get("SectionID",type=str)
    Topic=request.values.get("Topic",type=str)
    Semester=request.values.get("Semester",type=str)
    parent=request.values.get("Relation",type=str)
    haindraised=request.values.get("raisedhands",type=int)
    resources=request.values.get("VisitedResources",type=int)
    announcements=request.values.get("AnnouncementsView",type=int)
    discussion=request.values.get("Discussion",type=int)
    survey=request.values.get("ParentAnsweringSurvey",type=str)
    satisfy=request.values.get("ParentschoolSatisfaction",type=str)
    absent=request.values.get("StudentAbsenceDays",type=str)
    id=request.values.get("_id")
    stu_col.update({"_id":ObjectId(id)},{'$set':{"Gender":gender, "Nationality":nationality, "PlaceofBirth":birth, "StageID":StageID, "GradeID":GradeID,"SectionID":Section,"Topic":Topic,"Semester":Semester,"Relation":parent,"raisedhands":haindraised,"VisitedResources":resources,"AnnouncementsView":announcements,"Discussion":discussion,"ParentAnsweringSurvey":survey,"ParentschoolSatisfaction":satisfy,"StudentAbsenceDays":absent}})
    cursor = stu_col.find({})
    # Expand the cursor and construct the DataFrame
    df =  pd.DataFrame(list(cursor))
    df.to_csv('data/Edu.csv')
    return redirect("/list")

@app.route("/search", methods=['GET'])
def search():
	#Searching a Task with various references

	key=request.values.get("key")
	refer=request.values.get("refer")
	if(key=="_id"):
		stu_col_l = stu_col.find({refer:ObjectId(key)})
	else:
		stu_col_l = stu_col.find({refer:key})
	return render_template('searchlist.html',stu_col=stu_col_l,t="Search Student Information",h=heading)

if __name__ == "__main__":

    app.run()
