from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema.exceptions import SchemaError

user_schema = {
    "type": "object",
    "properties": {
        "username": {
            "type": "string",
        },
        "password": {
            "type": "string",
            "minLength": 8
        },
    },
    "required": ["username", "password"],
    "additionalProperties": False
}

def validate_user(data):
    try:
        validate(data, user_schema)
    except ValidationError as validate_error:
        return {'ok': False, 'message': validate_error}
    except SchemaError as schema_error:
        return {'ok': False, 'message': schema_error}

    return {'ok': True, 'user_data': data}

