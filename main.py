from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from database_setup import Base, Company, Applicant, Job, MatchScore
from sqlalchemy.orm import sessionmaker
import dbOperations, magic

engine = create_engine('postgres://localhost/simil')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def showMain():
    if request.method  == 'POST':
        mail = request.form['email']
        password = request.form['password']
        client_type = request.form['radiosTipodecliente']
        action = ""
        try:
            action = request.form['login']
        except:
            pass
        try:
            action = request.form['signup']
        except:
            pass
        if action == 'login':
            if client_type == "applicant":
                if dbOperations.validateApplicant(mail, password):
                    return redirect(url_for('showApplicant', applicant_id=dbOperations.getApplicantID(mail)))
                else:
                    flash("El correo o contraseña son incorrectos. Por favor intenta de nuevo")
            else:
                if dbOperations.validateCompany(mail, password):
                    return redirect(url_for('showCompany', company_id=dbOperations.getCompanyID(mail)))
                else:
                    flash("El correo o contraseña son incorrectos. Por favor intenta de nuevo")
        else:
            if client_type == "applicant":
                if dbOperations.validateApplicant(mail, password):
                    flash("Ya existe un aplicante registrado con ese correo y esa contraseña")
                else:
                    return redirect(url_for('newApplicant', app_mail=mail, app_password=password))
            else:
                if dbOperations.validateCompany(mail, password):
                    flash("Ya existe una compañía registrado con esos correo y contraseña")
                else:
                    return redirect(url_for('newCompany', mail = mail, password = password))
    return render_template("main.html")

@app.route('/applicant/new')
@app.route('/applicant/new/<string:app_mail>/<string:app_password>')
def newApplicant(app_mail="", app_password=""):
        return "This should show option to create a new applicant" + app_mail

@app.route('/company/new')
@app.route('/company/new/<string:mail>/<string:password>')
def newCompany(mail="", password=""):
        return "This should show option to create a new company" + mail

@app.route('/job/<int:company_id>/new')
def newJob(company_id):
        return "This should show option to create a new job"

@app.route('/company/<int:company_id>/feed')
def showCompany(company_id):
    try:
        jobs = session.query(Job).filter(Job.company_id == company_id).all()
        company = session.query(Company).filter(Company.id == company_id).one()
        return render_template("showCompany.html", jobs = jobs, company = company)
    except Exception as e:
        print(e)
        return render_template("main.html")

@app.route('/applicant/<int:applicant_id>/feed')
def showApplicant(applicant_id):
    try:
        matches = magic.getListOfMatchesForJob(job_id)
        print(type(matches))
        job = session.query(Job).filter(Job.id == job_id).one()
        company = session.query(Company).filter(Company.id == job.company_id).one()
        return render_template("showJob.html", matches = matches, job = job, company = company)
    except Exception as e:
        print(e)
        flash("Ocurrió un error, por favor intentalo de nuevo")
        return render_template("main.html")   

@app.route('/job/<int:job_id>/feed')
def showJob(job_id):
    try:
        matches = magic.getListOfMatchesForJob(job_id)
        print(type(matches))
        job = session.query(Job).filter(Job.id == job_id).one()
        company = session.query(Company).filter(Company.id == job.company_id).one()
        return render_template("showJob.html", matches = matches, job = job, company = company)
    except Exception as e:
        print(e)
        flash("Ocurrió un error, por favor intentalo de nuevo")
        return render_template("main.html")
    

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

@app.route('/job/<int:job_id>/<int:applicant_id>/interest')
def showInterestCompany(job_id, applicant_id):
    return"This should be the confirmation of a job interest by a company for job "+str(job_id)+ " in applicant " +str(applicant_id)


if __name__ == '__main__':
        app.secret_key = 'Super secret key'
        app.debug = True
        app.run(host='0.0.0.0', port=5000)