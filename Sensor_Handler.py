
import json
from datetime import datetime

def handle_sensor_request(req, broker):
    split_path = req.path.split('/')    
    length = int(req.headers['Content-Length'])
    request_data = req.rfile.read(length)
    request_data = request_data.decode('utf-8')
    json_data = json.loads(request_data)
    if split_path[2] == 'subscribe':
        __subscribe(req, broker, json_data)
    elif split_path[2] == 'publish':
        __publish(req,json_data,broker)
    elif split_path[2] == 'config':
        __config(req, json_data, broker)
    else:
        req.send_response(400) #Bad request

def __subscribe(req, broker, json_data):
    pubs = broker.get_publishers()
    token = req.generate_token()
    try:
        p = pubs[token]
        while True:
            token = req.generate_token()
            try:
                p = pubs[token]
            except Exception as e:
                pubs[token] = {'topic': json_data['topic'], 'id': broker.id, 'status': 'stopped', 'timestamp': datetime.now(), 'command': 'none'}
                broker.id += 1
                break
    except Exception as e:
        pubs[token] = {'topic': json_data['topic'], 'id': broker.id, 'status': 'stopped', 'timestamp': datetime.now(), 'command': 'none'}
        broker.id += 1
    req.send_response(201) #Created
    response = '{"token": "%s"}' %(token)
    req.wfile.write(bytes(response, 'utf-8'))

def __publish(req, json_data ,broker):
    try:
        p = broker.get_publishers()[json_data['token']]
        if json_data['topic'] == p['topic']:            
            p['timestamp'] = datetime.now()
            if json_data['message'] == "{stop}":
                p['status'] = 'stopped'
                response = '{"command": "stop"}'
                req.wfile.write(bytes(response, 'utf-8'))
            else:
                response = '{"command": "%s"}' %(p['command'])
                req.wfile.write(bytes(response, 'utf-8'))
                p['command'] == 'start'
                p['status'] = 'sending'
                broker.published_messages[json_data['topic']] = json_data['message']
            req.send_response(202) #Accepted
            return
        else:
            req.send_response(403) #Forbidden
            return
    except Exception as e:                          
        req.send_response(401) #Unauthorized

def __config(req, json_data, broker):
    action = json_data['action']
    try:
        req.send_response(200)
        p = broker.get_publishers()[json_data['token']]
        p['command'] = action
        req.send_header('Content-Type', 'application/json; charset=UTF-8')            
        req.end_headers()
        req.wfile.write(bytes('{"status": "success"}', 'utf-8'))
        
    except Exception as e:
        req.send_response(401) #Unauthorized 
        req.wfile.write(bytes('{"status": "error"}', 'utf-8'))