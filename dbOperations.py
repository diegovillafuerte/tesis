import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, func
from database_setup import Base, Company, Applicant, Job, MatchScore
from sqlalchemy.orm import sessionmaker
import random
import magic
import math


db_user = os.environ['db_user']
db_pass = os.environ['db_pass']
db_host = os.environ['db_host']
db_port = os.environ['db_port']

db = create_engine("postgresql+psycopg2://{}:{}@{}:{}/{}?sslmode=require".format(db_user, db_pass, db_host, db_port, 'postgres'))
Base.metadata.bind = db

DBSession = sessionmaker(bind=db)
session = DBSession()


def addDemo(birthdate, zipcode, gender, civil, dependientes, estudios, applicant_id):
	try:
		#distTot es el número de días entre 01/01/1900 y la fecha de nacimiento del aplicante
		distYears = (int(birthdate[6:10]) - 1900) * 365
		distMonth = (int(birthdate[3:5]) - 1) * 30
		distDays = (int(birthdate[0:2]))
		distTot = distYears + distMonth + distDays

		#zipc es el código postal como entero con un 1 añadido al principio para mantener los 0 iniciales
		zipc = int('1' + zipcode[0:6])

		#gen es el código de género con un 1 añadido al principio para mantener los 0 iniciales
		gen = int('1' + gender)

		# civ es el código de estado civil con un 1 añadido al principio para mantener los 0 iniciales
		civ = int('1' + civil)

		# dep es el número de dependientes económicos como entero
		dep = int(dependientes)

		# est es el código de estudios con un 1 añadido al principio para mantener los 0 iniciales
		est = int('1' + estudios)

		# demo es el arreglo con todos los valores del test demográfico
		demo = [distTot, zipc, gen, civ, dep, est]		

		# Se agrega a la base de datos en el usuario que ya fue creado
		aplicante = session.query(Applicant).filter(Applicant.id == applicant_id).one()
		aplicante.demografico = demo
		session.commit()
	except Exception as e:
		print(e)
		print("El error ocurrió en la función addDemo de dbOperations.py")


def addDemoJob(birthdate, zipcode, gender, civil, dependientes, estudios, company_id, job_id):
	try:
		#distTot es el número de días entre 01/01/1900 y la fecha de nacimiento del aplicante
		distYears = (int(birthdate[6:10]) - 1900) * 365
		distMonth = (int(birthdate[3:5]) - 1) * 30
		distDays = (int(birthdate[0:2]))
		distTot = distYears + distMonth + distDays

		#zipc es el código postal como entero con un 1 añadido al principio para mantener los 0 iniciales
		zipc = int('1' + zipcode[0:6])

		#gen es el código de género con un 1 añadido al principio para mantener los 0 iniciales
		gen = int('1' + gender)

		# civ es el código de estado civil con un 1 añadido al principio para mantener los 0 iniciales
		civ = int('1' + civil)

		# dep es el número de dependientes económicos como entero
		dep = int(dependientes)

		# est es el código de estudios con un 1 añadido al principio para mantener los 0 iniciales
		est = int('1' + estudios)

		# demo es el arreglo con todos los valores del test demográfico
		demo = [distTot, zipc, gen, civ, dep, est]		

		# Se agrega a la base de datos en el usuario que ya fue creado
		job = session.query(Job).filter(Job.id == job_id, Job.company_id == company_id).one()
		nuevo = job.demografico
		if nuevo is not None:
			nuevo.append(demo)
			session.query(Job).filter(Job.id == job_id, Job.company_id == company_id).update({"demografico":nuevo})
			session.commit()
		else:
			job.demografico = [demo]
			session.commit()
	except Exception as e:
		print(e)
		print("El error ocurrió en la función addDemoJob de dbOperations.py")


def addPersonality(response, applicant_id):
	try:
		# Calculate Factor I Surgency or Extraversion
		f1 = 0
		f1 = f1 + int(response['p1'])
		f1 = f1 - int(response['p6'])
		f1 = f1 + int(response['p11'])
		f1 = f1 - int(response['p16'])
		f1 = math.floor((f1 + 8)*100/16)

		# Calculate Factor II Agreeableness 
		f2 = 0
		f2 = f2 + int(response['p2'])
		f2 = f2 - int(response['p7'])
		f2 = f2 + int(response['p12'])
		f2 = f2 - int(response['p17'])
		f2 = math.floor((f2 + 8)*100/16)

		# Calculate Factor III Conscientiousness
		f3 = 0
		f3 = f3 + int(response['p3'])
		f3 = f3 - int(response['p8'])
		f3 = f3 + int(response['p13'])
		f3 = f3 - int(response['p18'])
		f3 = math.floor((f3 + 8)*100/16)

		# Calculate Factor IV Neuroticism
		f4 = 0
		f4 = f4 + int(response['p4'])
		f4 = f4 - int(response['p9'])
		f4 = f4 + int(response['p14'])
		f4 = f4 - int(response['p19'])
		f4 = math.floor((f4 + 8)*100/16)

		# Calculate Factor V Intellect or Imagination
		f5 = 0
		f5 = f5 + int(response['p5'])
		f5 = f5 - int(response['p10'])
		f5 = f5 - int(response['p15'])
		f5 = f5 - int(response['p20'])
		f5 = math.floor((f5 + 14)*100/16)

		resp = [f1, f2, f3, f4, f5]
		aplicante = session.query(Applicant).filter(Applicant.id == applicant_id).one()
		aplicante.personalidad = resp
		session.commit()
	except Exception as e:
		print(e)
		print("El error ocurrió en la función addPersonality the dbOperations.py")


def addPersonalityJob(response, company_id, job_id):
	try:
		# Calculate Factor I Surgency or Extraversion
		f1 = 0
		f1 = f1 + int(response['p1'])
		f1 = f1 - int(response['p6'])
		f1 = f1 + int(response['p11'])
		f1 = f1 - int(response['p16'])
		f1 = math.floor((f1 + 8)*100/16)

		# Calculate Factor II Agreeableness 
		f2 = 0
		f2 = f2 + int(response['p2'])
		f2 = f2 - int(response['p7'])
		f2 = f2 + int(response['p12'])
		f2 = f2 - int(response['p17'])
		f2 = math.floor((f2 + 8)*100/16)

		# Calculate Factor III Conscientiousness
		f3 = 0
		f3 = f3 + int(response['p3'])
		f3 = f3 - int(response['p8'])
		f3 = f3 + int(response['p13'])
		f3 = f3 - int(response['p18'])
		f3 = math.floor((f3 + 8)*100/16)

		# Calculate Factor IV Neuroticism
		f4 = 0
		f4 = f4 + int(response['p4'])
		f4 = f4 - int(response['p9'])
		f4 = f4 + int(response['p14'])
		f4 = f4 - int(response['p19'])
		f4 = math.floor((f4 + 8)*100/16)

		# Calculate Factor V Intellect or Imagination
		f5 = 0
		f5 = f5 + int(response['p5'])
		f5 = f5 - int(response['p10'])
		f5 = f5 - int(response['p15'])
		f5 = f5 - int(response['p20'])
		f5 = math.floor((f5 + 14)*100/16)

		resp = [f1, f2, f3, f4, f5]

		job = session.query(Job).filter(Job.id == job_id, Job.company_id == company_id).one()
		nuevo = job.personalidad
		if nuevo is not None:
			nuevo.append(resp)
			session.query(Job).filter(Job.id == job_id, Job.company_id == company_id).update({"personalidad":nuevo})
			session.commit()
		else:
			job.personalidad = [resp]
			session.commit()
	except Exception as e:
		print(e)
		print("El error ocurrió en la función addPersonalityJob the dbOperations.py")


def addMath(response, applicant_id):
	try:
		grade = 0
		questions = ['p1','p2','p3','p4','p5','p6','p7','p8','p9','p10']
		answers = ['3', '2', '3', '4', '5', '5', '4', '4', '4', '4']
		for i in range(len(questions)):
			if response[questions[i]] == answers[i]:
				grade = grade + 1
		skills = [grade]
		aplicante = session.query(Applicant).filter(Applicant.id == applicant_id).one()
		aplicante.skills = skills
		session.commit()

		all_jobs = session.query(Job).all()
		for job in all_jobs:
			job_id = job.id
			createMatchScore(magic.matchScore(job_id, applicant_id), job_id, applicant_id)
	except Exception as e:
		print(e)
		print("El error ocurrió en la función addMath the dbOperations.py")


def addMathJob(response, job_id):
	#try:
	grade = 0
	questions = ['p1','p2','p3','p4','p5','p6','p7','p8','p9','p10']
	answers = ['3', '2', '3', '4', '5', '5', '4', '4', '4', '4']
	for i in range(len(questions)):
		if response[questions[i]] == answers[i]:
			grade = grade + 1
	skill = [grade]
	job = session.query(Job).filter(Job.id == job_id).one()
	nuevo = job.skills
	if nuevo is not None:
		nuevo.append(skill)
		session.query(Job).filter(Job.id == job_id).update({"skills":nuevo})
		session.commit()
	else:
		job.skills = [skill]
		session.commit()

	#Crear los matchscores y ponerlos en la base de datos
	magic.generaModeloNevo(job_id)
	check = session.query(MatchScore).filter(MatchScore.job_id == job_id).first()
	if check is None:
		all_applicants = session.query(Applicant).all()
		job = session.query(Job).filter(Job.id == job_id).one()
		for applicant in all_applicants:
			applicant_id = applicant.id
			createMatchScore(magic.matchScore(job_id, applicant_id), job_id, applicant_id)
	else:
		scores = session.query(MatchScore).filter(MatchScore.job_id == job_id)
		for score in scores:
			applicant_id = score.applicant_id
			updateMatchScore(magic.matchScore(job_id, applicant_id), job_id, applicant_id)
		print("todo chido, si se logró")
	'''except Exception as e:
		print(e)
		print("El error ocurrió en la función addMathJob the dbOperations.py")'''


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


def createJob(title, salary, description, company_id, openings, status, zipcode):
	''' Function for creating a job. Everytime you create one, it creates a match score with every 
		applicant available and adds it to the db'''
	try:
		zipcode
		trab = Job(title = title, salary = salary, description = description , company_id = company_id, openings=openings, status=status, zipcode=zipcode)
		session.add(trab)
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


def updateMatchScore(score, job_id, applicant_id):
	try:
		scored = session.query(MatchScore).filter(MatchScore.job_id == job_id, MatchScore.applicant_id == applicant_id).one()
		scored.scores = score
		session.commit()
	except Exception as e:
		print(e)
		return render_template("main.html")
		print("El error está en updateMatchScore de dbOperations")
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

#printDB()

