from typing import Optional

import rest_framework.status as http_status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import TokenError

from core.exceptions import ExceptionHandlerError


def common_exception_handler(exc, context) -> Optional[Response]:
    response = exception_handler(exc, context)

    if isinstance(exc, ExceptionHandlerError):
        response = Response(status=exc.status)
    if isinstance(exc, TokenError):
        response = Response(status=http_status.HTTP_401_UNAUTHORIZED)

    return response
