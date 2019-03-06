from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from database_setup import Base, Company, Applicant, Job, MatchScore
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgres://localhost/simil')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def getMatch(job_id, applicant_id):
	score = session.query(MatchScore).filter(MatchScore.job_id==job_id, MatchScore.applicant_id==applicant_id).one()
	return score