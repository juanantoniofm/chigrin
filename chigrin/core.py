class ChigrinError(Exception):
    """Base class for all errors raised in chigrin."""

    def __init__(self, message, cause=None):
        super(ChigrinError, self).__init__((message, cause))
