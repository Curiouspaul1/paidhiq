# Dependencies
from flask import Flask, render_template, request, url_for, redirect
import sys
import stripe
from sqlalchemy import Column, ForeignKey, Integer, String
from  sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, validators
from wtforms.validators import DataRequired
from functools import wraps
from passlib.hash import sha256_crypt
from sqlalchemy.sql.expression import func, select



app = Flask(__name__)

# Wtforms Config
app.config['SECRET_KEY'] = '2019Mech#'

#keys for checkout
pub_key = 'pk_test_x0IDLqCvSBphq885oLDauzgg'
secret_key = 'sk_test_6UjGjRnxBTzv5xKdjLpsqc5a'

# API key
stripe.api_key = secret_key

#--------Database --------------#

Base = declarative_base()
# table class
class user(Base):
    __tablename__ = 'user'

    # mappers
    id = Column(Integer, primary_key = True)
    name = Column(String(200),nullable=False)
    username = Column(String(80),nullable=False)
    email = Column(String(200),nullable=False)
    password = Column(String(200),nullable=False)

class questions(Base):
    __tablename__ = 'questions'

    # mappers
    id = Column(Integer, primary_key=True, nullable=True)
    question =  Column(String(255),nullable=False)
    answers = Column(String(200),nullable=False)

class options(Base):
    __tablename__ = 'options'

    # mappers
    id = Column(Integer, primary_key=True, nullable=False)
    A = Column(String(80),nullable=False)
    B = Column(String(80),nullable=False)
    C = Column(String(80),nullable=False)
    D = Column(String(80),nullable=False)
    questionID = Column(Integer,ForeignKey('questions.id'))
    questions = relationship(questions)


######## End of Database_Setup ##########
engine = create_engine('mysql://root:mechatronic@localhost/test')
Base.metadata.create_all(engine)

#----------DB SESSION SETUP---------------------#
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


############## --------------Routes-------------###################
class Register(FlaskForm):
    name = StringField('name',[validators.Length(min=5,max=100)])
    username = StringField('username',[validators.Length(min=5,max=80)])
    email = StringField('email',[validators.Length(min=8,max=80)])
    password = PasswordField('password',[validators.Length(max=80)])

@app.route('/register', methods = ['GET','POST'])
def register():
    reg = Register()
    if reg.validate_on_submit():
        dets = user(name=reg.name.data,username=reg.username.data,email=reg.email.data,password=reg.password.data)

        session.add(dets)
        session.commit()
        return redirect(url_for('checkout'))
    return render_template('register.html',reg=reg)

@app.route('/checkout')
def checkout():
    return render_template('checkout.html',pub_key=pub_key)

@app.route('/pay',methods=['POST'])
def pay():
    customer = stripe.Customer.create(email=request.form['stripeEmail'], source=request.form['stripeToken'])

    charge = stripe.Charge.create(
        customer=customer.id,
        amount = 500,
        currency = 'usd',
        description = 'Quiz Fee'
    )

    return redirect(url_for('quizpage'))

@app.route('/quizpage',methods=['GET','POST'])
def quizpage():
    quiz = session.query(questions).order_by(func.rand()).limit(5)
    opts = session.query(options).filter(options.id==options.questionID)
    return render_template('quizpage.html',quiz=quiz,opts=opts)

if __name__ == '__main__':
    app.run(debug=True)
