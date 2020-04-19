# import the modules required for validating the user using json schema
from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError

# define the user schema
user_schema = {
    "type": "object",
    "properties": {
        "username": {
            "type": "string",
        },
        "password": {
            "type": "string",
            "pattern": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
            "minLength": 8
        },
    },
    "required": ["username", "password"],
    "additionalProperties": False
}

# validate the user based data based on the json schema
def validate_user(data):
    try:
        # validate user data with the schema defined above
        validate(data, user_schema)
    except ValidationError as validate_error:
        # if there was a validation error, return the error
        return {'ok': False, 'message': validate_error, 'error': 'validation'}
    except SchemaError as schema_error:
        # if there was a schema error, return the error
        return {'ok': False, 'message': schema_error, 'error': 'schema'}
    # if everything was valid and good, return the data with validation confirmation
    return {'ok': True, 'user_data': data}

