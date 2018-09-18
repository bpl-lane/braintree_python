from braintree.exceptions.unexpected_error import UnexpectedError
from braintree.exceptions.http.connection_error import ConnectionError

class TimeoutError(UnexpectedError):
    pass


class ConnectTimeoutError(TimeoutError):
    pass


class ReadTimeoutError(TimeoutError):
    pass
