import json
import boto3
import base64

def lambda_handler(event, context):
    try:
        # Initialize S3 client     
        s3 = boto3.client("s3")

        # Get the binary data from the event
        file_content = base64.b64decode(event['content'])
        print('the event is ',event)
        print('the context is',context)
        
        # Define S3 bucket and file key
        bucket_name = "volunteerresume" 
        file_key = "content.pdf"

        # Upload the binary content to S3
        s3_upload = s3.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=file_content,
            ContentType='application/pdf'
        )

        # Construct the S3 file URL
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_key}"

        # Return a success response with the file URL
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'The Object is Uploaded successfully!', 'file_url': file_url})
        }
    except Exception as e:
        # Return an error response in case of failure
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error uploading object: {str(e)}')
        }
