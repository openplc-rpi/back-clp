from globals import marshmallow
from pydantic import conlist


class ProjectSchemaAll(marshmallow.Schema):
    class Meta:
        fields = ("status", "error_description", "projects")
    projects = conlist(str)

schema_project_all = ProjectSchemaAll()