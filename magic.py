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
import scipy.stats
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
import pandas as pd
import numpy as np
from numpy.random import seed, rand, randn
import matplotlib.pyplot as plt

#Importar formateo de dinero
locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )

# engine = create_engine('postgres://localhost/simil')
db = create_engine('postgres://localhost/simil')
Base.metadata.bind = db

DBSession = sessionmaker(bind=db)
session = DBSession()

#Setup the api key for the api call
apiKey = os.environ['GOOGLE_API_KEY']
gmaps = googlemaps.Client(key=apiKey)

db_user = os.environ['db_user']
db_pass = os.environ['db_pass']
db_host = os.environ['db_host']
db_port = os.environ['db_port']

db = create_engine("postgresql+psycopg2://{}:{}@{}:{}/{}?sslmode=require".format(db_user, db_pass, db_host, db_port, 'postgres'))


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


def simulateDB(charVector, rows, desv):
	#set seed for reproducability
	successRows = int(rows/2)
	failureRows = rows - successRows

	seed(123)
	columns = ['edad', 'distancia', 'genero', 'edoCivil', 
				'dependientes', 'estudios', 'extroversion', 'empatia', 
				'responsabilidad', 'neuroticismo', 'creatividad', 'matematica', 'outcome']
	base = pd.DataFrame(columns = columns)
	#Primero siumlamos todas las filas exitosas
	#Simulamos edades.

	edadsim = charVector[0] + charVector[0] * desv * randn(successRows)
	base['edad'] = edadsim

	#Simulamos distancias
	distsim = charVector[1] + charVector[1] * desv * randn(successRows)
	base['distancia'] = distsim

	#Simulamos género
	lower = 0
	upper = 1
	if charVector[2] == 1:
		mu = .5 + desv
	else:
		mu = .5 - desv
	sigma = desv
	gensim = scipy.stats.truncnorm.rvs((lower-mu)/sigma,(upper-mu)/sigma,loc=mu,scale=sigma,size=successRows)
	base['genero'] = gensim

	#Simulamos estado civil
	lower = 0
	upper = 1
	if charVector[3] == 1:
		mu = .5 + desv
	else:
		mu = .5 - desv
	sigma = desv
	civsim = scipy.stats.truncnorm.rvs((lower-mu)/sigma,(upper-mu)/sigma,loc=mu,scale=sigma,size=successRows)
	base['edoCivil'] = civsim

	#Simulamos número de dependientes
	lower = 0
	upper = 10
	mu = charVector[4]
	sigma = (1+charVector[4])*desv
	depsim = scipy.stats.truncnorm.rvs((lower-mu)/sigma,(upper-mu)/sigma,loc=mu,scale=sigma,size=successRows)
	base['dependientes'] = depsim

	#Simulamos máximo grado de estudios
	lower = 0
	upper = 5
	mu = charVector[5]
	sigma = (1+charVector[5])*desv
	estsim = scipy.stats.truncnorm.rvs((lower-mu)/sigma,(upper-mu)/sigma,loc=mu,scale=sigma,size=successRows)
	base['estudios'] = estsim

	#Simulamos personalidad y matemáticas
	for i in range(6,12):
		lower = 0
		upper = 1
		mu = charVector[i]
		sigma = desv
		sim = scipy.stats.truncnorm.rvs((lower-mu)/sigma,(upper-mu)/sigma,loc=mu,scale=sigma,size=successRows)
		base[columns[i]] = sim

	base['outcome'] = [True] * successRows

	# ========================= Ahora generamos datos dummy ====================================================
	genVector = [15000.0, 3000.0, 0.5, 0.5, 2, 3, .5, 0.5, 0.5, 0.5, 0.5, 0.5]
	baseaux = pd.DataFrame(columns = columns)

	sim = genVector[0] + genVector[0] * desv * randn(failureRows)
	baseaux['edad'] = sim

	#Simulamos distancias
	sim = genVector[1] + genVector[1] * desv * randn(failureRows)
	baseaux['distancia'] = sim

	#Simulamos género
	lower = 0
	upper = 1
	mu = .5
	sigma = desv
	sim = scipy.stats.truncnorm.rvs((lower-mu)/sigma,(upper-mu)/sigma,loc=mu,scale=sigma,size=failureRows)
	baseaux['genero'] = sim


	#Simulamos estado civil
	lower = 0
	upper = 1
	mu = .5
	sigma = desv
	sim = scipy.stats.truncnorm.rvs((lower-mu)/sigma,(upper-mu)/sigma,loc=mu,scale=sigma,size=failureRows)
	baseaux['edoCivil'] = sim

	#Simulamos número de dependientes
	lower = 0
	upper = 10
	mu = genVector[4]
	sigma = (1+genVector[4])*desv
	sim = scipy.stats.truncnorm.rvs((lower-mu)/sigma,(upper-mu)/sigma,loc=mu,scale=sigma,size=failureRows)
	baseaux['dependientes'] = sim

	#Simulamos máximo grado de estudios
	lower = 0
	upper = 5
	mu = genVector[5]
	sigma = (1+genVector[5])*desv
	sim = scipy.stats.truncnorm.rvs((lower-mu)/sigma,(upper-mu)/sigma,loc=mu,scale=sigma,size=failureRows)
	baseaux['estudios'] = sim

	#Simulamos personalidad y matemáticas
	for i in range(6,12):
		lower = 0
		upper = 1
		mu = genVector[i]
		sigma = desv
		sim = scipy.stats.truncnorm.rvs((lower-mu)/sigma,(upper-mu)/sigma,loc=mu,scale=sigma,size=failureRows)
		baseaux[columns[i]] = sim

	baseaux['outcome'] = [False] * failureRows
	frames = [base, baseaux]
	baseCompleta = pd.concat(frames)
	baseCompleta = baseCompleta.reset_index(drop=True)
	baseCompleta.to_csv('base.csv')
	return baseCompleta


def entrenarModeloLog(base):
	'''
	Función para entrenar un modelo dada una base de datos (de la forma generada por simulateBD)
	Te regresa el modelo en un arreglo con los siguientes campos:
	[0] = Vector de coeficientes
	[1] = Intercept
	'''

	base = pd.read_csv(base, index_col=0)
	independientes = ['edad', 'distancia', 'genero', 'edoCivil', 
					'dependientes', 'estudios', 'extroversion', 'empatia', 
					'responsabilidad', 'neuroticismo', 'creatividad', 'matematica']
	X = base[independientes]
	y = base['outcome']
	X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.25,random_state=0)
	logreg = LogisticRegression()
	logreg.fit(X_train,y_train)
	y_pred=logreg.predict(X_test)
	matrizConf = metrics.confusion_matrix(y_test, y_pred)
	coeffs = logreg.coef_
	yint = logreg.intercept_
	coeficientes, intercept = coeffs.tolist()[0], yint.tolist()[0]
	# Regresa dos valores --> Coeficientes es un arreglo de dimensión 12 con los coeficientes del modelo y Intercept es un real 
	return coeficientes, intercept


def generaModeloNevo(job_id):
	''' Genera el modelo de un trabajo con base en los modelos existentes'''
	trabajoAModelar = session.query(Job).filter(Job.id == job_id).one()
	otroTrabajos = session.query(Job).filter(Job.id != job_id)
	vectorCaracteristico = getCharacteristicVector(1, trabajoAModelar.id, trabajoAModelar.id)
	similares = pd.DataFrame(columns= ['job', 'confidence', 'weight', 'vector', 'weighted'])
	for trabajo in otroTrabajos:
		modelo = LogisticRegression()
		modelo.coef_ = np.array([trabajo.coeficientes])
		modelo.intercept_ = np.array(trabajo.intercept)
		modelo.classes_ = np.array([False, True])
		prediction = modelo.predict([vectorCaracteristico])
		if prediction[0] == True: 
			probas = modelo.predict_proba([vectorCaracteristico])
			fila = pd.DataFrame({'job' : [trabajo.id] , 'confidence' : [probas[0][1]], 'vector' : [trabajo.coeficientes], 'intercept' : [trabajo.intercept]})
			similares = similares.append(fila, ignore_index = True)
	res = [0]*12
	for index, row in similares.iterrows():
		peso = row['confidence']/similares.confidence.sum()
		similares.set_value(index,'weight',peso)
	for index, row in similares.iterrows():
		pesado = [i*row['weight'] for i in row['vector']]
		similares.set_value(index, 'weighted',pesado)
		weightedInt = row['weight']*row['intercept']
		similares.set_value(index, 'weightedInt',weightedInt)
		for i in range(len(res)):
			res[i] = res[i] + similares['weighted'][index][i]
	intercept = similares.weightedInt.sum()
	job = session.query(Job).filter(Job.id == job_id).one()
	job.coeficientes = res
	job.intercept = intercept
	session.commit()


def getMatch(job_id, applicant_id):
	try:
		score = session.query(MatchScore).filter(MatchScore.job_id==job_id, MatchScore.applicant_id==applicant_id).one()
		return score
	except Exception as e:
		print(e)
		flash("Lo sentimos, ocurrió un error en nuestro sistema, por favor vuelve a intentarlo. Si el problema es persistente te pedimos que te pongas en contacto con nosotros")
		return render_template("main.html")


def getListOfMatchesForJob(job_id):
	try:
		applicants = session.query(Applicant).all()
		matches = []
		for i in applicants:
			match = getMatch(job_id, i.id)
			if match.interest_applicant and not match.interest_job and match != 0:
				matches.append([i.name,getMatch(job_id, i.id).scores,i.id])
		matches.sort(key=lambda x: x[1], reverse=True)
		return matches
	except Exception as e:
		print(e)
		print("El error es en la función getListOfMatchesForJob de magic.py")
		return render_template("main.html")


def getListOfMatchesForApplicant(applicant_id):
	try:
		jobs = session.query(Job).filter(Job.status==True)
		matches = []
		for i in jobs:
			match = getMatch(i.id, applicant_id)
			if not match.interest_applicant and match != 0:
				company_name = session.query(Company).filter(Company.id == i.company_id).one().name
				matches.append([i.id, i.title, locale.currency(i.salary, grouping=True), i.description, match.scores , company_name])
		matches.sort(key=lambda x: x[4], reverse=True)
		return matches
	except Exception as e:
		print(e)
		print("El error es en la función getListOfMatchesForApplicant de magic.py")
		flash("Lo sentimos, ocurrió un error en nuestro sistema, por favor vuelve a intentarlo. Si el problema es persistente te pedimos que te pongas en contacto con nosotros")
		return render_template("main.html")





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



def regenerateAllMatchScores():
	#Borrar todos los registros existentes de match
	session.query(MatchScore).delete()
	session.commit()

	#Fetch a todos los aplicantes
	aplicantes = session.query(Applicant)
	trabajos = session.query(Job)
	for job in trabajos:
		for aplicante in aplicantes:
			score = matchScore(job.id, aplicante.id)
			dbOperations.createMatchScore(score, job.id, aplicante.id)



#Esta es la versión vieja de matchScore que lo hace por distancias. Se deja pero no se usa 
''' def matchScore(job_id, applicant_id):
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

	Tercero, calculamos la distancia para el resto de los factores demográficos
	jobDemo es un vector de la siguiente forma:
				[0--edad, 
				1--distancia al trabajo (minutos), 
				2--género (Número entre 0 y 1) 
				3--estado civil (número entre 0 y 1), 
				4--dependientes económicos, 
				5--grado máximo de estudios]
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
	return matchScore '''

