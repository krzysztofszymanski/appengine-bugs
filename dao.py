from models import *


class Dao(object):
    """
    Dao singleton
    """
    _instance = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(
                Dao, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def add_comment(self, issue, comment):
        pass
