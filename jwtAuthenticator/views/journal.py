import json
from jwtAuthenticator.schemas.schema_tasks import validate_task
from jwtAuthenticator.models import db
from flask.views import MethodView

from flask_jwt_extended import (
        jwt_required, get_jwt_identity, fresh_jwt_required
)

from flask import (
    request, jsonify
)


