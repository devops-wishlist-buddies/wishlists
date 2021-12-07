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


@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
  """ Handles resources not found with 404_NOT_FOUND """
  msg = str(error)
  app.logger.warning(msg)
  return (
    jsonify(
      data = [],
      message =  msg,
    ),
    status.HTTP_404_NOT_FOUND,
  )


@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
  """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
  msg = str(error)
  app.logger.warning(msg)
  return (
    jsonify(
      data = [],
      message=msg,
    ),
    status.HTTP_405_METHOD_NOT_ALLOWED,
  )


@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
  """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
  msg = str(error)
  app.logger.warning(msg)
  return (
    jsonify(
      data = [],
      message=msg,
    ),
    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
  )


@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
  """ Handles unexpected server error with 500_SERVER_ERROR """
  msg = str(error)
  app.logger.error(msg)
  return (
    jsonify(
      data=[],
      message=msg,
    ),
    status.HTTP_500_INTERNAL_SERVER_ERROR,
  )

@app.errorhandler(TypeError)
def request_type_error(error):
  """Handles Type Error from bad data"""
  return bad_request(error)