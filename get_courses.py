import json
import urllib3
import datetime
from dateutil import relativedelta

def lambda_handler(event, context):
    print("Received event: " + str(event))
    
    #Common access token and Canvas endpoint URL
    ACCESS_TOKEN = '6936~tfyfufm7EBuCFyJLYcNuP8Pnv6RthDRzv9Xa2vyrxyeUHtKv9WnC2VmX6y2eGNvt'
    CANVAS_BASE_URL = 'https://canvas.instructure.com/api/v1/'
    http = urllib3.PoolManager()
    r = http.request('GET',CANVAS_BASE_URL + 'courses?access_token=' + ACCESS_TOKEN + '&per_page=100&include[]=public_description&include[]=teachers')
    data = json.loads(r.data)
    courses = []
    if event['queryStringParameters'] == None:
        event['queryStringParameters'] = {}
        event['queryStringParameters']['type'] = 'ALL'
    elif 'type' not in event['queryStringParameters']:
        event['queryStringParameters']['type'] = 'ALL'
    else:
        if (event['queryStringParameters']['type'] != 'ALL' and
        event['queryStringParameters']['type'] != 'VISUAL' and
        event['queryStringParameters']['type'] != 'MEDIA' and
        event['queryStringParameters']['type'] != 'SPECIAL' and
        event['queryStringParameters']['type'] != 'DANCE' and
        event['queryStringParameters']['type'] != 'THEATRE' and
        event['queryStringParameters']['type'] != 'PARENT' and
        event['queryStringParameters']['type'] != 'MUSIC'):
            event['queryStringParameters']['type'] = 'ALL'
    for i in data:
        i['id'] = str(i['id'])
        i['account_id'] = str(i['account_id'])
        i['root_account_id'] = str(i['root_account_id'])
        i['enrollment_term_id'] = str(i['enrollment_term_id'])
        if 'public_description' not in i:
            i['public_description'] = 'No Short Description-No Long Description'
        description = i['public_description']
        i['short_description'] = description
        i['long_description'] = description
        if(description.find('-') != -1):
            i['short_description'] = description[:description.find('-')]
            i['long_description'] = description[description.find('-')+1:]
        for j in i['enrollments']:
            j['role_id'] = str(j['role_id'])
            j['user_id'] = str(j['user_id'])
        if i['start_at'] != None and i['end_at'] != None:
            start_date = datetime.datetime.fromisoformat(i['start_at'])
            end_date = datetime.datetime.fromisoformat(i['end_at'])
            duration_days = end_date - start_date
            duration_days = str(duration_days).split(',')
            duration_days = duration_days[0]
            num_days = int(duration_days[:duration_days.index('d')-1])
            num_weeks = num_days // 7
            num_days_remainder = num_days % 7
            if num_days_remainder != 0:
                duration_weeks = str(num_weeks) + " weeks and " + str(num_days_remainder) + " days"
            else:
                duration_weeks = str(num_weeks) + " weeks"
            difference_dates = relativedelta.relativedelta(end_date,start_date)
            num_months = difference_dates.months
            duration_months = str(num_months) + " months"
        else:
            duration_days = "N/A"
            duration_weeks = "N/A"
            duration_months = "N/A"
        course_to_add = {'id': i['id'], 'name': i['name'], 'category': '', 'category_description': '', 'course_code': i['course_code'], 'teachers': [], 'start_at': i['start_at'], 'end_at': i['end_at'], 'course_duration_days': duration_days, 'course_duration_weeks': duration_weeks, 'course_duration_months': duration_months, 'short_description': i['short_description'],
            'long_description': i['long_description'], 'modules': None
        }
        
        for s in i['teachers']:
            course_to_add['teachers'].append({'display_name': s['display_name'], 'avatar_image_url': s['avatar_image_url']})
        
        if i.get('course_code')[0:6] == 'VISUAL':
            course_to_add['category'] = 'VISUAL'
        elif i.get('course_code')[0:5] == 'MEDIA':
            course_to_add['category'] = 'MEDIA'
        elif i.get('course_code')[0:7] == 'SPECIAL':
            course_to_add['category'] = 'SPECIAL'
        elif i.get('course_code')[0:5] == 'DANCE':
            course_to_add['category'] = 'DANCE'
        elif i.get('course_code')[0:7] == 'THEATRE':
            course_to_add['category'] = 'THEATRE'
        elif i.get('course_code')[0:6] == 'PARENT':
            course_to_add['category'] = 'PARENT'
        elif i.get('course_code')[0:5] == 'MUSIC':
            course_to_add['category'] = 'MUSIC'
        
        r2 = http.request('GET', CANVAS_BASE_URL + 'courses/' + course_to_add['id'] + '/modules?access_token=' + ACCESS_TOKEN + '&include=items')
        module_data = json.loads(r2.data)
        modules_to_add = []
        for j in module_data:
            module_to_add = {'name': j['name'], 'items': []}
            for k in j['items']:
                item_to_add = {'title': k['title']}
                if 'page_url' in k:
                    item_to_add['page_url'] = k['page_url']
                module_to_add['items'].append(item_to_add)
            modules_to_add.append(module_to_add)
        course_to_add['modules'] = modules_to_add
        
        if event['queryStringParameters']['type'] == 'ALL':
            courses.append(course_to_add)
        elif i.get('course_code')[0:6] == 'VISUAL' and event['queryStringParameters']['type'] == 'VISUAL':
            courses.append(course_to_add)
        elif i.get('course_code')[0:5] == 'MEDIA' and event['queryStringParameters']['type'] == 'MEDIA':
            courses.append(course_to_add)
        elif i.get('course_code')[0:7] == 'SPECIAL' and event['queryStringParameters']['type'] == 'SPECIAL':
            courses.append(course_to_add)
        elif i.get('course_code')[0:5] == 'DANCE' and event['queryStringParameters']['type'] == 'DANCE':
            courses.append(course_to_add)
        elif i.get('course_code')[0:7] == 'THEATRE' and event['queryStringParameters']['type'] == 'THEATRE':
            courses.append(course_to_add)
        elif i.get('course_code')[0:6] == 'PARENT' and event['queryStringParameters']['type'] == 'PARENT':
            courses.append(course_to_add)
        elif i.get('course_code')[0:5] == 'MUSIC' and event['queryStringParameters']['type'] == 'MUSIC':
            courses.append(course_to_add)
    return {
            'statusCode': 200,
            "headers":{
                'content-type': "application/json",
            },
            'body': json.dumps(courses, separators=(',', ':'))
    }
