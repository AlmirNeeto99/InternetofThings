
import json

def handle_sensor_request(req, broker):
    split_path = req.path.split('/')    
    length = int(req.headers['Content-Length'])
    request_data = req.rfile.read(length)
    request_data = request_data.decode('utf-8')
    json_data = json.loads(request_data)
    if split_path[2] == 'subscribe':
        print('Trying to subscribe a sensor...')
        __subscribe(req, broker, json_data)
    elif split_path[2] == 'publish':
        print('A sensor is trying to publish...')
        __publish(req,json_data,broker)
    else:
        req.send_response(400)

def __subscribe(req, broker, json_data):
    pubs = broker.get_publishers()
    token = req.generate_token()
    created = False
    for p in pubs:
        if token == p['token']: # if a publisher with generated token doesnt exists, create one
            continue
        new_pub = {'token': token, 'id': broker.id, 'topic': json_data['topic']}
        broker.id += 1
        pubs.append(new_pub)
        created = True
    if not created:        
        exists = True
        while exists:
            token = req.generate_token()
            if len(pubs) == 0:
                new_pub = {'token': token, 'id': broker.id, 'topic': json_data['topic']}
                broker.id += 1
                exists = False
            for p in pubs:
                if token not in p['token']:        
                    new_pub = {'token': token, 'id': broker.id, 'topic': json_data['topic']}
                    broker.id += 1
                    exists = False
                    break            
        pubs.append(new_pub)
    print(pubs)        
    req.send_response(201)
    print(f'Sensor with token {token} subscribed...')
    req.wfile.write(bytes(token, 'utf-8'))

def __publish(req, json_data ,broker):    
    for p in broker.get_publishers():
        if json_data['token'] == p['token']:
            if json_data['topic'] == p['topic']:                
                broker.published_messages[json_data['topic']] = json_data['message']
                print('Sensor published on topic', json_data['topic'] ,'successfully...')
                req.send_response(202)
                return
            else:
                print('Sensor doe\'nt belog to topic', json_data['topic'] ,'...')
                req.send_response(403)
                return
    print('Sensor with this token it\'s not subscribed...')
    req.send_response(401)