from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError

# define the tasks data
tasks_schema = {
    "type": "object",
    "properties": {
        "description": {
            "type": "string",
        },
    },
    "required": ["description"],
    "additionalProperties": False
}

def validate_task(data):

    try:
        # validate the task data with the above defined above
        validate(data, tasks_schema)

    except ValidationError as validate_error:
        # if there was a validation error, return the error
        return {'ok': False, 'message': validate_error, 'error': 'validation'}

    except SchemaError as schema_error:
        # if there was a schema error, return the error
        return {'ok': False, 'message': schema_error, 'error': 'schema'}

    # if everything was valid, return the data with validation confirmation
    return {'ok': True, 'tasks_data': data}
