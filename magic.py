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

def getlistOfMatches(job_id):
	applicants = session.query(Applicant).all()
	matches = {}
	par = []
	for i in applicants:
		score = magic.score(job_id, appli.id)
		par[0] = matchScore(job_id, i.id)
		par[1] = i.id
		matches[i.name] = par
	return matches

def matchScore(job_id, applicant_id):
	score = random.random()*100
	return score