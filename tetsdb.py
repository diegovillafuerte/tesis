from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from database_setup import Base, Company, Applicant, Job, MatchScore
from sqlalchemy.orm import sessionmaker
import dbOperations
import locale

engine = create_engine('postgres://localhost/simil')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def getMatch(job_id, applicant_id):
	score = session.query(MatchScore).filter(MatchScore.job_id==job_id, MatchScore.applicant_id==applicant_id).one()
	return score


def getListOfMatchesForApplicant(applicant_id):
	jobs = session.query(Job).filter(Job.status==True)
	matches = []
	for i in jobs:
		company = session.query(Company).filter(Company.id == i.company_id).one()
		match = getMatch(i.id, applicant_id)
		print(match.scores)
	# 	matches.append([i.id, i.title, i.salary, i.description, magic.getMatch(i.id, applicant_id).scores , company.name])
	# matches.sort(key=lambda x: x[4], reverse=True)
	# return matches
getListOfMatchesForApplicant(11)
