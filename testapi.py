import json
import mysql.connector
import datetime
    
    
rds_host = "database-csoaf.cz0kgu4o8jn1.us-east-1.rds.amazonaws.com"
db_username = "Mikhilesh"
db_password = "Mikhilesh123"
db_name = "csoaf_db"
db_port = "3306"


def lambda_handler(event, context):
    payload = json.dumps(event)
    print(f"payload: {payload}")
       
        # Handle the event
    handle_event(event)

    # return jsonify({'status': 'success'}), 200
    return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Stripe User details successfully stored',
                'user': event['data']['object']['customer']
            })
        }

def handle_event(event):
    event_type = event['type']
    data = event['data']['object']
    print(f"Received event: {event_type}")
    print(f"PaymentIntent data: {data}")

    if event_type == 'payment_intent.succeeded':
         # Extract relevant information
        transaction_id = str(data['id'])
        amount = str(data['amount_received'] / 100)  # Convert to dollars
        currency = str(data['currency'])
        payment_status = str(data['status'])
        customer_id = str(data['customer'])
            
        # Establishing the connection
        connection = create_connection(rds_host, db_username, db_password, db_name, db_port)

        # SQL query to insert data into a table
        insert_query = """
        INSERT INTO stripe_transaction (TransactionID, Amount, Currency, PaymentStatus, StripeCustomerID) 
        VALUES (%s, %s, %s,%s, %s)
        """

        # Data to be inserted
        data_to_insert = (transaction_id, amount, currency, payment_status,customer_id )

        # Executing the insert query
        execute_query(connection, insert_query, data_to_insert)
    else:
        print('Unhandled event type {}'.format(event['type']))
        return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': 'Stripe transaction is not successful',
                })
            
            }

def execute_query(connection, query, data=None):
        cursor = connection.cursor()
        try:
            #with connection.cursor() as cursor:
                cursor.execute(query, data)
                connection.commit()
                print("Query executed successfully")
        except Exception as e:
            print(f"The error '{e}' occurred")
    

def create_connection(host_name, user_name, user_password, db_name, db_port):
    connection = None
    # Connect to the RDS MySQL database
    try:
        print("Connecting to RDS MySQL database")
        connection = mysql.connector.connect(
            host=rds_host,
            user=db_username,
            password=db_password,
            db=db_name,
            connect_timeout=20
        )
        print("Connected to RDS successfully")
       
        return connection   
    except Exception as e:
        print(f"The error '{e}' occurred")
        print(f"Error connecting to RDS: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Could not connect to the database',
                'error': str(e)
            })
        }
    
