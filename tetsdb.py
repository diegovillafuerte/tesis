from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from database_setup import Base, Company, Applicant, Job, MatchScore
from sqlalchemy.orm import sessionmaker
import dbOperations
import locale
import math
import googlemaps
import magic

engine = create_engine('postgres://localhost/simil')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

psql \
   --host=simil1.cyw8ohrkqbea.us-west-2.rds.amazonaws.com \
   --port=5432 \
   --username=diegoMaster \
   --password \
   --dbname=simil1 

   ps = instanciaSimil123