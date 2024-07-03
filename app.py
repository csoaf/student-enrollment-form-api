from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import pymysql
import os

app = Flask(__name__)
api = Api(app)

# Database connection
def connect_db():
    return pymysql.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS'],
        port=os.environ['DB_PORT'],
        db=os.environ['DB_NAME'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

class Enrollment(Resource):
    def post(self):
        data = request.get_json()
        
        # Student information
        first_name = data['firstName']
        last_name = data['lastName']
        email = data['email']
        phone = data['phone']
        date_of_birth = data['dateOfBirth']
        gender = data['gender']
        ethnicity = data['ethnicity']
        seeking_program = data['seekingProgram']
        last_grade_completed = data['lastGradeCompleted']
        ec_first_name = data['ecFirstName']
        ec_last_name = data['ecLastName']
        ec_phone = data['ecPhone']
        relation_to_student = data['relationToStudent']
        
        # Student's address
        student_country = data['country']
        student_state = data['state']
        student_city = data['city']
        student_street = data['street']
        student_zipcode = data['zipcode']

        # School information
        school_name = data['schoolName']
        school_country = data['schoolCountry']
        school_state = data['schoolState']
        school_city = data['schoolCity']
        school_street = data['schoolStreet']
        school_zipcode = data['schoolZipcode']
        
        connection = connect_db()
        try:
            with connection.cursor() as cursor:
                # Insert student's address data
                sql_student_address = "INSERT INTO address (Country, State, City, Street, ZipCode) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql_student_address, (student_country, student_state, student_city, student_street, student_zipcode))
                student_address_id = cursor.lastrowid

                # Insert user data
                sql_user = "INSERT INTO user (FirstName, LastName, Email, Phone, AddressID) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql_user, (first_name, last_name, email, phone, student_address_id))
                user_id = cursor.lastrowid

                # Check if school exists by name and street
                sql_check_school = """
                SELECT school.SchoolID 
                FROM school 
                JOIN address ON school.AddressID = address.AddressID 
                WHERE school.SchoolName = %s AND address.Street = %s
                """
                cursor.execute(sql_check_school, (school_name, school_street))
                school = cursor.fetchone()

                if school:
                    school_id = school['SchoolID']
                    # Get the school's address ID
                    sql_get_school_address_id = "SELECT AddressID FROM school WHERE SchoolID = %s"
                    cursor.execute(sql_get_school_address_id, (school_id,))
                    school_address_id = cursor.fetchone()['AddressID']
                else:
                    # Insert school's address data
                    sql_school_address = "INSERT INTO address (Country, State, City, Street, ZipCode) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql_school_address, (school_country, school_state, school_city, school_street, school_zipcode))
                    school_address_id = cursor.lastrowid

                    # Insert school data
                    sql_school = "INSERT INTO school (SchoolName, AddressID, UserID, SeekingProgram) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql_school, (school_name, school_address_id, user_id, seeking_program))
                    school_id = cursor.lastrowid

                # Insert student data
                sql_student = """
                INSERT INTO student (UserID, DateofBirth, Gender, Ethnicity, SeekingProgram, LastGradeCompleted, SchoolID, ParentID, ECFirstName, ECLastName, ECPhone, RelationtoStudent) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_student, (user_id, date_of_birth, gender, ethnicity, seeking_program, last_grade_completed, school_id, None, ec_first_name, ec_last_name, ec_phone, relation_to_student))
                
            connection.commit()
            return jsonify({"message": "Student enrolled successfully!"})
        except Exception as e:
            return jsonify({"error": str(e)})
        finally:
            connection.close()

api.add_resource(Enrollment, '/enroll')

if __name__ == '__main__':
    app.run(debug=True)
