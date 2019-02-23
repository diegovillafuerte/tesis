from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, func
from database_setup import Base, Company, Applicant, Job
from sqlalchemy.orm import sessionmaker
import random

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


def createUser(name, mail, password):
	appli = Applicant(name = name, mail = mail, password=password)
	session.add(appli)
	session.commit()

def createCompany(name, mail, password, description):
	comp = Company(name = name, mail = mail, password = password, description = description)
	session.add(comp)
	session.commit()

def createJob(title, salary, description, company_id, openings, status):
	trab = Job(title = title, salary = salary, description = description , company_id = company_id, openings=openings)
	session.add(trab)
	session.commit()

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

def testIfExists():
	quer = session.query(Applicant).filter(Applicant.mail == "diegovillafuertesoraiz@gmail.com").scalar()
	if quer:
		sal = str(quer.id) +" - " + quer.name +" - " + quer.mail + "\n"
	else:
		sal = "hola"
	return sal

#Create a few users 
'''
user_names = ["Ana", "jose", "Pedro", "Joel", "Mariana", "Sofía"]
for user in user_names:
	mail = user + "@gmail.com"
	password = user + str(len(user))
	createUser(user, mail, password)


company_names = ["Transbarcos", "SuperLibros", "TodoMart", "DeportesExtreme", "BancoDeLaMeseta"]
for company in company_names:
	mail = "contacto@" + company + ".com"
	password = company + str(len(company))
	description = "Está es una descripción genérica porque esto es un ejemplo"
	createCompany(company, mail, password, description)

job_titles = ["Cajero", "Asistente", "Vendedor", "servic", "Mesero"]
for title in job_titles:
	salary = len(title)*1423
	description = "Todas las job descriptions son identicas"
	company_id =  random.randint(1,5)
	openings = len(title)*4
	createJob(title, salary, description, company_id, openings, True)

prints:
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
1 - Cajero - 8538.0 - 1 - 24

2 - Asistente - 12807.0 - 1 - 36

3 - Vendedor - 11384.0 - 1 - 32

4 - servic - 8538.0 - 4 - 24

5 - Mesero - 8538.0 - 1 - 24	
'''

#printDB()

