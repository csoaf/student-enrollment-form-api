import json
import urllib3

def lambda_handler(event, context):
    print("Received event: " + str(event))
    api_call = 'https://canvas.instructure.com/api/v1/courses/' + str(event['queryStringParameters']['course_id']) + ('/modules?access_token=6936~tfyfufm7EBuCFyJLYcNuP8Pnv6RthDRzv9Xa2vyrxyeUHtKv9WnC2VmX6y2eGNvt&include=items')
    http = urllib3.PoolManager()
    r = http.request('GET', api_call)
    data = json.loads(r.data)
    modules = []
    for i in data:
        i['id'] = str(i['id'])
        for j in i['items']:
            j['id'] = str(j['id'])
            j['module_id'] = str(j['module_id'])
            j['content_id'] = str(j['content_id'])
        modules.append(i)
    return {
            'statusCode': 200,
            "headers":{
                'content-type': "application/json"
            },
            'body': json.dumps(modules, separators=(',', ':'))
    }
