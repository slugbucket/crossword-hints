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
        self.db_fd, crossword_hints.application.config['DATABASE'] = tempfile.mkstemp()
        self.app = crossword_hints.application.test_client()
        crossword_hints.init_db()

    def tearDown(self):
        #os.close(self.db_fd)
        os.unlink(crossword_hints.application.config['DATABASE'])

    def loadSampleData(self):
        #with crossword_hints.app.app_context():
        for sql in ('setter_types', 'crossword_setters', 'solution_types', 'crossword_solutions'):
            with crossword_hints.application.open_resource(('tests/%s.sql' % sql), mode='r') as f:
                crossword_hints.database.execute_sql(f.read())

    def clearSampleData(self):
        for tbl in ('crossword_solutions', 'solution_types', 'crossword_setters', 'setter_types' ):
            crossword_hints.database.execute_sql("DELETE FROM %s" % tbl)

    def get_request(self, req, follow):
        with crossword_hints.application.app_context():
            rv = self.app.get(req, follow_redirects=True)
            return rv

    def post_request(self, req, data, follow):
        with crossword_hints.application.app_context():
            rv = crossword_hints.app.post('/crossword_hints/1/copy', follow_redirects=True)
            return rv

    # Doesn't work when application is using the ORM
    def db_count(self, table):
        with crossword_hints.application.app_context():
            rs = crossword_hints.query_db(("SELECT COUNT(rowid) AS count FROM %s" % table), one=True)
            return rs[0]


    """                   """
    """   T  E  S  T  S   """
    """                   """
    def test_0000_empty_db(self):
        rv = self.app.get('/')
        assert b'Cryptic cue search' in rv.data

    def test_0001_initial_data(self):
        self.loadSampleData()
        nr = crossword_hints.crossword_solutions.select().count()
        assert nr == 760
        self.clearSampleData()
        nr = crossword_hints.crossword_solutions.select().count()
        assert nr == 0


    """        S E T T E R   T Y P E S         """

    def test_000_count_setter_types(self):
        self.loadSampleData()
        nr = crossword_hints.setter_types.select().count()
        assert nr == 5

    def test_001_list_setter_types(self):
        rv = self.app.get('/setter-types/')
        assert b'Good mix of anagrams' in rv.data

    def test_002_new_setter_type(self):
        new_setter_type = {"name": "Convoluted",
                           "description": "Seriously devious and mindbending clues"}
        rv = self.app.post('/setter-types/new', data=new_setter_type, follow_redirects=True)
        assert b'Saved new setter type, ' in rv.data
        nr = crossword_hints.setter_types.select().count()
        assert nr == 6

    def test_003_edit_setter_type(self):
        upd_setter_type = {"name": "Fiendish",
                           "description": "Seriously devious and mindbending clues"}
        rv = self.app.post('/setter-types/6/edit', data=upd_setter_type, follow_redirects=True)
        assert b'Updated setter type, Fiendish' in rv.data

    def test_004_delete_setter_type(self):
        rv = self.app.get('/setter-types/6/delete', follow_redirects=True)
        assert b'Deleted setter type, Fiendish' in rv.data

    def test_099_clear_data(self):
        self.clearSampleData()
        nr = crossword_hints.setter_types.select().count()
        assert nr == 0

    """    C R O S S W O R D   S E T T E R S   """
    def test_101_count_crossword_setters(self):
        self.loadSampleData()
        nr = crossword_hints.crossword_setters.select().count()
        assert nr == 19

    def test_101_list_crossword_setters(self):
        rv = self.app.get('/crossword-setters/')
        assert b'Unrewarding and easily distracted elsewhere' in rv.data

    def test_102_new_crossword_setter(self):
        new_x_setter = {"name": "Slideshow",
                        "setter_type_id": 2,
                        "description": "On the sly side"}
        rv = self.app.post('/crossword-setters/new', data=new_x_setter, follow_redirects=True)
        assert b'Saved new crossword setter, ' in rv.data
        nr = crossword_hints.crossword_setters.select().count()
        assert nr == 20

    def test_103_edit_crossword_setter(self):
        csid = crossword_hints.crossword_setters.select(crossword_hints.crossword_setters.rowid).where(crossword_hints.crossword_setters.name == "Slideshow").scalar()
        upd_x_setter = {"name": "Slydeshow",
                        "setter_type_id": 3,
                        "description": "On the sly side"}
        rv = self.app.post(('/crossword-setters/%s/edit' % csid), data=upd_x_setter, follow_redirects=True)
        assert b'Updated crossword setter, Slydeshow' in rv.data

    def test_104_delete_crossword_setter(self):
        csid = crossword_hints.crossword_setters.select(crossword_hints.crossword_setters.rowid).where(crossword_hints.crossword_setters.name == "Slydeshow").scalar()
        rv = self.app.get(('/crossword-setters/%s/delete' % csid), follow_redirects=True)
        assert b'Deleted crossword setter, Slydeshow' in rv.data
        nr = crossword_hints.crossword_setters.select().count()
        assert nr == 19

    def test_199_clear_data(self):
        self.clearSampleData()
        nr = crossword_hints.crossword_setters.select().count()
        assert nr == 0


    """        S O L U T I O N   T Y P E S     """
    def test_200_count_solution_types(self):
        self.loadSampleData()
        nr = crossword_hints.solution_types.select().count()
        assert nr == 10

    def test_201_list_solution_types(self):
        rv = self.app.get('/solution-types/')
        assert b'Letter rearrangement' in rv.data

    def test_202_new_solution_type(self):
        new_solution_type = {"name": "Reverse split",
                           "description": "Splice reading backwards across two words"}
        rv = self.app.post('/solution-types/new', data=new_solution_type, follow_redirects=True)
        assert b'Saved new solution type, ' in rv.data
        nr = crossword_hints.solution_types.select().count()
        assert nr == 11

    def test_203_edit_solution_type(self):
        stid = crossword_hints.solution_types.select(crossword_hints.solution_types.rowid).where(crossword_hints.solution_types.name == "Reverse split").scalar()
        upd_solution_type = {"name": "Reverse splice",
                           "description": "Splice reading backwards across two words"}
        rv = self.app.post(('/solution-types/%s/edit' % stid), data=upd_solution_type, follow_redirects=True)
        assert b'Updated solution type, Reverse splice' in rv.data

    def test_204_delete_solution_type(self):
        stid = crossword_hints.solution_types.select(crossword_hints.solution_types.rowid).where(crossword_hints.solution_types.name == "Reverse splice").scalar()
        rv = self.app.get(('/solution-types/%s/delete' % stid), follow_redirects=True)
        assert b'Deleted solution type, Reverse splice' in rv.data
        nr = crossword_hints.solution_types.select().count()
        assert nr == 10

    def test_299_clear_data(self):
        self.clearSampleData()
        nr = crossword_hints.solution_types.select().count()
        assert nr == 0

    """             S O L U T I O N S          """
    def test_300_count_crossword_solutions(self):
        self.loadSampleData()
        nr = crossword_hints.crossword_solutions.select().count()
        assert nr == 760

    def test_301_list_crossword_solutions(self):
        rv = self.app.get('/crossword-solutions/')
        assert b'Add new crossword solution' in rv.data

    def test_302_new_crossword_solution(self):
        csid = crossword_hints.crossword_setters.select(crossword_hints.crossword_setters.rowid).where(crossword_hints.crossword_setters.name == "Hypnos").scalar()
        stid = crossword_hints.solution_types.select(crossword_hints.solution_types.rowid).where(crossword_hints.solution_types.name == "Double meaning").scalar()
        new_solution = {"crossword_setter_id": csid,
                        "clue": "One son comes down for Christmas and Easter, perhaps",
                        "solution": "Islands",
                        "solution_hint": "1 Son = I-S; comes down = LANDS; Christmas and Easter are ISLANDS",
                        "solution_type_id": stid,
                        "created_at": datetime.datetime.now(),
                        "updated_at": datetime.datetime.now()}
        rv = self.app.post('/crossword-solutions/new', data=new_solution, follow_redirects=True)
        assert b'Saved new crossword solution, ' in rv.data
        nr = crossword_hints.crossword_solutions.select().count()
        assert nr == 761

    def test_303_edit_crossword_solution(self):
        csid = crossword_hints.crossword_setters.select(crossword_hints.crossword_setters.rowid).where(crossword_hints.crossword_setters.name == "Klingsor").scalar()
        stid = crossword_hints.crossword_solutions.select(crossword_hints.crossword_solutions.solution_type_id).where(crossword_hints.crossword_solutions.solution == "Islands").scalar()
        upd_solution = {"crossword_setter_id": csid,
                        "clue": "One son comes down for Christmas and Easter, perhaps",
                        "solution": "islands",
                        "solution_hint": "One Son = I-S; comes down = LANDS; Christmas and Easter are ISLANDS",
                        "solution_type_id": stid,
                        "updated_at": datetime.datetime.now()}
        rv = self.app.post(('/crossword-solutions/%s/edit' % csid), data=upd_solution, follow_redirects=True)
        assert b'Updated crossword solution, islands' in rv.data

    def test_304_show_crosword_solution(self):
        soln = crossword_hints.crossword_solutions.get(crossword_hints.crossword_solutions.solution == "islands")
        rv = self.app.get('/crossword-solutions/%s' % soln)
        assert b'One son comes down for Christmas and Easter, perhaps' in rv.data

    def test_305_delete_crossword_solution(self):
        csid = crossword_hints.crossword_solutions.get(crossword_hints.crossword_solutions.solution == "islands")
        rv = self.app.get(('/crossword-solutions/%s/delete' % csid), follow_redirects=True)
        assert b'Deleted crossword solution, islands' in rv.data
        nr = crossword_hints.crossword_solutions.select().count()
        assert nr == 151

    """ Pagination tests
    """

    """ Search tests
    """
    def test_306_search_solution(self):
        word = {"search_box": "CINEMA"}
        rv = self.app.post(('/crossword-solutions/'), data=word, follow_redirects=True)
        assert b'At home in church with mother where Rebecca and Arthur might be seen' in rv.data

    def test_399_clear_data(self):
        self.clearSampleData()
        nr = crossword_hints.crossword_solutions.select().count()
        assert nr == 0


if __name__ == '__main__':
    unittest.main(exit=True)
