# app.py
#
# Use this sample code to handle webhook events in your integration.
#
# 1) Paste this code into a new file (app.py)
#
# 2) Install dependencies
#   pip3 install flask
#   pip3 install stripe
#
# 3) Run the server on http://localhost:4242
#   python3 -m flask run --port=4242

import json
import os
import stripe
import mysql.connector
import datetime

from flask import Flask, jsonify, request
from mysql.connector import Error

# Replace the following values with your MySQL server credentials
host='localhost',
user='root',
password='8689',
database='cosaf_ngo_db',
port ='3306'

# The library needs to be configured with your account's secret key.
# Ensure the key is kept out of any version control system you might be using.
stripe.api_key = "sk_test_51PnT7wRtQ73GLoRxHZYhiDeBaySg9qyrYGk256R5X8aztoBc59Z0Eig35bNc3JC2FvVyMHuVRrrEaPtmjiOAUCfR00yAxvTGv1"

# This is your Stripe CLI webhook secret for testing your endpoint locally.
endpoint_secret = 'whsec_d71e65fbc8e755a1ff440dc46d1ee0018f9d1267cbef907fbd5afae679f438e1'



def create_connection(host_name, user_name, user_password, db_name, port_number):
        connection = None
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='8689',
                database='cosaf_ngo_db',
                port ='3306'
            )
            if connection.is_connected():
                print("Connection to MySQL DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")
        return connection

def execute_query(connection, query, data=None):
    cursor = connection.cursor()
    try:
        cursor.execute(query, data)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

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
            connection = create_connection(host, user, password, database, port)

            # SQL query to insert data into a table
            insert_query = """
            INSERT INTO stripetransaction (TransactionID, Amount, Currency, PaymentStatus, StripeCustomerID) 
            VALUES (%s, %s, %s,%s, %s)
            """

            # Data to be inserted
            data_to_insert = (transaction_id, amount, currency, payment_status,customer_id )

            # Executing the insert query
            execute_query(connection, insert_query, data_to_insert)
        else:
            print('Unhandled event type {}'.format(event['type']))

app = Flask(__name__)
try:
    @app.route('/webhook', methods=['POST'])
    def webhook():
        payload = request.json
        print(f"payload: {payload}")
       
        # Handle the event
        handle_event(payload)

        return jsonify({'status': 'success'}), 200
except mysql.connector.Error as err:
    print(f"Error: {err}")
     
if __name__ == '__main__':
    #context = ('C:\Windows\System32\localhost.pem', 'C:\Windows\System32\localhost-key.pem') ssl_context=context, host='localhost', 
    app.run(port=3000)
