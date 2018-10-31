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
APP_SETTINGS='test-settings.py' python crossword-hints-tests.py
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
        for tbl in ('crossword_solutions', 'solution_types', 'crossword_setters', 'setter_types' ):
            crossword_hints.database.execute_sql("DELETE FROM %s" % tbl)

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
    def test_0000_empty_db(self):
        rv = self.app.get('/')
        assert b'Cryptic cue search' in rv.data

    def test_0001_initial_data(self):
        print("DEBUG: test_initial_data")
        self.loadSampleData()
        nr = crossword_hints.crossword_solutions.select().count()
        assert nr == 151
        self.clearSampleData()
        nr = crossword_hints.crossword_solutions.select().count()
        assert nr == 0


    """        S E T T E R   T Y P E S         """

    def test_000_count_setter_types(self):
        print("DEBUG: Test full and empty setter types")
        self.loadSampleData()
        nr = crossword_hints.setter_types.select().count()
        print("DEBUG: Found %s rows in the table." % nr)
        assert nr == 5

    def test_001_list_setter_types(self):
        print("DEBUG: List the index page")
        rv = self.app.get('/setter-types/')
        #print("DEBUG: index data contains %s" % rv.data)
        assert b'Good mix of anagrams' in rv.data

    def test_002_new_setter_type(self):
        print("DEBUG: Submit a new setter type.")
        new_setter_type = {"name": "Convoluted",
                           "description": "Seriously devious and mindbending clues"}
        rv = self.app.post('/setter-types/new', data=new_setter_type, follow_redirects=True)
        assert b'Saved new setter type, ' in rv.data
        nr = crossword_hints.setter_types.select().count()
        assert nr == 6

    def test_003_edit_setter_type(self):
        print("DEBUG: Update a setter type.")
        upd_setter_type = {"name": "Fiendish",
                           "description": "Seriously devious and mindbending clues"}
        rv = self.app.post('/setter-types/6/edit', data=upd_setter_type, follow_redirects=True)
        assert b'Updated setter type, Fiendish' in rv.data

    def test_004_delete_setter_type(self):
        print("DEBUG: Update a setter type.")
        rv = self.app.get('/setter-types/6/delete', follow_redirects=True)
        assert b'Deleted setter type, Fiendish' in rv.data

    def test_099_clear_data(self):
        self.clearSampleData()
        nr = crossword_hints.setter_types.select().count()
        assert nr == 0

    """    C R O S S W O R D   S E T T E R S   """
    def test_101_count_crossword_setters(self):
        print("DEBUG: Test full and empty crossword setters")
        self.loadSampleData()
        nr = crossword_hints.crossword_setters.select().count()
        print("DEBUG: Found %s rows in the table." % nr)
        assert nr == 19
        self.clearSampleData()
        nr = crossword_hints.crossword_setters.select().count()
        assert nr == 0

    """        S O L U T I O N   T Y P E S     """
    def test_200_count_solution_types(self):
        print("DEBUG: Test full and empty solution types")
        self.loadSampleData()
        nr = crossword_hints.solution_types.select().count()
        print("DEBUG: Found %s rows in the table." % nr)
        assert nr == 10
        self.clearSampleData()
        nr = crossword_hints.solution_types.select().count()
        assert nr == 0

    """             S O L U T I O N S          """
    def test_300_count_crossword_solutions(self):
        print("DEBUG: Test full and empty crossword solutions")
        self.loadSampleData()
        nr = crossword_hints.crossword_solutions.select().count()
        print("DEBUG: Found %s rows in the table." % nr)
        assert nr == 151
        self.clearSampleData()
        nr = crossword_hints.crossword_solutions.select().count()
        assert nr == 0


if __name__ == '__main__':
    unittest.main(exit=True)
