import json
import boto3
import base64
import uuid

def lambda_handler(event, context):
    try:
        s3 = boto3.client("s3")
        file_content = base64.b64decode(event['body'])
        headers = event.get('headers', {})
        file_name = headers.get('File-Name', '')

        bucket_name = "csaofuploadresumefiles"
        file_type = ".pdf"
        file_uuid = uuid.uuid4().hex
        file_key = file_name if file_name else f"{file_uuid}{file_type}"

        s3.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=file_content,
            ContentType='application/pdf'
        )

        file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_key}"

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, File-Name',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'message': 'The Object is Uploaded successfully!', 'file_url': file_url})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(f'Error uploading object: {str(e)}')
        }
