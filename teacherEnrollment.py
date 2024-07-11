import json
import pymysql
import os
from datetime import datetime

# database connection
def connect_db():
     return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='csofa',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def teacherEnrollment(event,context):
    connection = None
    try:
       body = json.loads(event.get('body'))
   
       country = body.get('country')
       state = body.get('state')
       city = body.get('city')
       street = body.get('street')
       zipcode = body.get('zipcode')
       firstname =body.get('firstName')
       lastname = body.get('lastName')
       email = body.get('email')
       phone = body.get('phone')
       title = body.get('title')
       passwordhash = body.get('passwordhash')
       teachingProgram=body.get('teachingProgram')
       resumeUrl=body.get('resumeUrl')
       refName = body.get('refName')
       refEmail = body.get('refEmail')
       refOrganization = body.get('refOrganization')
       refPhone = body.get('refPhone')
       if not country or not state or not city or not street or not zipcode:
            return {
                    'statusCode': 400,
                    'body': json.dumps({'message': 'Missing required Address fields'})
                }
       if not firstname or not lastname or not email or not phone or not title or not passwordhash:
            return {
                    'statusCode': 400,
                    'body': json.dumps({'message': 'Missing required User Details'})
                }
       if not teachingProgram or not resumeUrl or not refName or not refEmail or not refOrganization or not refPhone:
            return {
                    'statusCode': 400,
                    'body': json.dumps({'message': 'Missing required Teacher Details'})
                }
       
       connection = connect_db()
       with connection.cursor() as cursor:
            addressSql="""
                  INSERT INTO Address (Country, State, City, Street, ZipCode)
                VALUES (%s, %s, %s, %s, %s) 
            """   
            cursor.execute(addressSql, (country, state, city, street, zipcode))
            connection.commit()  
            address_id = cursor.lastrowid 

            sql_user = "INSERT INTO User (FirstName, LastName, Email, Phone, AddressID, Title, PasswordHash) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql_user, (firstname,lastname,email,phone,address_id,title,passwordhash))
            user_id = cursor.lastrowid
            connection.commit() 

            sql_teacher = "INSERT INTO Teacher (UserID, TeachingProgram, ResumeURL, RefName, RefEmail, RefOrganization, RefPhone) VALUES(%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql_teacher,(user_id,teachingProgram,resumeUrl,refName,refEmail,refOrganization,refPhone))
            teacher_id = cursor.lastrowid
            connection.commit() 
            print("Inserted teacher with ID: {teacher_id}")
       return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Data inserted successfully!','teacher_id':teacher_id})
        } 
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error inserting data into RDS',
                'error': str(e)
            })
        } 
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
   
    class Context:
        pass
    event = {
        "body": json.dumps({
             "country": "USA",
            "state": "California",
            "city": "Los Angeles",
            "street": "123 Main St",
            "zipcode": "90001",
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe7@example.com",
            "phone": "+1234567897",
            "title":"testtitle1",
            "passwordhash":"passtest",
            "teachingProgram":"Program1",
            "resumeUrl":"Test-Resume1",
            "refName":"Test-ref1",
            "refEmail":"Test-refEmail123",
            "refOrganization":"Test-refOrganization",
            "refPhone":"Test-refPhone2"
        })
    }
    context = Context()
    print(teacherEnrollment(event, context),"Done")
