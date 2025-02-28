from globals import marshmallow
from pydantic import conlist


class ProjectSchemaAll(marshmallow.Schema):
    class Meta:
        fields = ("status", "error_description", "projects")
    projects = conlist(str)

schema_project_all = ProjectSchemaAll()


class ProjectSchema(marshmallow.Schema):
    class Meta:
        fields = ("status", "error_description", "name", "flowchart")

schema_project = ProjectSchema()


class IOPortsSchema(marshmallow.Schema):
    class Meta:
        fields = ('in_ports', 'out_ports')
    in_ports = conlist(str)
    out_ports = conlist(str)

schema_ioports = IOPortsSchema()


class isRunningSchema(marshmallow.Schema):
    class Meta:
        fields = ('status', 'is_running',)

schema_is_running = isRunningSchema()