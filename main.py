import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from database_setup import Base, Company, Applicant, Job, MatchScore
from sqlalchemy.orm import sessionmaker
import dbOperations, magic
from werkzeug.utils import secure_filename

app = Flask(__name__)
#app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#UPLOAD_FOLDER = './static/cv'
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = create_engine('postgres://localhost/simil')
Base.metadata.bind = db

DBSession = sessionmaker(bind=db)
session = DBSession()

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
                if dbOperations.validateMail(mail):
                    flash("Ya existe un aplicante registrado con ese correo")
                else:
                    return redirect(url_for('newApplicant', app_mail=mail))
            else:
                if dbOperations.validateMail(mail):
                    flash("Ya existe una compañía registrado con ese correo")
                else:
                    return redirect(url_for('newCompany', mail = mail))
    return render_template("main.html")


@app.route('/applicant/new', methods=['GET', 'POST'])
@app.route('/applicant/new/<string:app_mail>', methods=['GET', 'POST'])
def newApplicant(app_mail=""):
    try:
        if request.method  == 'POST':
            mail = request.form['email']
            password = request.form['password']
            name = request.form['name']
            dbOperations.createApplicant(name, mail, password)
            applicantID = session.query(Applicant).filter(Applicant.mail == mail).one().id
            cv = request.files['file']

            #Guarda su CV en el folder static/cv con el nombre CV + el id del usuario
            filename = "CV" + str(applicantID) + ".pdf"
            cv.save(secure_filename(filename))

            return redirect(url_for('demoTestApplicant', applicant_id = applicantID))
        return render_template('signUpApplicant.html', mail = app_mail)
    except Exception as e:
        print(e)
        print("El error ocurrió en la función newApplicant de main.py")
        flash("Ocurrió un error, por favor intentalo de nuevo")
        return render_template("main.html")


@app.route('/applicant/new/demotest/<int:applicant_id>', methods=['GET', 'POST'])
def demoTestApplicant(applicant_id):
    try:
        if request.method  == 'POST':
            birthdate = request.form['date']
            zipcode = request.form['zipCode']
            gender = request.form['gender']
            civil = request.form['civil']
            dependientes = request.form['dependientes']
            estudios = request.form['estudios']
            dbOperations.addDemo(birthdate, zipcode, gender, civil, dependientes, estudios, applicant_id)
            return redirect(url_for('personalityTestApplicant', applicant_id = applicant_id))
        return render_template("demoApplicants.html", applicant_id = applicant_id)
    except Exception as e:
        print(e)
        print("El error ocurrió en la función demoTestApplicant de main.py")
        flash("Ocurrió un error, por favor intentalo de nuevo")
        return render_template("main.html")


@app.route('/applicant/new/perstest/<int:applicant_id>', methods=['GET', 'POST'])
def personalityTestApplicant(applicant_id):
    try:
        if request.method  == 'POST':
            aux = request.form.to_dict()
            dbOperations.addPersonality(aux, applicant_id)
            return redirect(url_for('mathTestApplicant', applicant_id = applicant_id))
        return render_template("personalityApplicants.html", applicant_id = applicant_id)
    except Exception as e:
        print(e)
        print("El error ocurrió en la función personalityTestApplicant de main.py")
        flash("Ocurrió un error, por favor intentalo de nuevo")
        return render_template("main.html")


@app.route('/applicant/new/mathtest/<int:applicant_id>', methods=['GET', 'POST'])
def mathTestApplicant(applicant_id):
    try:
        if request.method  == 'POST':
            aux = request.form.to_dict()
            dbOperations.addMath(aux, applicant_id)
            return redirect(url_for('showApplicant', applicant_id = applicant_id))
        return render_template("mathApplicants.html", applicant_id = applicant_id)
    except Exception as e:
        print(e)
        print("El error ocurrió en la función mathTestApplicant de main.py")
        flash("Ocurrió un error, por favor intentalo de nuevo")
        return render_template("main.html")


@app.route('/company/new', methods=['GET', 'POST'])
@app.route('/company/new/<string:mail>', methods=['GET', 'POST'])
def newCompany(mail="", password=""):
    try:
        if request.method  == 'POST':
            mail = request.form['email']
            password = request.form['up1']
            name = request.form['name']
            description = request.form['description']
            dbOperations.createCompany(name, mail, password, description)
            companyID = session.query(Company).filter(Company.mail == mail).one().id
            return redirect(url_for('showCompany', company_id = companyID))
        return render_template('signUpCompany.html', mail = mail)
    except Exception as e:
        print(e)
        print("El error ocurrión en la función newCompany de main.py")
        flash("Ocurrió un error, por favor intentalo de nuevo")
        return render_template("main.html")


@app.route('/job/<int:company_id>/new', methods=['GET', 'POST'])
def newJob(company_id):
    try:
        if request.method  == 'POST':
            title = request.form['title']
            description = request.form['description']
            openings = request.form['openings']
            salary = request.form['salary']
            activa = request.form['radiosactiva']
            status = False
            zipcode = request.form['zipcode']
            if activa == 'activa':
                status = True
            dbOperations.createJob(title, salary, description, company_id, openings, status, zipcode)
            job_id = session.query(Job).filter(Job.company_id == company_id, Job.title == title).one().id
            return redirect(url_for('demoTestJob', company_id = company_id, job_id = job_id))
        else:
            return render_template('createJob.html', company_id = company_id)
    except Exception as e:
        print(e)
        print("El error ocurrión en la función newJob de main.py")
        flash("Ocurrió un error, por favor intentalo de nuevo")
        return render_template("main.html")


@app.route('/job/new/demotest/<int:company_id>/<int:job_id>', methods=['GET', 'POST'])
def demoTestJob(company_id, job_id):
    try:
        if request.method  == 'POST':
            birthdate = request.form['date']
            zipcode = request.form['zipCode']
            gender = request.form['gender']
            civil = request.form['civil']
            dependientes = request.form['dependientes']
            estudios = request.form['estudios']
            dbOperations.addDemoJob(birthdate, zipcode, gender, civil, dependientes, estudios, company_id, job_id)
            return redirect(url_for('personalityTestJob', company_id = company_id, job_id = job_id))
        return render_template("demoJob.html", company_id = company_id, job_id = job_id)
    except Exception as e:
        print(e)
        print("El error ocurrió en la función demoTestJob de main.py")
        flash("Ocurrió un error, por favor intentalo de nuevo")
        return render_template("main.html")


@app.route('/job/new/perstest/<int:company_id>/<int:job_id>', methods=['GET', 'POST'])
def personalityTestJob(company_id, job_id):
    try:
        if request.method  == 'POST':
            aux = request.form.to_dict()
            dbOperations.addPersonalityJob(aux, company_id, job_id)
            return redirect(url_for('mathTestJob', company_id = company_id, job_id = job_id))
        return render_template("personalityJob.html", company_id = company_id, job_id = job_id)
    except Exception as e:
        print(e)
        print("El error ocurrió en la función personalityTestJob de main.py")
        flash("Ocurrió un error, por favor intentalo de nuevo")
        return render_template("main.html")


@app.route('/job/new/mathtest/<int:company_id>/<int:job_id>', methods=['GET', 'POST'])
def mathTestJob(company_id, job_id):
    try:
        if request.method  == 'POST':
            aux = request.form.to_dict()
            dbOperations.addMathJob(aux, job_id)
            return redirect(url_for('showCompany', company_id = company_id))
        return render_template("mathJob.html", company_id = company_id, job_id = job_id)
    except Exception as e:
        print(e)
        print("El error ocurrió en la función mathTestJob de main.py")
        flash("Ocurrió un error, por favor intentalo de nuevo")
        return render_template("main.html")


@app.route('/company/<int:company_id>/feed')
def showCompany(company_id):
    try:
        jobs = session.query(Job).filter(Job.company_id == company_id).all()
        company = session.query(Company).filter(Company.id == company_id).one()
        return render_template("showCompany.html", jobs = jobs, company = company)
    except Exception as e:
        print(e)
        print("El error ocurrió en showCompany de main.py")
        flash("Ocurrió un error, por favor vuelve a intentarlo")
        return render_template("main.html")


@app.route('/applicant/<int:applicant_id>/feed')
def showApplicant(applicant_id):
    try:
        matches = magic.getListOfMatchesForApplicant(applicant_id)
        applicant = session.query(Applicant).filter(Applicant.id == applicant_id).one()
        return render_template("showApplicant.html", matches = matches, applicant = applicant)
    except Exception as e:
        print(e)
        flash("Ocurrió un error, por favor intentalo de nuevo")
        return render_template("main.html")   


@app.route('/job/<int:job_id>/feed')
def showJob(job_id):
    try:
        matches = magic.getListOfMatchesForJob(job_id)
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
    try:
        offer = session.query(MatchScore).filter(MatchScore.job_id == job_id, MatchScore.applicant_id == applicant_id).one()
        offer.interest_job = True
        session.commit()
        applicant = session.query(Applicant).filter(Applicant.id == applicant_id).one()
        job = session.query(Job).filter(Job.id == job_id).one()
        companyId = job.company_id
        if dbOperations.sendInfoToCompany(applicant_id, job_id):
            return render_template('showInterestJob.html', company_id = companyId, applicant = applicant , job = job)
        else:
            print("El error ocurrión en la función showInterestJob de main.py")
            flash("Ocurrió un error, por favor intentalo de nuevo")
            return render_template("main.html")
    except Exception as e:
        print(e)
        print("El error ocurrión en la función showInterestJob de main.py")
        flash("Ocurrió un error, por favor intentalo de nuevo")
        return render_template("main.html")


@app.route('/applicant/<int:job_id>/<int:applicant_id>/interest')
def showInterestApplicant(job_id, applicant_id):
    try:
        offer = session.query(MatchScore).filter(MatchScore.job_id == job_id, MatchScore.applicant_id == applicant_id).one()
        offer.interest_applicant = True
        session.commit()
        #return"This should be the confirmation of a job interest by applicant "+str(applicant_id)+ " in job " +str(job_id)
        return render_template('showInterestApplicant.html', applicantID = applicant_id)
    except Exception as e:
        print(e)
        print("El error ocurrión en la función showInterestApplicant de main.py")
        flash("Ocurrió un error, por favor intentalo de nuevo")
        return render_template("main.html")


@app.route('/contact') 
def showContact():
    return render_template('contact.html')


@app.route('/about') 
def showAbout():
    return render_template('about.html')


@app.route('/company/<int:company_id>/myApplicants') 
def showMyApplicants(company_id):
    '''
    This function will take a company id and return a two dimensional list
    with all the jobs that company has posted followed by the applicants that
    have matched to it. For example:
    [[job1, applicant1, applicant2],
    [job2, applicant1, applicant3, applicant 6],
    [job3]
    [job4, applicant 2, applicant3, applicant4]]
    '''
    try:
        jobs_matches = []
        jobs = session.query(Job).filter(Job.company_id == company_id).all()
        for i in jobs:
            # create a list that starts with the job (as a job object) and follows with all of that jobs matches (as applicant objects)
            job = [i]
            matches = session.query(MatchScore).filter(MatchScore.job_id == i.id, MatchScore.interest_job == True)
            for j in matches:
                applicant = [session.query(Applicant).filter(Applicant.id == j.applicant_id).one(), j.scores]
                job.append(applicant)
            jobs_matches.append(job)
        company = session.query(Company).filter(Company.id == company_id).one()
        return render_template('myApplicants.html', jobsMatches = jobs_matches, company = company)
    except Exception as e:
        print(e)
        print("El error ocurrión en la función showMyApplicants de main.py")
        flash("Ocurrió un error, por favor intentalo de nuevo")
        return render_template("main.html")


if __name__ == '__main__':
    app.secret_key = "Está es mi llave super secreta"
    app.debug = True
    app.run()#(host='0.0.0.0', port=5000)