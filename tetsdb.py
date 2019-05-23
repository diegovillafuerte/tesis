from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from database_setup import Base, Company, Applicant, Job, MatchScore
from sqlalchemy.orm import sessionmaker
import dbOperations
import locale
import os
import math
import googlemaps
import magic
import dbOperations
import pandas as pd
import numpy as np
from numpy.random import seed, rand, randn
import matplotlib.pyplot as plt
import scipy.stats
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

#engine = create_engine('postgres://localhost/simil')
db_user = os.environ['db_user']
db_pass = os.environ['db_pass']
db_host = os.environ['db_host']
db_port = os.environ['db_port']

engine = create_engine("postgresql+psycopg2://{}:{}@{}:{}/{}?sslmode=require".format(db_user, db_pass, db_host, db_port, 'postgres'))
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Setup the api key for the api call
apiKey = os.environ['GOOGLE_API_KEY']
gmaps = googlemaps.Client(key=apiKey)



magic.generaModeloNevo(4)







'''
personalidad = [[87,62,87,37,62]] 
skills =  [[9]] 
company_id = 5 
zipcode =  11000  
intercept = 0.375256780722198 
coeficientes = [0.000290400965114909,-0.00650529427700954,0.309185183468641,0.299571900939,-0.465213087004751,1.3595358287453,0.375639225053791,0.247777430270992,0.372059201489015,0.113991537900837,0.258707846486217,0.414117685168708]

demo = [[34220,111550,11,11,0,14]]
job = session.query(Job).filter(Job.id == 3).first()
job.demografico = demo
job.personalidad = personalidad
job.skills = skills
job.company_id = company_id
job.zipcode = zipcode
job.intercept = intercept
job.coeficientes = coeficientes
session.commit()
'''








	



