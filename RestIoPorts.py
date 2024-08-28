from flask import request
from flask_restful import Resource
from globals import FlaskAPI, ParseConfig
from app_schemas import schema_ioports

class RestIoPorts(Resource):

    def get(self):
        ret = {
                'in_ports': ParseConfig('Ports', 'in_ports', True),
                'out_ports': ParseConfig('Ports', 'out_ports', True)
            }
        
        return schema_ioports.dump(ret)



FlaskAPI.add_resource(RestIoPorts, '/app/v0.1/io_ports')