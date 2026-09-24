import sys
import os
import json
import traceback

# Ensure the api directory is in the Python path so `app` package can be found
api_dir = os.path.dirname(os.path.abspath(__file__))
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

try:
    from app.main import app
except Exception as e:
    err_traceback = traceback.format_exc()

    async def app(scope, receive, send):
        if scope['type'] == 'lifespan':
            while True:
                message = await receive()
                if message['type'] == 'lifespan.startup':
                    await send({'type': 'lifespan.startup.complete'})
                elif message['type'] == 'lifespan.shutdown':
                    await send({'type': 'lifespan.shutdown.complete'})
                    return
        elif scope['type'] == 'http':
            response_body = json.dumps({
                "error": "Initialization failed",
                "exception": str(e),
                "traceback": err_traceback,
                "python_version": sys.version,
                "sys_path": sys.path,
                "cwd": os.getcwd(),
                "api_dir": api_dir,
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
