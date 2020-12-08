class ParserError(BaseException):
    def __init__(self, error, token):
        self.error = error
        self.token = token

    def __str__(self):
        return f"{self.error} on token {self.token}"
