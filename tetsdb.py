from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from database_setup import Base, Company, Applicant, Job, MatchScore
from sqlalchemy.orm import sessionmaker
#import dbOperations
import locale
import math

engine = create_engine('postgres://localhost/simil')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def matchScore(job_id, applicant_id):
	applicant = session.query(Applicant).filter(Applicant.id == applicant_id).one()
	job = session.query(Job).filter(Job.id == job_id).one()
	#Primero calculamos la distancia entre los skills
	jobskill = 0
	for i in job.skills:
		jobskill = jobskill + i[0]
	jobskill = jobskill / len(job.skills)
	skillDistance = math.sqrt(pow(jobskill-applicant.skills[0],2))/10
	print(skillDistance)
	#Segundo calculamos la distancia entre los vectores de personalidad
	jobPers = [0,0,0,0,0]
	for i in job.personalidad:
		for j in range(5):
			jobPers[j] = jobPers[j] + i[j]
	n = len(job.personalidad)
	for k in range(5):
		jobPers[k] = jobPers[k] / n
	persDistance = [0,0,0,0,0]
	tot = 0
	for t in range(5):
		persDistance[t] = math.sqrt(pow(jobPers[t] - applicant.personalidad[t],2))/100
		tot = tot + persDistance[t] 
	#Sacar el promedio de las distancias en dimensiones de personalidad para llegar a un solo número entre 0 y 1 de la distancia total en personalidad
	tot = tot/5
	print(tot)


matchScore(5,5)



