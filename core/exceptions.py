from rest_framework import status as http_status


class ExceptionHandlerErrorMeta(type):
    def __new__(mcs, name, bases, dct, status=None):
        dct["status"] = status
        return super().__new__(mcs, name, bases, dct)


class ExceptionHandlerError(Exception, metaclass=ExceptionHandlerErrorMeta):
    status: int


class BadRequestError(ExceptionHandlerError, status=http_status.HTTP_400_BAD_REQUEST):
    pass


class NotFoundError(ExceptionHandlerError, status=http_status.HTTP_404_NOT_FOUND):
    pass
