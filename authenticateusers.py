import boto3
import json

cognito_client = boto3.client('cognito-idp')

def lambda_handler(event, context):
    email = event['email']
    password = event['password']
    user_type = event['user_type']
    
    try:
        response = cognito_client.admin_initiate_auth(
            UserPoolId='us-east-1_BjLIxSdgv',
            ClientId='3df75m2viojrptnkk4kr80hmo1',
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )
        
        # Check the user's type
        user = cognito_client.admin_get_user(
            UserPoolId='us-east-1_BjLIxSdgv',
            Username=email
        )
        
        attributes = {attr['Name']: attr['Value'] for attr in user['UserAttributes']}
        
        if attributes.get('custom:user_type') != user_type:
            return {
                'statusCode': 400,
                'body': json.dumps('Invalid user type')
            }
        
        # Successful authentication
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Login successful',
                'token': response['AuthenticationResult']['IdToken']
            })
        }

    except cognito_client.exceptions.NotAuthorizedException:
        return {
            'statusCode': 401,
            'body': json.dumps('Invalid email or password')
        }
    except cognito_client.exceptions.UserNotFoundException:
        return {
            'statusCode': 404,
            'body': json.dumps('User does not exist')
        }
