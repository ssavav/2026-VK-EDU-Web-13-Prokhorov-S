import urllib.parse

def application(environ, start_response):
    get_str = environ.get('QUERY_STRING', '')
    get_params = urllib.parse.parse_qs(get_str)
    
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError, TypeError):
        request_body_size = 0
        
    request_body = environ.get('wsgi.input').read(request_body_size)
    post_params = urllib.parse.parse_qs(request_body.decode('utf-8'))
    
    response_text = f"GET: {get_params}\nPOST: {post_params}\n"
    response_body = response_text.encode('utf-8')
    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/plain; charset=utf-8'),
        ('Content-Length', str(len(response_body)))
    ]
    
    start_response(status, response_headers)
    return [response_body]