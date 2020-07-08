from typing import NamedTuple
from collections import namedtuple


class ServiceError(Exception):
    def __init__(self, text, details=""):
        self.text = text
        self.details = details
        super().__init__(self.text)

    def __str__(self):
        return f"\n{self.text}:\n{self.details}\n"
