import sys
import os
import json
import traceback

api_dir = os.path.dirname(os.path.abspath(__file__))
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

try:
    from app.main import app
except Exception as e:
    err_traceback = traceback.format_exc()
    
    async def app(scope, receive, send):
        if scope['type'] != 'http':
            return
            
        response_body = json.dumps({
            "error": "Initialization failed",
            "traceback": err_traceback,
            "python_version": sys.version,
        }).encode('utf-8')
        
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                [b'content-type', b'application/json'],
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': response_body,
        })
