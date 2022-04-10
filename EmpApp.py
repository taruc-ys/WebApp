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
ACCESS_ID = 'ASIAUMF277DFYYPFLL3Y'
ACCESS_KEY = 'fsS2SdWSv/AKgMXJlkgeOWTR8CaQx97KY2M1tkZL'
ACCESS_TOKEN = 'FwoGZXIvYXdzEHUaDFivxJaHqoZ59K/irSLPAbXNbVsxYiRpS+RD1VgP751zM4YiYTxbPpqP3FnduF7unjhUcYNT5v8iI8AEPwI8IuPprCDQXE/P9hOim8Yr/Bztt0SLKKttjczFdJlXkF84FfrQp7K3XngTZCOrSElVeM3PyXvlfFxk1S+DdQ/xXUbZILdK85d+Z5CmAS3ByLBl+lKQEbasVAddDgYbnjOPmfMRotOnnFuKaVj0bowgk7yfV6HaXVZsRb91mOMEs2tWz2Y89YjWteizocN/iWPN9wEFGYlyJKRwIjKU1rgw1yiGoMmSBjItzMlpNdunhYkyhxfTeUpYPDKORXrotoQA92YUOV05pVbTmW9mNP13q0XoOfcO'


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
