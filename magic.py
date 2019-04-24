import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, func
from database_setup import Base, Company, Applicant, Job, MatchScore
from sqlalchemy.orm import sessionmaker
import random
import locale
import math
import googlemaps

#Importar formateo de dinero
locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )

# engine = create_engine('postgres://localhost/simil')
db = create_engine('postgres://localhost/simil')
Base.metadata.bind = db

DBSession = sessionmaker(bind=db)
session = DBSession()

#Setup the api key for the api call
API_key = 'AIzaSyD7dxFiUZuFca-dU-uLgVqL4oJ9q7P14fY'
gmaps = googlemaps.Client(key=API_key)

def getListOfMatchesForJob(job_id):
	try:
		applicants = session.query(Applicant).all()
		matches = []
		for i in applicants:
			match = getMatch(job_id, i.id)
			if match.interest_applicant and not match.interest_job:
				matches.append([i.name,getMatch(job_id, i.id).scores,i.id])
		matches.sort(key=lambda x: x[1], reverse=True)
		return matches
	except Exception as e:
		print(e)
		print("El error es en la función getListOfMatchesForJob de magic.py")
		flash("Lo sentimos, ocurrió un error en nuestro sistema, por favor vuelve a intentarlo. Si el problema es persistente te pedimos que te pongas en contacto con nosotros")
		return render_template("main.html")

def getListOfMatchesForApplicant(applicant_id):
	try:
		jobs = session.query(Job).filter(Job.status==True)
		matches = []
		for i in jobs:
			match = getMatch(i.id, applicant_id)
			if not match.interest_applicant:
				company_name = session.query(Company).filter(Company.id == i.company_id).one().name
				matches.append([i.id, i.title, locale.currency(i.salary, grouping=True), i.description, match.scores , company_name])
		matches.sort(key=lambda x: x[4], reverse=True)
		return matches
	except Exception as e:
		print(e)
		print("El error es en la función getListOfMatchesForApplicant de magic.py")
		flash("Lo sentimos, ocurrió un error en nuestro sistema, por favor vuelve a intentarlo. Si el problema es persistente te pedimos que te pongas en contacto con nosotros")
		return render_template("main.html")

def getMatch(job_id, applicant_id):
	try:
		score = session.query(MatchScore).filter(MatchScore.job_id==job_id, MatchScore.applicant_id==applicant_id).one()
		return score
	except Exception as e:
		print(e)
		flash("Lo sentimos, ocurrió un error en nuestro sistema, por favor vuelve a intentarlo. Si el problema es persistente te pedimos que te pongas en contacto con nosotros")
		return render_template("main.html")

def matchScore(job_id, applicant_id):
	applicant = session.query(Applicant).filter(Applicant.id == applicant_id).one()
	job = session.query(Job).filter(Job.id == job_id).one()
	#Primero calculamos la distancia entre los skills
	jobskill = 0
	for i in job.skills:
		jobskill = jobskill + i[0]
	jobskill = jobskill / len(job.skills)
	skillDistance = math.sqrt(pow(jobskill-applicant.skills[0],2))/10

	#Segundo calculamos la distancia entre los vectores de personalidad
	jobPers = [0,0,0,0,0]
	for i in job.personalidad:
		for j in range(5):
			jobPers[j] = jobPers[j] + i[j]
	n = len(job.personalidad)
	for k in range(5):
		jobPers[k] = jobPers[k] / n
	persDistance = [0,0,0,0,0]
	#tot = 0
	for t in range(5):
		persDistance[t] = math.sqrt(pow(jobPers[t] - applicant.personalidad[t],2))/100
		#tot = tot + persDistance[t] 
	# Se deja fuera--Sacar el promedio de las distancias en dimensiones de personalidad para llegar a un solo número entre 0 y 1 de la distancia total en personalidad
	#personalityDistance = tot/5

	'''Tercero, calculamos la distancia para el resto de los factores demográficos
	jobDemo es un vector de la siguiente forma:
				[0--edad, 
				1--distancia al trabajo (minutos), 
				2--género (Número entre 0 y 1) 
				3--estado civil (número entre 0 y 1), 
				4--dependientes económicos, 
				5--grado máximo de estudios]'''
	jobDemo = [0,0,0,0,0,0]
	n = len(job.demografico)
	for i in job.demografico:
		#Edad
		jobDemo[0] = jobDemo[0] + i[0]
		#Distancia entre el domicilio del empleado que contesto la encuesta y su centro de trabajo
		result = gmaps.distance_matrix( 'mexico ' +  str(i[1])[1:], job.zipcode + ' mexico')
		dist = result['rows'][0]['elements'][0]['duration']['value']
		jobDemo[1] = jobDemo[1] + dist
		#Género
		jobDemo[2] = jobDemo[2] + int(str(i[2])[1:])
		#Estado civil
		jobDemo[3] = jobDemo[3] + int(str(i[3])[1:])
		#Dependientes económicos
		jobDemo[4] = jobDemo[4] + i[4]
		#Grado máximo de estudios
		jobDemo[5] = jobDemo[5] + int(str(i[5])[1:])
	#Promediar edad
	for j in range(6):
		jobDemo[j] = jobDemo[j] / n
	#Preparamos vector de aplicante
	appDemo = [0,0,0,0,0,0]
	appDemo[0] = applicant.demografico[0]
	result = gmaps.distance_matrix(str(applicant.demografico[1])[1:] + ' mexico', job.zipcode + ' mexico')
	dist = result['rows'][0]['elements'][0]['duration']['value']
	appDemo[1] = dist
	appDemo[2] = int(str(applicant.demografico[2])[1:])
	appDemo[3] = int(str(applicant.demografico[3])[1:])
	appDemo[4] = applicant.demografico[4]
	appDemo[5] = int(str(applicant.demografico[5])[1:])	

	#Sacamos la distancia para cada campo
	demDistance = [0,0,0,0,0,0]
	for t in range(6):
		demDistance[t] = math.sqrt(pow(jobDemo[t] - appDemo[t],2))
	#Ahora lo normalizamos para que tenga valores entre 0 y 1 en todos sus indices
	#Si hay más de 10 años de distancia, esta es máxima
	demDistance[0] = (demDistance[0]/365)/10
	#Si hay más de 4 horas de distancia en tiempo al trabajo, la distancia es máxima
	demDistance[1] = (demDistance[1]/3600)/4
	#Si tiene más de 5 dependientes econoómicos, la distancia es máxima
	demDistance[4] = (demDistance[4])/5
	#El grado máximo de estudios no tiene distancia máxima, solo se escala
	demDistance[5] = (demDistance[5])/5
	for l in range(6):
		if demDistance[l] > 1:
			demDistance[l] = 1

	#Juntamos a todos en un solo vector y le sacamos un promedio ponderando por el vector de pesos
	totDistance = demDistance + persDistance
	totDistance.append(skillDistance)
	weightVector = [1/len(totDistance) for x in totDistance]
	print(sum([a*b for a,b in zip(totDistance,weightVector)]))
	matchScore = ((sum([a*b for a,b in zip(totDistance,weightVector)])*100)/2)+50
	return matchScore

def recalculateAllScores():
	return 0
