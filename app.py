from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import pymysql
import json

app = Flask(__name__)
api = Api(app)

# Database connection
def connect_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        db='csoaf',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

class Enrollment(Resource):
    def post(self):
        connection = None
        try:
            data = request.get_json()

            # Extract student and address data
            country = data.get('country')
            state = data.get('state')
            city = data.get('city')
            street = data.get('street')
            zipcode = data.get('zipcode')
            firstname = data.get('firstName')
            lastname = data.get('lastName')
            email = data.get('email')
            phone = data.get('phone')
            eligibility = data.get('eligibility')
            title = data.get('title')
            passwordhash = data.get('passwordhash')
            date_of_birth = data.get('dateOfBirth')
            gender = data.get('gender')
            ethnicity = data.get('ethnicity')
            seeking_program = data.get('seekingProgram')
            last_grade_completed = data.get('lastGradeCompleted')
            ec_first_name = data.get('ecFirstName')
            ec_last_name = data.get('ecLastName')
            ec_phone = data.get('ecPhone')
            relation_to_student = data.get('relationToStudent')
            school_name = data.get('schoolName')
            school_country = data.get('schoolCountry')
            school_state = data.get('schoolState')
            school_city = data.get('schoolCity')
            school_street = data.get('schoolStreet')
            school_zipcode = data.get('schoolZipcode')

            # Validate required fields
            if not country or not state or not city or not street or not zipcode:
                return jsonify({'statusCode': 400, 'message': 'Missing required fields'})

            connection = connect_db()
            with connection.cursor() as cursor:
                try:
                    # Insert student's address data
                    sql_student_address = """
                        INSERT INTO address (Country, State, City, Street, ZipCode)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_student_address, (country, state, city, street, zipcode))
                    connection.commit()
                    student_address_id = cursor.lastrowid

                    # Insert user data
                    sql_user = """
                        INSERT INTO user (FirstName, LastName, Email, Phone, AddressID, Title, PasswordHash)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_user, (firstname, lastname, email, phone, student_address_id, title, passwordhash))
                    connection.commit()
                    user_id = cursor.lastrowid

                    # Check if school exists by name and street
                    sql_check_school = """
                    SELECT SchoolID 
                    FROM School 
                    JOIN Address ON School.AddressID = Address.AddressID 
                    WHERE School.SchoolName = %s AND Address.Street = %s
                    """
                    cursor.execute(sql_check_school, (school_name, school_street))
                    school = cursor.fetchone()

                    if school:
                        school_id = school['SchoolID']
                        # Get the school's address ID
                        sql_get_school_address_id = "SELECT AddressID FROM School WHERE SchoolID = %s"
                        cursor.execute(sql_get_school_address_id, (school_id,))
                        school_address_id = cursor.fetchone()['AddressID']
                    else:
                        # Insert school's address data
                        sql_school_address = """
                            INSERT INTO address (Country, State, City, Street, ZipCode)
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(sql_school_address, (school_country, school_state, school_city, school_street, school_zipcode))
                        connection.commit()
                        school_address_id = cursor.lastrowid

                        # Insert school data
                        sql_school = """
                            INSERT INTO school (SchoolName, AddressID, UserID, SeekingProgram)
                            VALUES (%s, %s, %s, %s)
                        """
                        cursor.execute(sql_school, (school_name, school_address_id, user_id, seeking_program))
                        connection.commit()
                        school_id = cursor.lastrowid

                    # Insert student data
                    sql_student = """
                    INSERT INTO student (UserID, DateOfBirth, Gender, Ethnicity, Eligibility, SeekingProgram, LastGradeCompleted, SchoolID, ParentID, ECFirstName, ECLastName, ECPhone, RelationToStudent)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_student, (user_id, date_of_birth, gender, ethnicity, eligibility, seeking_program, last_grade_completed, school_id, None, ec_first_name, ec_last_name, ec_phone, relation_to_student))
                    connection.commit()

                    return jsonify({'message': 'Data inserted successfully'})

                except pymysql.Error as e:
                    if e.args[0] == 1205:
                        # Retry logic
                        for attempt in range(3):
                            try:
                                # Repeat the database operations
                                cursor.execute(sql_student_address, (country, state, city, street, zipcode))
                                connection.commit()
                                student_address_id = cursor.lastrowid

                                cursor.execute(sql_user, (firstname, lastname, email, phone, student_address_id, title, passwordhash))
                                connection.commit()
                                user_id = cursor.lastrowid

                                cursor.execute(sql_check_school, (school_name, school_street))
                                school = cursor.fetchone()

                                if school:
                                    school_id = school['SchoolID']
                                    sql_get_school_address_id = "SELECT AddressID FROM School WHERE SchoolID = %s"
                                    cursor.execute(sql_get_school_address_id, (school_id,))
                                    school_address_id = cursor.fetchone()['AddressID']
                                else:
                                    cursor.execute(sql_school_address, (school_country, school_state, school_city, school_street, school_zipcode))
                                    connection.commit()
                                    school_address_id = cursor.lastrowid

                                    cursor.execute(sql_school, (school_name, school_address_id, user_id, seeking_program))
                                    connection.commit()
                                    school_id = cursor.lastrowid

                                cursor.execute(sql_student, (user_id, date_of_birth, gender, ethnicity, eligibility, seeking_program, last_grade_completed, school_id, None, ec_first_name, ec_last_name, ec_phone, relation_to_student))
                                connection.commit()

                                return jsonify({'message': 'Data inserted successfully'})
                            except pymysql.Error as retry_error:
                                continue
                    else:
                        return jsonify({"error": str(e)})
        except Exception as e:
            return jsonify({"error": str(e)})
        finally:
            if connection:
                connection.close()

api.add_resource(Enrollment, '/student-enrollment')

if __name__ == '__main__':
    app.run(debug=True)
