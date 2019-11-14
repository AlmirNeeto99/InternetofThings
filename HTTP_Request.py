def format_request(method, path, data, content_type):
    request = method + ' ' +path + ' HTTP/1.1\r\nHost: localhost:8000\r\n'
    request += f'Content-Type: {content_type}\r\n'
    size = len(data)
    request+= f'Content-Length: {size}\r\n\r\n'
    request += data
    return request