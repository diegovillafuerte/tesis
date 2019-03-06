from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, func
from database_setup import Base, Company, Applicant, Job, MatchScore
from sqlalchemy.orm import sessionmaker
import random
import magic


engine = create_engine('postgres://localhost/simil')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def validateApplicant(mail, password):
	''' Validates whether or not the applicant exists in the 
		database and if the password is correct
		true = user exists and password is correct '''
	try:
		user = session.query(Applicant).filter(func.lower(Applicant.mail) == func.lower(mail), func.lower(Applicant.password) == func.lower(password)).scalar()
		if user:
			return True
		else:
			return False
	except Exception as e:
		print(e)
		return False

def validateMail(mail):
	''' Validates whether or not the company exists in the 
		database and if the password is correct
		true = user exists and password is correct '''
	try:
		company = session.query(Company).filter(func.lower(Company.mail) == func.lower(mail)).scalar()
		applicant = session.query(Applicant).filter(func.lower(Applicant.mail) == func.lower(mail)).scalar()
		if company or applicant:
			return True
		else:
			return False
	except Exception as e:
		print(e)
		return False

def validateCompany(mail, password):
	''' Validates whether or not the company exists in the 
		database and if the password is correct
		true = user exists and password is correct '''
	try:
		company = session.query(Company).filter(func.lower(Company.mail) == func.lower(mail), func.lower(Company.password) == func.lower(password)).scalar()
		if company:
			return True
		else:
			return False
	except Exception as e:
		print(e)
		return False

def getApplicantID(mail):
	''' Receives an email and returns an id. If the user does not exist, it returns 0 '''
	try:
		user = session.query(Applicant).filter(func.lower(Applicant.mail) == func.lower(mail)).one()
		#user = session.query(Applicant).filter(Applicant.mail == mail).one()
		id = user.id
		return id
	except Exception as e:
		print(e)
		return 0


def getCompanyID(mail):
	''' Receives an email and returns an id. If the company does not exist, it returns 0 '''
	try:
		company = session.query(Company).filter(func.lower(Company.mail) == func.lower(mail)).one()
		#user = session.query(Applicant).filter(Applicant.mail == mail).one()
		id = company.id
		return id
	except Exception as e:
		print(e)
		return 0


def createApplicant(name, mail, password):
	''' Given a name, an email address and a password, it creates an applicant in the database
		For every applicant it creates it calculates its match score with every job available'''
	try:
		appli = Applicant(name = name, mail = mail, password=password)
		session.add(appli)
		all_jobs = session.query(Job).all()
		applicant_id = session.query(Applicant).filter(Applicant.mail == mail).one().id
		for job in all_jobs:
			job_id = job.id
			createMatchScore(magic.matchScore(job_id, applicant_id), job_id, applicant_id)
		session.commit()
	except Exception as e:
		print(e)
		return render_template("main.html")
		flash("Lo sentimos, ocurrió un error en nuestro sistema, por favor vuelve a intentarlo.\
			Si el problema es persistente te pedimos que te pongas en contacto con nosotros")


def createCompany(name, mail, password, description):
	''' Given a name, mail, password and description, it creates a company in the database '''
	try:
		comp = Company(name = name, mail = mail, password = password, description = description)
		session.add(comp)
		session.commit()
	except Exception as e:
		print(e)
		return render_template("main.html")
		flash("Lo sentimos, ocurrió un error en nuestro sistema, por favor vuelve a intentarlo.\
			Si el problema es persistente te pedimos que te pongas en contacto con nosotros")


def createJob(title, salary, description, company_id, openings, status):
	''' Function for creating a job. Everytime you create one, it creates a match score with every 
		applicant available and adds it to the db'''
	try:
		trab = Job(title = title, salary = salary, description = description , company_id = company_id, openings=openings)
		session.add(trab)
		all_applicants = session.query(Applicant).all()
		job = session.query(Job).filter(Job.title == title, Job.company_id == company_id).one()
		job_id = job.id
		for applicant in all_applicants:
			applicant_id = applicant.id
			createMatchScore(magic.matchScore(job_id, applicant_id), job_id, applicant_id)
		session.commit()
	except Exception as e:
		print(e)
		return render_template("main.html")
		flash("Lo sentimos, ocurrió un error en nuestro sistema, por favor vuelve a intentarlo.\
			Si el problema es persistente te pedimos que te pongas en contacto con nosotros")

def createMatchScore(score, job_id, applicant_id):
	try:
		match = MatchScore(scores=score, job_id=job_id, applicant_id=applicant_id)
		session.add(match)
		session.commit()
	except Exception as e:
		print(e)
		return render_template("main.html")
		print("El error está en createMatchScore de dbOperations")
		flash("Lo sentimos, ocurrió un error en nuestro sistema, por favor vuelve a intentarlo.\
			Si el problema es persistente te pedimos que te pongas en contacto con nosotros")

def sendInfoToCompany(applicant_id, job_id):
	return True

def printDB():
	print("==============Applicants================")
	applicants = session.query(Applicant).all()
	for applicant in applicants:
		sal = str(applicant.id) +" - " + applicant.name +" - " + applicant.mail +" - " + applicant.password + "\n"
		print(sal)
	print("\n==============Companies===============")
	companies = session.query(Company).all()
	for company in companies:
		sal = str(company.id) +" - " + company.name +" - " + company.mail  +" - " + company.password + "\n"
		print(sal)
	print("\n==============Jobs===============")
	jobs = session.query(Job).all()
	for job in jobs:
		sal = str(job.id) +" - " + job.title +" - " + str(job.salary) +" - " + str(job.company_id)+" - " + str(job.openings) +" - " + str(job.status)+"\n"
		print(sal)
	print("\n==============Matches===============")
	matchscores = session.query(MatchScore).all()
	for match in matchscores:
		sal = "job: " + str(match.job_id) +" - " + "applicant: " + str(match.applicant_id)  +" - " + "Score: " + str(match.scores) + "\n"
		print(sal)

#Create a few users 
'''
user_names = ["Ana", "jose", "Pedro", "Joel", "Mariana", "Sofía"]
for user in user_names:
	mail = user + "@gmail.com"
	password = user + str(len(user))
	createApplicant(user, mail, password)


company_names = ["Transbarcos", "SuperLibros", "TodoMart", "DeportesExtreme", "BancoDeLaMeseta"]
for company in company_names:
	mail = "contacto@" + company + ".com"
	password = company + str(len(company))
	description = "Esta es una descripción genérica porque esto es un ejemplo"
	createCompany(company, mail, password, description)

job_titles = ["Cajero", "Asistente", "Vendedor", "servic", "Mesero"]
for title in job_titles:
	salary = len(title)*1423
	description = "Todas las job descriptions son identicas"
	company_id =  random.randint(1,5)
	openings = len(title)*4
	createJob(title, salary, description, company_id, openings, True)



#prints:
==============Applicants================
1 - Ana - Ana@gmail.com - Ana3

2 - jose - jose@gmail.com - jose4

3 - Pedro - Pedro@gmail.com - Pedro5

4 - Joel - Joel@gmail.com - Joel4

5 - Mariana - Mariana@gmail.com - Mariana7

6 - Sofía - Sofía@gmail.com - Sofía5


==============Companies===============
1 - Transbarcos - contacto@Transbarcos.com - Transbarcos11

2 - SuperLibros - contacto@SuperLibros.com - SuperLibros11

3 - TodoMart - contacto@TodoMart.com - TodoMart8

4 - DeportesExtreme - contacto@DeportesExtreme.com - DeportesExtreme15

5 - BancoDeLaMeseta - contacto@BancoDeLaMeseta.com - BancoDeLaMeseta15


==============Jobs===============
4 - Cajero - 8538.0 - 1 - 24 - True

5 - Asistente - 12807.0 - 5 - 36 - True

6 - Vendedor - 11384.0 - 1 - 32 - True

7 - servic - 8538.0 - 1 - 24 - True

8 - Mesero - 8538.0 - 4 - 24 - True


==============Matches===============
job: 4 - applicant: 1 - Score: 73

job: 4 - applicant: 2 - Score: 24

job: 4 - applicant: 3 - Score: 62

job: 4 - applicant: 4 - Score: 24

job: 4 - applicant: 5 - Score: 92

job: 4 - applicant: 6 - Score: 21

job: 5 - applicant: 1 - Score: 98

job: 5 - applicant: 2 - Score: 66

job: 5 - applicant: 3 - Score: 83

job: 5 - applicant: 4 - Score: 91

job: 5 - applicant: 5 - Score: 38

job: 5 - applicant: 6 - Score: 39

job: 6 - applicant: 1 - Score: 70

job: 6 - applicant: 2 - Score: 24

job: 6 - applicant: 3 - Score: 98

job: 6 - applicant: 4 - Score: 24

job: 6 - applicant: 5 - Score: 17

job: 6 - applicant: 6 - Score: 93

job: 7 - applicant: 1 - Score: 44

job: 7 - applicant: 2 - Score: 9

job: 7 - applicant: 3 - Score: 45

job: 7 - applicant: 4 - Score: 60

job: 7 - applicant: 5 - Score: 42

job: 7 - applicant: 6 - Score: 81

job: 8 - applicant: 1 - Score: 8

job: 8 - applicant: 2 - Score: 75

job: 8 - applicant: 3 - Score: 68

job: 8 - applicant: 4 - Score: 90

job: 8 - applicant: 5 - Score: 92

job: 8 - applicant: 6 - Score: 48
'''

#printDB()
