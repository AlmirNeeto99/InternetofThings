
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
    elif split_path[2] == 'state':
        __status(req,json_data,broker)
    elif split_path[2] == 'config':
        __config(req,json_data,broker)
    else:
        req.send_response(400)

def __subscribe(req, broker, json_data):
    subs = broker.get_subscribers()
    token = req.generate_token()
    created = False
    for s in subs:
        if token == s['token']: # if a publisher with generated token doesnt exists, create one
            continue
        new_sub = {'token': token, 'id': broker.id, 'topic': json_data['topic']}
        broker.id += 1
        subs.append(new_sub)
        created = True
    if not created:        
        exists = True
        while exists:
            token = req.generate_token()
            if len(subs) == 0:
                new_sub = {'token': token, 'id': broker.id, 'topic': json_data['topic']}
                broker.id += 1
                exists = False
            for s in subs:
                if token not in s['token']:        
                    new_sub = {'token': token, 'id': broker.id, 'topic': json_data['topic']}
                    broker.id += 1
                    exists = False
                    break            
        subs.append(new_sub)      
    req.send_response(201)
    req.wfile.write(bytes(token, 'utf-8'))

def __receive(req, json_data ,broker):
    for s in broker.get_subscribers():
        if s['token'] == json_data['token']:
            messages = broker.get_published_messages()
            try:
                message = messages[json_data['topic']]
            except Exception as e:
                req.wfile.write(bytes('No messages in this topic...', 'utf-8'))
                return
            req.send_response(200)
            req.wfile.write(bytes(str(message), 'utf-8'))
            return
    req.send_response(401)

def __status(req, json_data, broker):
    try:
        p = broker.get_subscribers()[json_data['token']]
        response = '{"status": "%s"}' %(p['status'])
        req.wfile.write(bytes(response, 'utf-8'))
        req.send_response(200)
    except Exception as e:
        req.send_response(401) #Unauthorized

def __config(req, json_data, broker):
    a = json_data['action']
    try:
        p = broker.get_subscribers()[json_data['token']]
        p['status'] = a
        req.wfile.write(bytes('{"status": "success"}', 'utf-8'))
        req.send_response(200)
    except Exception as e:
        req.wfile.write(bytes('{"status": "error"}', 'utf-8'))
        req.send_response(401) #Unauthorized 