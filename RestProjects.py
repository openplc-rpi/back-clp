import os

from flask import request
from flask_restful import Resource
from globals import FlaskAPI, ParseConfig
from app_schemas import schema_project_all

class RestAppUser(Resource):


    def get(self):
        #ler os projetos do diretório e montar o json.
        #o diretório esta definido no arquivo app.conf.
        base_dir = ParseConfig('all', 'base_dir')

        project_name = request.args.get('project_name', default = '', type = str)

        if project_name == '':
            #retornar todos os projetos.
            pass
        else:
            #retornar o projeto solicitado.
            pass

        
        project = { "status": 0,
                   "projects": [
                     "file1.flow", 
                     "file2.flow"
                   ]
                }
        return schema_project_all.dump(project)


    def post(self):
        #implementar o salvamento do flowchart no diretório.

        base_dir = ParseConfig('all', 'base_dir')
        file_name = 'flowchart'
        try:
            new_file_json = os.path.join(base_dir, '%s.json' % file_name)
            file_json = open(new_file_json, 'w+')

            try:
                file_json.write('conteudo')
            finally:
                file_json.close()

            return True
        except:
            return None



FlaskAPI.add_resource(RestAppUser, '/app/v0.1/projects')