class SourceNotFoundError(Exception):
    pass


class EmailAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class SubscriptionNotFoundError(Exception):
    pass


class NotificationNotFoundError(Exception):
    pass


class MangadexNotFoundError(Exception):
    pass


class MangadexError(Exception):
    pass


class AthreaError(Exception):
    pass


class AthreaNotFoundError(Exception):
    pass


class EmailTemporaryError(Exception):
    pass


class EmailError(Exception):
    pass
