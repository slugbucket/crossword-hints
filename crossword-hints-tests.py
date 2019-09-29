import os
import sys
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
"""                                           """
""" http://flask.pocoo.org/docs/0.12/testing/ """
"""                                           """

class MyAnonymousUser():
    def __init__(self):
        self.username = "unittest"

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return(1)

    def get_name(self):
        return(self.username)

"""
Tests that involve calls to routes that use the (PeeWee) ORM
appear to use the development database rather than the one
for the test.
To run the tests,
APP_SETTINGS='test-settings.py' python3 crossword-hints-tests.py
"""
class XwordhintsTestCase(unittest.TestCase):
    def setUp(self):
        crossword_hints.application.login_manager.init_app(crossword_hints.application)
        self.db_fd, crossword_hints.application.config['DATABASE'] = tempfile.mkstemp()
        self.app = crossword_hints.application.test_client()
        crossword_hints.init_db()
        crossword_hints.login_manager.anonymous_user = MyAnonymousUser
        self.numx  = crossword_hints.application.config['NUM_SOLUTION_ROWS']
        self.numst = crossword_hints.application.config['NUM_SOLUTION_TYPES']
        self.numcs = crossword_hints.application.config['NUM_CROSSWORD_SETTERS']
        self.numsy = crossword_hints.application.config['NUM_SETTER_TYPES']

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(crossword_hints.application.config['DATABASE'])

    def loadSampleData(self):
        #with crossword_hints.app.app_context():
        for sql in ('setter_types', 'crossword_setters', 'solution_types', 'crossword_solutions', 'users'):
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
        self.assertIn(b'Cryptic cue search', rv.data, "Cannot find front page heading text")

    def test_0001_initial_data(self):
        self.loadSampleData()
        nr = crossword_hints.crossword_solutions.select().count()
        self.assertEqual(nr, self.numx, "Unexpected number of solutions, %s rather than %s" % (nr, self.numx))
        self.clearSampleData()
        nr = crossword_hints.crossword_solutions.select().count()
        self.assertEqual(nr, 0, "Failed to empty database after test sequence")


    """        S E T T E R   T Y P E S         """

    def test_000_count_setter_types(self):
        self.loadSampleData()
        nr = crossword_hints.setter_types.select().count()
        self.assertEqual(nr, self.numsy, "Unexpected number of setter types, %s rather than %s" % (nr, self.numsy))

    def test_001_list_setter_types(self):
        rv = self.app.get('/setter-types/')
        self.assertIn(b'Good mix of anagrams', rv.data, "Missing expected text in setter type list")

    def test_002_new_setter_type(self):
        new_setter_type = {"name": "Convoluted",
                           "description": "Seriously devious and mindbending clues"}
        rv = self.app.post('/setter-types/new', data=new_setter_type, follow_redirects=True)
        self.assertIn(b'Saved new setter type, ',  rv.data, "New setter type save failed")
        nr = crossword_hints.setter_types.select().count()
        self.assertEqual(nr, self.numsy+1, "New setter type failed, expected %s rather than %s" % (self.numsy+1, nr))

    def test_003_edit_setter_type(self):
        upd_setter_type = {"name": "Fiendish",
                           "description": "Seriously devious and mindbending clues"}
        rv = self.app.post('/setter-types/6/edit', data=upd_setter_type, follow_redirects=True)
        self.assertIn(b'Updated setter type, Fiendish', rv.data, "Edit setter type failed for %s" % upd_setter_type['name'])

    def test_004_delete_setter_type(self):
        rv = self.app.get('/setter-types/6/delete', follow_redirects=True)
        self.assertIn(b'Deleted setter type, Fiendish', rv.data, "Cannot find deleted setter type message")
        nr = crossword_hints.setter_types.select().count()
        self.assertEqual( nr, self.numsy, "Delete setter type failed, expected %s rather than %s" % (self.numsy, nr))

    def test_099_clear_data(self):
        self.clearSampleData()
        nr = crossword_hints.setter_types.select().count()
        self.assertEqual(nr, 0, "Failed to empty database after test sequence")

    """    C R O S S W O R D   S E T T E R S   """
    def test_101_count_crossword_setters(self):
        self.loadSampleData()
        nr = crossword_hints.crossword_setters.select().count()
        self.assertEqual(nr, self.numcs, "Unexpected number of setters, %s rather than %s" % (nr, self.numcs))

    def test_101_list_crossword_setters(self):
        rv = self.app.get('/crossword-setters/')
        self.assertIn( b'Unrewarding and easily distracted elsewhere', rv.data, "Cannot find expected text in setters list")

    def test_102_new_crossword_setter(self):
        new_x_setter = {"name": "Slideshow",
                        "setter_type_id": 2,
                        "description": "On the sly side"}
        rv = self.app.post('/crossword-setters/new', data=new_x_setter, follow_redirects=True)
        self.assertIn(b'Saved new crossword setter, ',  rv.data, "New crossword setter failed for %s" % new_x_setter['name'])
        nr = crossword_hints.crossword_setters.select().count()
        self.assertEqual(nr, self.numcs+1, "New crossword setter failed, expected %s, found %s" % (self.numcs+1, nr))

    def test_103_edit_crossword_setter(self):
        csid = crossword_hints.crossword_setters.select(crossword_hints.crossword_setters.rowid).where(crossword_hints.crossword_setters.name == "Slideshow").scalar()
        upd_x_setter = {"name": "Slydeshow",
                        "setter_type_id": 3,
                        "description": "On the sly side"}
        rv = self.app.post(('/crossword-setters/%s/edit' % csid), data=upd_x_setter, follow_redirects=True)
        self.assertIn(b'Updated crossword setter, Slydeshow', rv.data, "crossword setter update failed")

    def test_104_delete_crossword_setter(self):
        csid = crossword_hints.crossword_setters.select(crossword_hints.crossword_setters.rowid).where(crossword_hints.crossword_setters.name == "Slydeshow").scalar()
        rv = self.app.get(('/crossword-setters/%s/delete' % csid), follow_redirects=True)
        self.assertIn(b'Deleted crossword setter, Slydeshow', rv.data, "Crossword setter deletion failed to display message")
        nr = crossword_hints.crossword_setters.select().count()
        self.assertEqual(nr, self.numcs, "Crossword setter deletion failed, found %s rather than %s" % (nr, self.numcs))

    def test_199_clear_data(self):
        self.clearSampleData()
        nr = crossword_hints.crossword_setters.select().count()
        self.assertEqual(nr, 0, "Failed to empty database after test sequence")


    """        S O L U T I O N   T Y P E S     """
    def test_200_count_solution_types(self):
        self.loadSampleData()
        nr = crossword_hints.solution_types.select().count()
        self.assertEqual(nr, self.numst, "Expected %s solution types, but found %s" % (self.numst, nr))

    def test_201_list_solution_types(self):
        rv = self.app.get('/solution-types/')
        self.assertIn(b'Letter rearrangement', rv.data, "Cannot find expected text in solution type listing")

    def test_202_new_solution_type(self):
        new_solution_type = {"name": "Reverse split",
                           "description": "Splice reading backwards across two words"}
        rv = self.app.post('/solution-types/new', data=new_solution_type, follow_redirects=True)
        assert b'Saved new solution type, ' in rv.data
        nr = crossword_hints.solution_types.select().count()
        self.assertEqual(nr, self.numst+1, "New solution type failed: (expectecd %s, found %s)" % (self.numst+1, nr))

    def test_203_edit_solution_type(self):
        stid = crossword_hints.solution_types.select(crossword_hints.solution_types.rowid).where(crossword_hints.solution_types.name == "Reverse split").scalar()
        upd_solution_type = {"name": "Reverse splice",
                           "description": "Splice reading backwards across two words"}
        rv = self.app.post(('/solution-types/%s/edit' % stid), data=upd_solution_type, follow_redirects=True)
        self.assertIn(b'Updated solution type, Reverse splice', rv.data, "Cannot find updated solution_type")

    def test_204_delete_solution_type(self):
        stid = crossword_hints.solution_types.select(crossword_hints.solution_types.rowid).where(crossword_hints.solution_types.name == "Reverse splice").scalar()
        rv = self.app.get(('/solution-types/%s/delete' % stid), follow_redirects=True)
        assert b'Deleted solution type, Reverse splice' in rv.data
        nr = crossword_hints.solution_types.select().count()
        self.assertEqual(nr, self.numst, "Delete solution type failed: (expected %s, found %s.)" % (self.numst, nr))

    def test_299_clear_data(self):
        self.clearSampleData()
        nr = crossword_hints.solution_types.select().count()
        self.assertEqual(nr, 0, "Failed to empty database after test sequence")

    """             S O L U T I O N S          """
    def test_300_count_crossword_solutions(self):
        self.loadSampleData()
        nr = crossword_hints.crossword_solutions.select().count()
        self.assertEqual(nr, self.numx, "AssertionError(300): Expected %s rows, but found %s." % (self.numx, nr))

    def test_301_list_crossword_solutions(self):
        rv = self.app.get('/crossword-solutions/')
        self.assertIn(b'New crossword solution', rv.data, "AssertionError(301): Add solution failed: Received data of %s" % rv.data)

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
        self.assertIn(b'Saved new crossword solution, ', rv.data)
        nr = crossword_hints.crossword_solutions.select().count()
        self.assertEqual(nr, self.numx+1, "New solution failed (expected %s, found %s)" % (self.numx, nr))

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
        self.assertIn(b'Updated crossword solution, islands', rv.data, "Crossword solution update failed for %s" % upd_solution['solution'])

    def test_304_show_crosword_solution(self):
        soln = crossword_hints.crossword_solutions.get(crossword_hints.crossword_solutions.solution == "islands")
        rv = self.app.get('/crossword-solutions/%s' % soln)
        self.assertIn(b'One son comes down for Christmas and Easter, perhaps', rv.data, "Cannot find updated solution on listing")

    def test_305_delete_crossword_solution(self):
        csid = crossword_hints.crossword_solutions.get(crossword_hints.crossword_solutions.solution == "islands")
        rv = self.app.get(('/crossword-solutions/%s/delete' % csid), follow_redirects=True)
        self.assertIn(b'Deleted crossword solution, islands', rv.data, "Solution deletion failed")
        nr = crossword_hints.crossword_solutions.select().count()
        self.assertEqual(nr, self.numx, "Solution deletion failed (expected %s, found %s)" % (self.numx, nr))

    def test_399_clear_data(self):
        self.clearSampleData()
        nr = crossword_hints.crossword_solutions.select().count()
        self.assertEqual(nr, 0, "Failed to empty database after test sequence")

    """ Pagination tests
    """
    def test_400_solution_pagination(self):
        self.loadSampleData()
        rv = self.app.get('/crossword-solutions/', follow_redirects=True)
        self.assertIn(b'<span class="pagination nolink">&laquo; Prev</span>', rv.data, "Cannot find greyed out prev box")
        self.assertIn(b'<a href="/crossword-solutions/page/2?q=">Next &raquo;</a>', rv.data, "Cannot find next link")

    def test_401_get_next_page(self):
        rv = self.app.get('/crossword-solutions/page/2?q=', follow_redirects=True)
        self.assertIn(b'ALLEGRETTO', rv.data, "Cannot find expected solution (ALLEGRETTO) on second page")

    def test_402_get_last_page(self):
        rv = self.app.get('/crossword-solutions/page/31?q=', follow_redirects=True)
        self.assertIn(b'ZEAL', rv.data, "Cannot find expected solution (ZEAL) on last page")
        self.assertIn(b'<span class="pagination nolink">Next &raquo;</span>', rv.data, "Cannot find greyed out next box")
        self.assertIn(b'<a href="/crossword-solutions/page/30?q=">&laquo; Prev</a>', rv.data, "Cannot find prev link")

    def test_403_more_items_per_page(self):
        oldpp = crossword_hints.application.config['PER_PAGE']
        crossword_hints.application.config['PER_PAGE'] = 60
        rv = self.app.get('/crossword-solutions/', follow_redirects=True)
        self.assertIn(b'<a href="/crossword-solutions/page/13?q=">13</a>', rv.data, "Cannot find link to last page")
        rv = self.app.get('/crossword-solutions/page/13', follow_redirects=True)
        self.assertIn(b'<span class="pagination nolink">Next &raquo;</span>', rv.data, "Cannot find greyed out next box")
        crossword_hints.application.config['PER_PAGE'] = oldpp

    def test_499_clear_data(self):
        self.clearSampleData()
        nr = crossword_hints.crossword_solutions.select().count()
        self.assertEqual(nr, 0, "Failed to empty database after test sequence")

    """ Search tests
    """
    def test_500_search_solution(self):
        self.loadSampleData()
        word = {"search_box": "CINEMA"}
        rv = self.app.post('/crossword-solutions/search', data=word, follow_redirects=True)
        self.assertIn(b'At home in church with mother where Rebecca and Arthur might be seen', rv.data, "Clue solution search failed for %s." % word['search_box'])

    def test_501_search_many_solutions(self):
        word = {"search_box": "AGE"}
        rv = self.app.post('/crossword-solutions/search', data=word, follow_redirects=True)
        for res in [b'AGENCIES', b'AGENT', b'BARRAGE', b'MIDDLE-AGE SPREAD', b'SHRINKAGE', b'STAGE WIN', b'UPSTAGED']:
            self.assertIn(res, rv.data, "Cannot find expected solution %s in search results" % str(res))
        self.assertIn(b'<span class="pagination nolink">Next &raquo;</span>', rv.data, "Cannot find greyed out next box")
        self.assertIn(b'<span class="pagination nolink">&laquo; Prev</span>', rv.data, "Cannot find greyed out prev box")

    def test_502_search_solution_pages(self):
        word = {"search_box": "dac"}
        rv = self.app.post('/crossword-solutions/search', data=word, follow_redirects=True)
        for res in [b'AIGRETTE', b'ALAN SHEARER', b'INVENTOR', b'JACKS']:
            self.assertIn(res, rv.data, "Cannot find expected solution %s in search results" % str(res))
        self.assertIn(b'<span class="pagination nolink">&laquo; Prev</span>', rv.data, "Cannot find greyed out prev box")
        self.assertIn((b'<a href="/crossword-solutions/page/2?q=%s">Next &raquo;</a>' % str.encode(word['search_box'])), rv.data, "Cannot find next link")
        rv = self.app.get(('/crossword-solutions/page/2?q=%s' % word['search_box']), follow_redirects=True)
        for res in [b'JOSEPH', b'LAWSON', b'STERNE', b'SUPERVISION']:
            self.assertIn(res, rv.data, "Cannot find expected solution %s in search results" % str(res))
        self.assertIn((b'<a href="/crossword-solutions/page/3?q=%s">Next &raquo;</a>' % str.encode(word['search_box'])), rv.data, "Cannot find prev link")
        self.assertIn((b'<a href="/crossword-solutions/?q=%s">&laquo; Prev</a>' % str.encode(word['search_box'])), rv.data, "Cannot find next link")

    def test_599_clear_data(self):
        self.clearSampleData()
        nr = crossword_hints.crossword_solutions.select().count()
        self.assertEqual(nr, 0, "Failed to empty database after test sequence")

__unittest = True

if __name__ == '__main__':
    unittest.main(exit=True)

os.unlink(crossword_hints.application.config['DATABASE'])