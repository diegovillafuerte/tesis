from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from database_setup import Base, Company, Applicant, Job
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgres://localhost/simil')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

@app.route('/')
@app.route('/main')
def showMain():
	quer = session.query(Applicant).one()
	sal = str(quer.id) +" - " + quer.name +" - " + quer.mail + "\n"
	quer = session.query(Company).one()
	sal1 = str(quer.id) +" - " + quer.name +" - " + quer.description + "\n"
	quer = session.query(Job).one()
	sal2 = str(quer.id) +" - " + quer.title +" - " + quer.description +" - " + quer.company.name
	return render_template("main.html")

@app.route('/applicant/new')
def newApplicant():
	appli = Applicant(name = 'Diego', mail = 'diegovillafuertesoraiz@gmail.com', password='Holisima')
	session.add(appli)
	session.commit()
	return "This should show option to create a new applicant"

@app.route('/company/new')
def newCompany():
	comp = Company(name = "Mongoles SA de CV", mail = "claudiam@mongoles.com", password = "mongolessa", description = "Somos una compañía de comercio internacional especializada en el mercado astiático")
	session.add(comp)
	session.commit()
	return "This should show option to create a new company"

@app.route('/job/<int:company_id>/new')
def newJob(company_id):
	trab = Job(title = "CEO", salary = 1000000, description = "In this role you will lead the team" , company_id = company_id)
	session.add(trab)
	session.commit()
	return "This should show option to create a new job"

@app.route('/company/<int:company_id>/feed')
def showCompany(company_id):
    return "This should show the feed for a company"

@app.route('/applicant/<int:applicant_id>/feed')
def showApplicant(applicant_id):
    return "This should show the feed for an applicant"

@app.route('/job/<int:job_id>/feed')
def showJob(job_id):
    return "This should show the feed for a job posting"

@app.route('/applicant/<int:applicant_id>/edit')
def editApplicant(applicant_id):
    return "This should show the option to edit an applicant's information"

@app.route('/applicant/<int:applicant_id>/delete')
def deleteApplicant(applicant_id):
    return "This should show the option to delete an applicant's information"

@app.route('/company/<int:company_id>/edit')
def editCompany(company_id):
    return "This should show the option to edit a company's information"

@app.route('/company/<int:company_id>/delete')
def deleteCompany(company_id):
    return "This should show the option to delete a company's information"

@app.route('/job/<int:job_id>/edit')
def editJob(job_id):
    return "This should show the option to edit a job's information"

@app.route('/job/<int:job_id>/delete')
def deleteJob(job_id):
    return "This should show the option to delete a job's information"


if __name__ == '__main__':
	app.secret_key = 'Super secret key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)