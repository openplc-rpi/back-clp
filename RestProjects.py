from flask import request
from flask_restful import Resource
from globals import FlaskAPI
from app_schemas import schema_project_all

class RestAppUser(Resource):


    def get(self):
        #ler os projetos do diretório e montar o json.
        #o diretório esta definido no arquivo app.conf.
        
        project = { "status": 0,
                   "projects": [
                     "file1.flow", 
                     "file2.flow"
                   ]
                }
        return schema_project_all.dump(project)


    def post(self):
        #implementar o salvamento do flowchart no diretório.
        pass


FlaskAPI.add_resource(RestAppUser, '/app/v0.1/projects')