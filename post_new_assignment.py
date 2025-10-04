import json
import string
import urllib3
from http.client import responses

def lambda_handler(event, context):
    api_call = "https://canvas.instructure.com/api/v1/courses/"
    api_call += str(event['course_id'])
    api_call += "/assignments?access_token=6936~tfyfufm7EBuCFyJLYcNuP8Pnv6RthDRzv9Xa2vyrxyeUHtKv9WnC2VmX6y2eGNvt"
    api_call += "&assignment[name]="
    api_call += str(event['name'])
    api_call += "&assignment[position]="
    api_call += str(event['position'])
    api_call += "&assignment[submission_types][]="
    for i in event['submission_types']:
        api_call += str(i) + ","
    api_call = api_call[:-1]
    api_call += "&assignment[allowed_extensions][]="
    for i in event['allowed_extensions']:
        api_call += str(i) + ","
    api_call = api_call[:-1]
    api_call += "&assignment[points_possible]="
    api_call += str(event['points_possible'])
    api_call += "&assignment[grading_type]="
    api_call += str(event['grading_type'])
    api_call += "&assignment[due_at]="
    api_call += str(event['due_at'])
    api_call += "&assignment[lock_at]="
    api_call += str(event['lock_at'])
    api_call += "&assignment[unlock_at]="
    api_call += str(event['unlock_at'])
    api_call += "&assignment[description]="
    api_call += str(event['description'])
    api_call += "&assignment[published]="
    api_call += str(event['published']).lower()
    api_call += "&assignment[anonymous_grading]="
    api_call += str(event['anonymous_grading']).lower()
    api_call += "&assignment[allowed_attempts]="
    api_call += str(event['allowed_attempts'])
    http = urllib3.PoolManager()
    r = http.request('POST', api_call)
    return {
        'status_code': r.status,
        'status_description': responses[r.status]
    }
