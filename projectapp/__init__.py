from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import config       

app = Flask(__name__,instance_relative_config=True)                 
app.config.from_pyfile('config.py')                                 
app.config.from_object(config.LiveConfig)                     

db = SQLAlchemy(app)
migrate = Migrate(app,db)

from projectapp.routes import userroutes,walletapiroutes,apiroutes
from projectapp import models
from projectapp import forms