from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'
link = "http://3.237.234.68:8080/"


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file. <a href = />Go Back</a>"
		
    if emp_id == "":
        return "Employee id field is empty! <a href = />Go Back</a>"
		
    if first_name == "":
        return "First name field is empty! <a href = />Go Back</a>"

    if last_name == "":
        return "Last name field is empty! <a href = />Go Back</a>"
	
    if pri_skill == "":
        return "Primary skill field is empty! <a href = />Go Back</a>"
	
    if location == "":
        return "Location field is empty! <a href = />Go Back</a>"

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
            
        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
			ACCESS_ID = 'ASIAUMF277DF5A7V7EKH'
			ACCESS_KEY = 'xI9IFiFmBeDDhyldedjCcXN2MmyDoQi+cPWyVico'
			ACCESS_TOKEN = 'FwoGZXIvYXdzEFwaDBXDs7c3A1AMGIpmcyLPAQYMLYUcHGjzRYFHk9WzAOo/MkAJyOffk12ITbU+cIKtRmoqebHjo+rqRcHts+rQvaFScCr0J/ry0dVyqfk9Uedf8VhfsmHko4JOOtvqax/NtmbeD0L54IU0e+y6tPmlIBC6kp03MVQ8tmyl9F4Kpy8NU8qWamisXRmNC5bNm3fejyjAu4ezg83p3ioXbeshuoll1BrOI3dlxLZbjcBgtUbc2xniJb1ytT4q4o8O4/LdIAPXw8Pdhn4IqZCaO+7haO1ED09k+GtzneA6g4ivryjM2MOSBjItqqZmjwzXtVjFxXE8kfMXXVygjm9Q3eKfCW8Mk0YwQddh2JprRUOD5XnaRg83'
			s3 = boto3.resource('s3', aws_access_key_id=ACCESS_ID, aws_secret_access_key= ACCESS_KEY, aws_session_token = ACCESS_TOKEN)
			
			s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3', aws_access_key_id=ACCESS_ID, aws_secret_access_key= ACCESS_KEY, aws_session_token = ACCESS_TOKEN).get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

        except Exception as e:
            return str(e)

    except Exception as e:
        return str(e)
		
    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/getemp", methods=['POST', 'GET'])
def get_page():
    return render_template('GetEmp.html')

@app.route("/fetchdata", methods=['POST'])
def GetEmp():
    emp_id = request.form['emp_id']
    cursor = db_conn.cursor()
    image_url = ""
    emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"

    try:
        n_rows = cursor.execute("SELECT *  FROM employee where emp_id = %s", emp_id)

        if (n_rows == 0):
            return "No employee with this id."

        details = cursor.fetchone()

        try:		
            print("Data retrieved from MySQL RDS... obtaining image url from S3...")
            ACCESS_ID = 'ASIAUMF277DF5A7V7EKH'
            ACCESS_KEY = 'xI9IFiFmBeDDhyldedjCcXN2MmyDoQi+cPWyVico'
			ACCESS_TOKEN = 'FwoGZXIvYXdzEFwaDBXDs7c3A1AMGIpmcyLPAQYMLYUcHGjzRYFHk9WzAOo/MkAJyOffk12ITbU+cIKtRmoqebHjo+rqRcHts+rQvaFScCr0J/ry0dVyqfk9Uedf8VhfsmHko4JOOtvqax/NtmbeD0L54IU0e+y6tPmlIBC6kp03MVQ8tmyl9F4Kpy8NU8qWamisXRmNC5bNm3fejyjAu4ezg83p3ioXbeshuoll1BrOI3dlxLZbjcBgtUbc2xniJb1ytT4q4o8O4/LdIAPXw8Pdhn4IqZCaO+7haO1ED09k+GtzneA6g4ivryjM2MOSBjItqqZmjwzXtVjFxXE8kfMXXVygjm9Q3eKfCW8Mk0YwQddh2JprRUOD5XnaRg83'
			s3 = boto3.resource('s3', aws_access_key_id=ACCESS_ID, aws_secret_access_key= ACCESS_KEY, aws_session_token = ACCESS_TOKEN)

            bucket = s3.Bucket(custombucket)
            bucket_location = boto3.client('s3', aws_access_key_id=ACCESS_ID, aws_secret_access_key= ACCESS_KEY, aws_session_token = ACCESS_TOKEN)).get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location
				
            image_url = "https://(1)s3{0}.amazonaws.com/{2}".format(s3_location, custombucket, emp_image_file_name_in_s3)
			
        except Exception as e:
            return str(e)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('GetEmpOutput.html', id=details[0], fname=details[1], lname=details[2], interest=details[3], location=details[4], image_url=image_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
