from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, func
from database_setup import Base, Company, Applicant, Job, MatchScore
from sqlalchemy.orm import sessionmaker
import random

engine = create_engine('postgres://localhost/simil')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def getListOfMatchesForJob(job_id):
	try:
		applicants = session.query(Applicant).all()
		matches = []
		for i in applicants:
			matches.append([i.name,getMatchScore(job_id, i.id),i.id])
		matches.sort(key=lambda x: x[1], reverse=True)
		return matches
	except Exception as e:
		print(e)
		flash("Lo sentimos, ocurrió un error en nuestro sistema, por favor vuelve a intentarlo. Si el problema es persistente te pedimos que te pongas en contacto con nosotros")
		return render_template("main.html")

def getListOfMatchesForApplicant(applicant_id):
	try:
		jobs = session.query(Job).filter(status==True)
		matches = []
		for i in jobs:
			matches.append([i.id, i.title, i.salary, i.descrition, getMatchScore(i.id, applicant_id)])
		matches.sort(key=lambda x: x[4], reverse=True)
		return matches
	except Exception as e:
		print(e)
		flash("Lo sentimos, ocurrió un error en nuestro sistema, por favor vuelve a intentarlo. Si el problema es persistente te pedimos que te pongas en contacto con nosotros")
		return render_template("main.html")

def getMatchScore(job_id, applicant_id):
	try:
		score = session.query(MatchScore).filter(MatchScore.job_id==job_id, MatchScore.applicant_id==applicant_id).one()
		return score.scores
	except Exception as e:
		print(e)
		flash("Lo sentimos, ocurrió un error en nuestro sistema, por favor vuelve a intentarlo. Si el problema es persistente te pedimos que te pongas en contacto con nosotros")
		return render_template("main.html")

def matchScore(job_id, applicant_id):
	score = random.random()*100
	return score
