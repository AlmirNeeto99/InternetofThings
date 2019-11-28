import json

def handle_sensor_request(req, broker):
    split_path = req.path.split('/')    #split the requested URL
    # Gets the size of the data sent to the server
    length = int(req.headers['Content-Length'])
    #Read this content and converts it to JSON
    request_data = req.rfile.read(length)
    request_data = request_data.decode('utf-8')
    json_data = json.loads(request_data)
    if split_path[2] == 'subscribe': # Subscribe a sensor
        __subscribe(req, broker, json_data)
    elif split_path[2] == 'publish': # Save a message
        __publish(req,json_data,broker)
    elif split_path[2] == 'config':
        if split_path[3] == 'app': # Route to configure a actuator via application
            __config(req, json_data, broker)
        elif split_path[3] == 'device': # Route to configure a actuator via device
            __config_device(req, json_data, broker)        
    else:
        req.send_response(400) #Bad request
    return

def __subscribe(req, broker, json_data):
    pubs = broker.get_publishers()
    token = req.generate_token()
    # Generate an unique token to a sensor
    try:
        p = pubs[token]
        while True:
            token = req.generate_token()
            try:
                p = pubs[token]
            except Exception as e:
                pubs[token] = {'topic': json_data['topic'], 'id': broker.id, 'command': 'none', 'data': 0}
                broker.id += 1
                break
    except Exception as e:
        pubs[token] = {'topic': json_data['topic'], 'id': broker.id, 'command': 'none', 'data': 0}
        broker.id += 1 # Increment unique ID to devices
    req.send_response(201) #Created
    response = '{"token": "%s"}' %(token)
    req.wfile.write(bytes(response, 'utf-8'))
    return

def __publish(req, json_data ,broker):
    try:
        p = broker.get_publishers()[json_data['token']]
        if json_data['topic'] == p['topic']:
            if json_data['message'] == "{stop}":
                p['command'] = 'stop' # receive a command from application (browser) and refresh device
                response = '{"command": "stop"}'
                req.wfile.write(bytes(response, 'utf-8'))
            else:
                response = '{"command": "%s"}' %(p['command'])
                req.wfile.write(bytes(response, 'utf-8'))
                p['data'] = json_data['message']
                broker.published_messages[json_data['topic']] = json_data['message']
            req.send_response(202) #Accepted
            return
        else:
            req.send_response(403) #Forbidden
            return
    except Exception as e:                          
        req.send_response(401) #Unauthorized
    return

def __config(req, json_data, broker):
    req.send_response(200)
    action = json_data['action']
    try:        
        p = broker.get_publishers()[json_data['token']]
        p['command'] = action # receive a command from device and refresh it
        req.send_header('Content-Type', 'application/json; charset=UTF-8')            
        req.end_headers()              
        req.wfile.write(bytes('{"status": "success"}', 'utf-8'))    
    except Exception as e:
        req.send_response(401) #Unauthorized 
        req.wfile.write(bytes('{"status": "error"}', 'utf-8'))
    return

def __config_device(req, json_data, broker):
    req.send_response(200)
    action = json_data['action']
    try:        
        p = broker.get_publishers()[json_data['token']]
        p['command'] = action              
        req.wfile.write(bytes('{"status": "success"}', 'utf-8'))                   
    except Exception as e:
        req.send_response(401) #Unauthorized 
        req.wfile.write(bytes('{"status": "error"}', 'utf-8'))
    return