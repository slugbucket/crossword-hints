import os
import unittest
import tempfile
import sqlite3
import json
import io
try:
    from StringIO import StringIO
except ModuleNotFoundError:
    from io import StringIO
import re
import zipfile
import socket
from peewee import *
from flask import Flask, request, flash, redirect, render_template, g, jsonify, Response, send_file
import datetime
import crossword_hints
"""                                       """
""" http://flask.pocoo.org/docs/0.12/testing/ """
"""                                       """
"""
Tests that involve calls to routes that use the (PeeWee) ORM
appear to use the development database rather than the one
for the test.
To run the tests,
APP_SETTINGS='test-settings.py' python crossword-hints-test.py
"""
class XwordhintsTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, crossword_hints.app.config['DATABASE'] = tempfile.mkstemp()
        self.app = crossword_hints.app.test_client()
        crossword_hints.init_db()

    def tearDown(self):
        #os.close(self.db_fd)
        os.unlink(crossword_hints.app.config['DATABASE'])

    def loadSampleData(self):
        #with crossword_hints.app.app_context():
        for sql in ('setter_types', 'crossword_setters', 'solution_types', 'crossword_solutions'):
            with crossword_hints.app.open_resource(('tests/%s.sql' % sql), mode='r') as f:
                crossword_hints.database.execute_sql(f.read())

    def clearSampleData(self):
        crossword_hints.database.execute_sql("DELETE FROM crossword_solutions")

    def get_request(self, req, follow):
        with crossword_hints.app.app_context():
            rv = self.app.get(req, follow_redirects=True)
            return rv

    def post_request(self, req, data, follow):
        with crossword_hints.app.app_context():
            rv = crossword_hints.app.post('/crossword_hints/1/copy', follow_redirects=True)
            return rv

    # Doesn't work when application is using the ORM
    def db_count(self, table):
        with crossword_hints.app.app_context():
            rs = crossword_hints.query_db(("SELECT COUNT(rowid) AS count FROM %s" % table), one=True)
            return rs[0]


    """                   """
    """   T  E  S  T  S   """
    """                   """
    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'Cryptic cue search' in rv.data

    def test_initial_data(self):
        print("DEBUG: test_initial_data")
        self.loadSampleData()
        nr = crossword_hints.crossword_solutions.select().count()
        assert nr == 151
        self.clearSampleData()
        nr = crossword_hints.crossword_solutions.select().count()
        assert nr == 0

if __name__ == '__main__':
    unittest.main(exit=True)
