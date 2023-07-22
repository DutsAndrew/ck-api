from flask import Flask, request, jsonify
from wtforms import Form, StringField, validators
from datetime import datetime
from models.user import db, User
import bcrypt

#####
#####

# NEED TO CONVERT MODELS TO MOTOR AND REMOVE MONGOENGINE USAGE TO KEEP THINGS ASYNC NON I/O BLOCKING

#####
#####

class SignUpForm(Form):
    email = StringField("email", [
        validators.DataRequired("You must provide an email address"),
        validators.Email("Your format does not match that of a typical email address, please try again"),
        validators.Length(min=1, max=1000, message="Email must be at least one character and no more than 1000"),
    ])
    firstName = StringField("firstName", [
        validators.DataRequired("You must provide a first name to create an account"),
        validators.Length(min=1, max=1000, message="Your name must be at least 1 character and no more than 1000"),
    ])
    lastName = StringField("lastName", [
        validators.DataRequired("You must enter a last name to create an account"),
        validators.Length(min=1, max=1000, message="last name must be at least 1 character and no more than 1000"),
    ])
    jobTitle = StringField("jobTitle", [
        validators.DataRequired("Job Title must be entered for comparability with our 'Teams' microservice"),
        validators.Length(min=1, max=100, message="Job title must be at least 1 character and no more than 100"),
    ])
    password = StringField("password", [
        validators.DataRequired("You must enter a password to create an account"),
        validators.Length(min=1, max=1000, message="Password must be at least 1 character and no more than 1000")
    ])
    confirmPassword = StringField("confirmPassword", [
        validators.DataRequired("We cannot create your account without a confirmed password"),
        validators.Length(min=1, max=1000, message="Your confirmed password must be at least 1 character and no more than 1000"),
        validators.EqualTo("password", message="Your passwords do not match, please try again"),
    ])

async def sign_up():
    form = SignUpForm(request.form)

    # form had no errors proceed
    if form.validate():
        # check if email has already been registered
        try:
            check_if_email_exists = await User.objects.get(email=request.form['email'])
            if check_if_email_exists:
                return jsonify({
                    "message": "That email is already registered with us, please login to your account or create one with a new email",
                    "email": request.form['email'],
                    "firstName": request.form['firstName'],
                    "jobTitle": request.form['jobTitle'],
                    "lastName": request.form['lastName'],
                    "password": request.form['password'],
                    "confirmPassword": request.form['confirmPassword'],
                })
            
        except Exception as e:
            return jsonify({
                "message": "We could not confirm that email address and had to abort"
            })
        
        # no errors on form, email is not already registered and has been checked, continue sanitizing
        hashed_password = bcrypt.hashpw(request.form['password'].encode("utf-8"), bcrypt.gensalt())
        new_user = User(
            accountType = 'basic',
            calendars = [],
            email = request.form['email'],
            firstName = request.form['firstName'],
            jobTitle = request.form['jobTitle'],
            joined = datetime.now(),
            lastName = request.form['lastName'],
            lastOnline = datetime.now(),
            password = hashed_password,
            tasks = [],
            teams = [],
        )

        # begin uploading user to db
        try: 
            uploadedUser = new_user.save()
            if uploadedUser:
                stripSensitiveData = {
                    "email": new_user.email,
                    "firstName": new_user.firstName,
                    "lastName": new_user.lastName,
                    "jobTitle": new_user.jobTitle,
                }
                return jsonify({
                    "message": "Success, we created your account",
                    "account": stripSensitiveData,
                })
            else:
                return jsonify({
                    "message": "Failed to save user",
                    "email": request.form['email'],
                    "firstName": request.form['firstName'],
                    "jobTitle": request.form['jobTitle'],
                    "lastName": request.form['lastName'],
                    "password": request.form['password'],
                    "confirmPassword": request.form['confirmPassword'],
                })
            
        # failed to upload to db, abort, send form data back
        except Exception as e:
            return jsonify({
                "message": "We failed to create your account, please resubmit your form",
                "email": request.form['email'],
                "firstName": request.form['firstName'],
                "jobTitle": request.form['jobTitle'],
                "lastName": request.form['lastName'],
                "password": request.form['password'],
                "confirmPassword": request.form['confirmPassword'],
            })

    # form had errors return errors and inputs to user   
    else:
        return jsonify({
            "errors": form.errors,
            "email": request.form['email'],
            "firstName": request.form['firstName'],
            "jobTitle": request.form['jobTitle'],
            "lastName": request.form['lastName'],
            "password": request.form['password'],
            "confirmPassword": request.form['confirmPassword']
        })