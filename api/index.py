import sys
import json
import traceback
import pkg_resources

def app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'application/json')]
    start_response(status, response_headers)
    
    try:
        installed = {d.project_name: d.version for d in pkg_resources.working_set}
        import os
        cwd = os.getcwd()
        files = os.listdir(cwd)
        data = {
            "cwd": cwd,
            "sys_path": sys.path,
            "files": files,
            "installed": installed
        }
        return [json.dumps(data).encode('utf-8')]
    except Exception as e:
        return [json.dumps({"error": traceback.format_exc()}).encode('utf-8')]
