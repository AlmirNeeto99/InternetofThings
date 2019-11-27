
import json

def handle_actuator_request(req, broker):
    split_path = req.path.split('/')    
    length = int(req.headers['Content-Length'])
    request_data = req.rfile.read(length)
    request_data = request_data.decode('utf-8')
    json_data = json.loads(request_data)
    if split_path[2] == 'subscribe':
        __subscribe(req, broker, json_data)
    elif split_path[2] == 'receive':
        __receive(req,json_data,broker)
    elif split_path[2] == 'config':
        if split_path[3] == 'app':
            __config(req, json_data, broker)
        elif split_path[3] == 'device':
            __config_device(req, json_data, broker) 
    else:
        req.send_response(400)
    return

def __subscribe(req, broker, json_data):
    subs = broker.get_subscribers()
    token = req.generate_token()
    try:
        p = subs[token]
        while True:
            token = req.generate_token()
            try:
                p = subs[token]
            except Exception as e:
                subs[token] = {'topic': json_data['topic'], 'id': broker.id, 'command': 'none', 'data': 0}
                broker.id += 1
                break
    except Exception as e:
        subs[token] = {'topic': json_data['topic'], 'id': broker.id, 'command': 'none', 'data': 0}
        broker.id += 1
    req.send_response(201) #Created
    response = '{"token": "%s"}' %(token)
    req.wfile.write(bytes(response, 'utf-8'))
    return

def __receive(req, json_data ,broker):
    try:
        p = broker.get_subscribers()[json_data['token']]
        if json_data['topic'] == p['topic']:
            try:
                msg = broker.published_messages[json_data['topic']]
                p['data'] = msg
                response = '{"message": "%s", "command": "%s"}' %(p['data'], p['command'])
                req.wfile.write(bytes(response, 'utf-8'))
            except Exception as e:
                response = '{"message": "0", "command": "%s"}' %(p['command'])
                req.wfile.write(bytes(response, 'utf-8'))
            req.send_response(200) #Accepted
            return
        else:
            req.send_response(403) #Forbidden
            return
    except Exception as e:                          
        req.send_response(401) #Unauthorized
    return

def __config(req, json_data, broker):
    action = json_data['action']
    try:
        p = broker.get_subscribers()[json_data['token']]
        p['command'] = action
        req.send_header('Content-Type', 'application/json; charset=UTF-8')            
        req.end_headers()   
        req.wfile.write(bytes('{"status": "success"}', 'utf-8'))
        req.send_response(200)
    except Exception as e:
        req.wfile.write(bytes('{"status": "error"}', 'utf-8'))
        req.send_response(401) #Unauthorized 
    return

def __config_device(req, json_data, broker):
    action = json_data['action']
    try:
        p = broker.get_subscribers()[json_data['token']]
        p['command'] = action
        req.wfile.write(bytes('{"status": "success"}', 'utf-8'))
        req.send_response(200)
    except Exception as e:
        req.wfile.write(bytes('{"status": "error"}', 'utf-8'))
        req.send_response(401) #Unauthorized
    return