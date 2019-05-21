import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Float, create_engine, Boolean, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import psycopg2


#db = create_engine('postgres://localhost/simil')
db_user = os.environ['db_user']
db_pass = os.environ['db_pass']
db_host = os.environ['db_host']
db_port = os.environ['db_port']
db_name = os.environ['db_name']

db = create_engine("postgresql+psycopg2://{}:{}@{}:{}/{}?sslmode=require".format(db_user, db_pass, db_host, db_port, 'postgres'))


Base = declarative_base()

class Company(Base):

	__tablename__ = 'company'

	id = Column(Integer, primary_key = True)
	name = Column(String(150), nullable = False)
	mail = Column(String(150), nullable = False, unique=True)
	password = Column(String(150), nullable = False)
	description = Column(String(400), nullable = False)

	@property
	def serialize(self):
		return {
			'name': self.name,
			'id': self.id,
			'mail': self.mail,
			'password': self.password,
			'description': self.description}

class Applicant(Base):

	__tablename__ = 'applicant'

	id = Column(Integer, primary_key = True)
	name = Column(String(150), nullable = False)
	mail = Column(String(150), nullable = False, unique=True)
	password = Column(String(150), nullable = False)
	demografico = Column(ARRAY(Integer))
	personalidad = Column(ARRAY(Integer))
	skills = Column(ARRAY(Integer))
	outcome = Column(Boolean, default = False)

	@property
	def serialize(self):
		#returns object data in easily serializable format
		return{
		'id':self.id,
		'name':self.name,
		'mail':self.mail,
		'demográfico':self.demografico,
		'personalidad':self.personalidad,
		'skills':self.skills
		}

class Job(Base):

	__tablename__ = 'job'

	id = Column(Integer, primary_key = True)
	title = Column(String(150), nullable = False)
	salary = Column(Float, nullable = False)
	description = Column(String(400), nullable = False)
	openings = Column(Integer)
	status = Column(Boolean, default=True)
	demografico = Column(ARRAY(Integer))
	personalidad = Column(ARRAY(Integer))
	skills = Column(ARRAY(Integer))
	zipcode = Column(String(6))
	coeficientes = Column(ARRAY(Float))
	intercept = Column(Float)

	company_id = Column(Integer, ForeignKey('company.id'))
	company = relationship(Company)

	@property
	def serialize(self):
		return {
			'id': self.id,
			'title': self.title,
			'salary': self.salary,
			'description': self.description,
			'openings': self.openings,
			'status': self.status}

class MatchScore(Base):

	__tablename__ = 'matchscore'

	scores = Column(Integer, nullable = False)
	job_id = Column(Integer, ForeignKey('job.id'), primary_key = True)
	job = relationship(Job)
	applicant_id = Column(Integer, ForeignKey('applicant.id'), primary_key = True)
	applicant = relationship(Applicant)
	interest_applicant = Column(Boolean, default = False)
	interest_job = Column(Boolean, default = False)

	@property
	def serialize(self):
		return {
			'score': self.scores,
			'job_id': self.job_id,
			'applicant_id': self.applicant_id}


Session = sessionmaker(db)
session = Session()
Base.metadata.create_all(db)