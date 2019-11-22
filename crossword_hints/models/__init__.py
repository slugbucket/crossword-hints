# -*- coding: utf-8 -*-
import os
import glob

__all__ = [os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__) + "/*.py")]

from peewee import *
from crossword_hints import application
from crossword_hints import database
"""                                                        """
"""  D  A  T  A  B  A  S  E     M  O  D  E  L  L  I  N  G  """
"""                                                        """
"""                                                        """
"""     A base model that will use our Sqlite database.    """
"""     Appears to be incompatible with Flask TestCase     """
class BaseModel(Model):
    with application.app_context():
        class Meta:
            database = database
"""                                             """
"""  E N D   O F   D A T A B A S E   M O D E L  """
"""                                             """