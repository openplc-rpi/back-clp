import os
from flask import request
from flask_restful import Resource
import json
from executor import Executor

from globals import FlaskAPI, ParseConfig
from app_schemas import schema_project, schema_is_running

ExecutorInstance = None

class RestStart(Resource):
    def get(self):
        ret = { "status": 0,
                    "is_running": True if ExecutorInstance is not None else False
                }
        return schema_is_running.dump(ret)
        

    def put(self):
        global ExecutorInstance

        if 'state' not in request.json or 'filename' not in request.json:
            return schema_project.dump({'status': 1, 'error_description': 'state and filename are required'})

        state = request.json['state']
        filename = request.json['filename']

        if state == 'start' and ExecutorInstance is None:
            ExecutorInstance = Executor(filename='projects/'+filename)
            ExecutorInstance.start()
            print('Executor started')

        elif state == 'stop' and ExecutorInstance is not None:
                ExecutorInstance.stop()
                ExecutorInstance = None
                print('Executor stopped')

        return schema_is_running.dump({'status': 0, 'is_runnging': True if ExecutorInstance is None else False}) 


FlaskAPI.add_resource(RestStart, '/app/v0.1/start')