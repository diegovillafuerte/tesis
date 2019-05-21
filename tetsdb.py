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








	



