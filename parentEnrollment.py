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

class ParentEnrollment(Resource):
    def post(self):
        connection = None
        try:
            data = request.get_json()
            # Extract parent and address data
            country = data.get('country')
            state = data.get('state')
            city = data.get('city')
            street = data.get('street')
            zipcode = data.get('zipcode')
            firstname = data.get('firstName')
            lastname = data.get('lastName')
            email = data.get('email')
            phone = data.get('phone')
            title = data.get('title')
            passwordhash = data.get('passwordhash')
            seeking_program = data.get('seekingProgram')
            comments = data.get('comments', None)

            # Validate required fields
            if not country or not state or not city or not street or not zipcode:
                return jsonify({'statusCode': 400, 'message': 'Missing required address fields'})
            if not firstname or not lastname or not email or not phone or not title or not passwordhash or not seeking_program:
                return jsonify({'statusCode': 400, 'message': 'Missing required user fields'})
            
            connection = connect_db()

            with connection.cursor() as cursor:
                try:
                    # Insert parent's address data
                    sql_parent_address = """
                        INSERT INTO address (Country, State, City, Street, ZipCode)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_parent_address, (country, state, city, street, zipcode))
                    connection.commit()
                    parent_address_id = cursor.lastrowid
                    # Insert user data
                    sql_user = """
                        INSERT INTO user (FirstName, LastName, Email, Phone, AddressID, Title, PasswordHash)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_user, (firstname, lastname, email, phone, parent_address_id, title, passwordhash))
                    connection.commit()
                    user_id = cursor.lastrowid
                    # Insert parent data
                    sql_parent = """
                        INSERT INTO parent (UserID, SeekingProgram, comments)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(sql_parent, (user_id, seeking_program, comments))
                    connection.commit()
                    return jsonify({'message': 'Parent data inserted successfully'})
                
                except pymysql.Error as e:
                    if e.args[0] == 1205:
                        # Retry logic
                        for attempt in range(3):
                            try:
                                # Repeat the database operations
                                cursor.execute(sql_parent_address, (country, state, city, street, zipcode))
                                connection.commit()
                                parent_address_id = cursor.lastrowid
                                cursor.execute(sql_user, (firstname, lastname, email, phone, parent_address_id, title, passwordhash))
                                connection.commit()
                                user_id = cursor.lastrowid
                                cursor.execute(sql_parent, (user_id, seeking_program, comments))
                                connection.commit()
                                return jsonify({'message': 'Parent data inserted successfully'})
                            except pymysql.Error as retry_error:
                                continue
                    else:
                        return jsonify({"error": str(e)})
        except Exception as e:
            return jsonify({"error": str(e)})
        finally:
            if connection:
                connection.close()
                
api.add_resource(ParentEnrollment, '/parent-enrollment')

if __name__ == '__main__':
    app.run(debug=True)