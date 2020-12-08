class LexerError(BaseException):
    error: str
    line: str

    def __init__(self, error, line):
        self.error = error
        self.line = line

    def __str__(self):
        return f"{self.error} on line {repr(self.line)}"
