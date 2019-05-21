from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from database_setup import Base, Company, Applicant, Job, MatchScore
from sqlalchemy.orm import sessionmaker
#import dbOperations
import locale
import os
import math
import googlemaps
#import magic
import pandas as pd
import numpy as np
from numpy.random import seed, rand, randn
import matplotlib.pyplot as plt
import scipy.stats
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

engine = create_engine('postgres://localhost/simil')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Setup the api key for the api call
apiKey = os.environ['GOOGLE_API_KEY']
gmaps = googlemaps.Client(key=apiKey)


def getCharacteristicVector(tipo, id, job_id):
	'''
	Function to fetch and normalize the characteristic vector of an applicant or jobPosting given a specific job
	It recevies a tipo parameter which may be 0 if it is an applicant and 1 if its a job
	It receives an id which points to the specific user

	Regresa un vector de la siguiente forma:
		[1. Edad, 
		2. distancia al centro de trabajo, 
		3. genero, 
		4. estado civil, 
		5. número de personas que dependen económicamente, 
		6. grado máximo de estudios,
		7. extroversión,
		8. empatía/capacidad para cooperar,
		9. responsabilidad/atención al detalle,
		10. neuroticismo,
		11. apertura al cambio/creatividad,
		12. habilidad matemática 
		]
	'''
	job = session.query(Job).filter(Job.id == job_id).one()
	if tipo == 0:
		applicant = session.query(Applicant).filter(Applicant.id == id).one()

		#Obtenemos la calificación de matemáticas
		skill = applicant.skills[0]/10

		#Obtenermos vector de personalidad
		appPers = [0,0,0,0,0]
		for i in range(len(appPers)):
			appPers[i] = applicant.personalidad[i]/100

		#Obtenemos vector demográfico
		appDemo = [0,0,0,0,0,0]
		appDemo[0] = applicant.demografico[0]
		result = gmaps.distance_matrix(str(applicant.demografico[1])[1:] + ' mexico', job.zipcode + ' mexico')
		dist = result['rows'][0]['elements'][0]['duration']['value']
		appDemo[1] = dist
		appDemo[2] = int(str(applicant.demografico[2])[1:])
		appDemo[3] = int(str(applicant.demografico[3])[1:])
		appDemo[4] = applicant.demografico[4]
		appDemo[5] = int(str(applicant.demografico[5])[1:])	

		#Los juntamos todos en uno solo
		characteristicVector = appDemo + appPers
		characteristicVector.append(skill)
		#characteristicVector.append(applicant.outcome)
		return characteristicVector

	else:
		#Obtenemos calificación promedio de matemáticas
		jobskill = 0
		for i in job.skills:
			jobskill = jobskill + i[0]/10
		jobskill = jobskill / len(job.skills)

		#Obtenermos vector promedio de personalidad
		jobPers = [0,0,0,0,0]
		for i in job.personalidad:
			for j in range(5):
				jobPers[j] = jobPers[j] + i[j]/100
		n = len(job.personalidad)
		for k in range(5):
			jobPers[k] = jobPers[k] / n

		#Obtenemos vector promedio demográfico
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
		for j in range(6):
			jobDemo[j] = jobDemo[j] / n

		#Los juntamos todos en uno solo
		characteristicVector = jobDemo + jobPers
		characteristicVector.append(jobskill)
		return characteristicVector



def matchScore(job_id, applicant_id):
	''' Toma el id del aplicante y del trabajo y te regresa un score de compatibilidad '''
	#Generamos el vector característico del aplicante con respecto a este trabajo
	vectorPersona = getCharacteristicVector(0,applicant_id,job_id)
	#Obtenemos los coeficientes y el intercept del modelo del trabajo
	trabajoAModelar = session.query(Job).filter(Job.id == job_id).one()
	#Inicializamos el modelo
	modelo = LogisticRegression()
	modelo.coef_ = np.array([trabajoAModelar.coeficientes])
	modelo.intercept_ = np.array(trabajoAModelar.intercept)
	modelo.classes_ = np.array([False, True])
	
	prediction = modelo.predict([vectorPersona])
	if prediction[0] == True:
		matchScore = modelo.predict_proba([vectorPersona])[0][1]*100
	else:
		matchScore = 0
	return matchScore
	



