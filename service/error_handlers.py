from flask import jsonify
# from service.models import DataValidationError
from service.models.model_utils import DataValidationError
from . import app, status

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
  """ Handles Value Errors from bad data """
  return bad_request(error)


@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
  """ Handles bad reuests with 400_BAD_REQUEST """
  msg = str(error)
  app.logger.warning(msg)
  return (
      jsonify(
          data = [],
          message = msg
      ),
      status.HTTP_400_BAD_REQUEST,
  )
