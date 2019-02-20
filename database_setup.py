import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
import psycopg2

db_string = 'postgres://localhost/simil'

db = create_engine(db_string)

Base = declarative_base()


class Company(Base):

	__tablename__ = 'company'

	id = Column(Integer, primary_key = True)
	name = Column(String(150), nullable = False)
	mail = Column(String(150), nullable = False)
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
	mail = Column(String(150), nullable = False)
	password = Column(String(150), nullable = False)

	@property
	def serialize(self):
		#returns object data in easily serializable format
		return{
		'name':self.name,
		'description':self.description,
		'id':self.id,
		'price':self.price,
		'course':self.course,
		}

class Job(Base):

	__tablename__ = 'job'

	id = Column(Integer, primary_key = True)
	title = Column(String(150), nullable = False)
	salary = Column(Float, nullable = False)
	description = Column(String(400), nullable = False)

	company_id = Column(Integer, ForeignKey('company.id'))
	company = relationship(Company)

	@property
	def serialize(self):
		return {
			'id': self.id,
			'title': self.title,
			'salary': self.salary,
			'description': self.description}

Session = sessionmaker(db)
session = Session()
Base.metadata.create_all(db)