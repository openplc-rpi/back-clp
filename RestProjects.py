import os
from flask import request
from flask_restful import Resource
import json

from globals import FlaskAPI, ParseConfig
from app_schemas import schema_project_all,  schema_project

class RestAppUser(Resource):

    def _get_files(self):
        base_dir = ParseConfig('all', 'base_dir')
        files = [f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f)) and f.endswith('.flow')]
        return files

    def get(self):
        #ler os projetos do diretório e montar o json.
        #o diretório esta definido no arquivo app.conf.
        base_dir = ParseConfig('all', 'base_dir')

        project_name = request.args.get('project_name', default = '', type = str)

        project = {}

        if project_name == '':
            files = self._get_files()
            
            project = { "status": 0,
                        "projects": files
                    }
            
            return schema_project_all.dump(project)
        else:
            path = os.path.join(base_dir, project_name)

            try:
                with open(path, 'r') as f:
                    flow = json.load(f)
            except Exception as e:
                return schema_project.dump({'status': 1, 'error_description': str(e)})
            
            project = { "status": 0,
                        "name": project_name,
                        "flowchart": flow
                    }
            return schema_project.dump(project)
        

    def post(self):
        base_dir = ParseConfig('all', 'base_dir')

        if 'project_name' not in request.json:
            return schema_project.dump({'status': 1, 'error_description': 'project_name is required'})

        if 'flowchart' not in request.json:
            return schema_project({'status': 1, 'error_description': 'flowchart is required'})
        
        try:
            new_file = os.path.join(base_dir, request.json['project_name'])

            with open(new_file, 'w') as new_file:
                json.dump(request.json['flowchart'], new_file, indent=4)

        except Exception as e:
            return schema_project.dump({'status': 1, 'error_description': str(e)})

        return schema_project_all.dump({'status': 0, 'projects': self._get_files()}) 


FlaskAPI.add_resource(RestAppUser, '/app/v0.1/projects')