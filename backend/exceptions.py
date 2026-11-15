class SourceNotFoundError(Exception):
    pass


class EmailAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class MangadexError(Exception):
    pass


class MangadexNotFoundError(MangadexError):
    pass


class MangadexTimeoutError(MangadexError):
    pass


class MangadexUnavailableError(MangadexError):
    pass
