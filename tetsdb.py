from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from database_setup import Base, Company, Applicant, Job
from sqlalchemy.orm import sessionmaker
import random

engine = create_engine('postgres://localhost/simil')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def createUser(name, mail, password):
	appli = Applicant(name = name, mail = mail, password=password)
	session.add(appli)
	session.commit()

def createCompany(name, mail, password, description):
	comp = Company(name = name, mail = mail, password = password, description = description)
	session.add(comp)
	session.commit()

def createJob(title, salary, description, company_id, openings):
	trab = Job(title = title, salary = salary, description = description , company_id = company_id, openings=openings)
	session.add(trab)
	session.commit()

def printDB():
	print("==============Applicants================")
	applicants = session.query(Applicant).all()
	for applicant in applicants:
		sal = str(applicant.id) +" - " + applicant.name +" - " + applicant.mail + "\n"
		print(sal)
	print("\n==============Companies===============")
	companies = session.query(Company).all()
	for company in companies:
		sal = str(company.id) +" - " + company.name +" - " + company.mail + "\n"
		print(sal)
	print("\n==============Jobs===============")
	jobs = session.query(Job).all()
	for job in jobs:
		sal = str(job.id) +" - " + job.title +" - " + str(job.salary) +" - " + str(job.company_id)+" - " + str(job.openings) +"\n"
		print(sal)

def testIfExists():
	quer = session.query(Applicant).filter(Applicant.mail == "diegovillafuertesoraiz@gmail.com").scalar()
	if quer:
		sal = str(quer.id) +" - " + quer.name +" - " + quer.mail + "\n"
	else:
		sal = "hola"
	return sal

'''#Create a few users
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
	createJob(title, salary, description, company_id, openings)
	'''

printDB()

