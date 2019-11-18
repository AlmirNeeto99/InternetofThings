
import json

def handle_actuator_request(req, broker):
    split_path = req.path.split('/')    
    length = int(req.headers['Content-Length'])
    request_data = req.rfile.read(length)
    request_data = request_data.decode('utf-8')
    json_data = json.loads(request_data)
    if split_path[2] == 'subscribe':
        print('Trying to subscribe a actuator...')
        __subscribe(req, broker, json_data)
    elif split_path[2] == 'receive':
        print('A actuator is trying to read...')
        __receive(req,json_data,broker)
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
    print(subs)        
    req.send_response(201)
    print(f'Actuator with token {token} subscribed...')
    req.wfile.write(bytes(token, 'utf-8'))

def __receive(req, json_data ,broker):
    print(f'Actuator is trying to read...')
    for s in broker.get_subscribers():
        if s['token'] == json_data['token']:
            messages = broker.get_published_messages()
            try:
                message = messages[json_data['topic']]
            except Exception as e:
                req.wfile.write(bytes('No messages in this topic...', 'utf-8'))
                return
            req.send_response(200)
            print('Actuator read a message...')
            req.wfile.write(bytes(str(message), 'utf-8'))
            return
    print('Actuator does not read a message...')
    req.send_response(401)