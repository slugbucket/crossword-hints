#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crossword hints tests
See http://flask.pocoo.org/docs/0.12/testing/ for reference for this testing
"""
import os
import unittest
import sqlite3

try:
    from StringIO import StringIO
except ModuleNotFoundError:
    from io import StringIO
import datetime
from peewee import *
from flask import current_app
from crossword_hints import application
from crossword_hints.models import crossword_hints as xwordmodel
# from jur_ldap_login.models import users


class MyAnonymousUser:
    """Anonymous user class
    """

    def __init__(self):
        """Class constructor
        """
        self.username = "unittest"

    def is_authenticated(self):
        """User authenticated method
        """
        return True

    def is_active(self):
        """Active user method
        """
        return True

    def is_anonymous(self) -> bool:
        """Anonymous user method
        """
        return False

    def get_id(self) -> int:
        """Return anonymous user id
        """
        return 1

    def get_name(self) -> str:
        """Anonymous username method
        """
        return self.username


class XwordhintsTestCase(unittest.TestCase):
    """
    Tests that involve calls to routes that use the (PeeWee) ORM
    appear to use the development database rather than the one
    for the test.
    To run the tests,
    APP_SETTINGS='test-settings.py' python3 crossword-hints-tests.py
    """

    @classmethod
    def setUpClass(cls):
        """
        initialization logic for the test suite declared in the test module
        code that is executed before all tests in one test run
        """
        application.login_manager.init_app(application)
        xwordmodel.init_db()
        application.login_manager.anonymous_user = MyAnonymousUser

    @classmethod
    def tearDownClass(cls):
        """Class method to remove db config
        """
        try:
            os.close(application.config["DB_FD"])
        except OSError:
            print(f"Error closing database {application.config['DATABASE']}")
        os.unlink(application.config["DATABASE"])

    def setUp(self):
        """Class method to setup test area
        """
        self.app = application.test_client()
        self.numx = application.config["NUM_SOLUTION_ROWS"]
        self.numst = application.config["NUM_SOLUTION_TYPES"]
        self.numcs = application.config["NUM_CROSSWORD_SETTERS"]
        self.numsy = application.config["NUM_SETTER_TYPES"]

    def load_sample_data(self):
        """Class method to load sample data
        """
        with application.app_context():
            for sql in (
                "setter_types",
                "crossword_setters",
                "solution_types",
                "crossword_solutions",
                "users",
            ):
                with current_app.open_resource((f"tests/{sql}.sql"), mode="r") as f:
                    try:
                        xwordmodel.database.execute_sql(f.read())
                    except OSError:
                        print(f"Error executing SQL for {sql}")

    def clear_sample_data(self):
        """Class method to clear sample data
        """
        with application.app_context():
            for tbl in (
                "setter_types",
                "crossword_setters",
                "solution_types",
                "crossword_solutions",
            ):
                try:
                    xwordmodel.database.execute_sql(f"DELETE FROM {tbl}")
                except sqlite3.OperationalError:
                    print(f"clear_ample_data failed for {tbl}")

    def get_request(self, req, follow=True):
        """Class method to follow redirect"""
        with application.app_context():
            rv = self.app.get(req, follow_redirects=follow)
            return rv

    def post_request(self, req, data, follow=True):
        """Class method to post request
        """
        with application.app_context() as xwordhints:
            rv = xwordhints.post(req, follow_redirects=follow, data=data)
            return rv

    def db_count(self, table):
        """
        Class method to count rows in query
        doesn't work when application is using the ORM
        """
        with application.app_context():
            rs = application.query_db(
                (f"SELECT COUNT(rowid) AS count FROM {table}"), one=True
            )
            return rs[0]

    """
          T  E  S  T  S
    """

    def test_0000_empty_db(self):
        """Test empty database"""
        rv = self.app.get("/")
        self.assertIn(
            b"Cryptic cue search", rv.data, "Cannot find front page heading text"
        )

    def test_0001_initial_data(self):
        """Test initial data"""
        self.load_sample_data()
        nr = xwordmodel.crossword_solutions.select().count()
        self.assertEqual(
            nr,
            self.numx,
            f"Unexpected number of solutions, {nr} rather than {self.numsy}",
        )
        self.clear_ample_data()
        nr = xwordmodel.crossword_solutions.select().count()
        self.assertEqual(nr, 0, "Failed to empty database after test sequence")

    """        S E T T E R   T Y P E S         """

    def test_000_count_setter_types(self):
        """ Load sample data """
        self.load_sample_data()
        nr = xwordmodel.setter_types.select().count()
        self.assertEqual(
            nr,
            self.numsy,
            f"Unexpected number of setter types, {nr} rather than {self.numsy}",
        )

    def test_001_list_setter_types(self):
        """ Test list setter """
        rv = self.app.get("/setter-types/")
        self.assertIn(
            b"Good mix of anagrams",
            rv.data,
            "Missing expected text in setter type list",
        )

    def test_002_new_setter_type(self):
        """ add new setter type """
        new_setter_type = {
            "name": "Convoluted",
            "description": "Seriously devious and mindbending clues",
        }
        rv = self.app.post(
            "/setter-types/new", data=new_setter_type, follow_redirects=True
        )
        self.assertIn(
            b"Saved new setter type, ", rv.data, "New setter type save failed"
        )
        nr = xwordmodel.setter_types.select().count()
        self.assertEqual(
            nr,
            self.numsy + 1,
            f"New setter type failed, expected {self.numsy + 1} rather than {nr}",
        )

    def test_003_edit_setter_type(self):
        """ Test update setter type """
        upd_setter_type = {
            "name": "Fiendish",
            "description": "Seriously devious and mindbending clues",
        }
        rv = self.app.post(
            "/setter-types/6/edit", data=upd_setter_type, follow_redirects=True
        )
        self.assertIn(
            b"Updated setter type, Fiendish",
            rv.data,
            f"Edit setter type failed for {upd_setter_type['name']}",
        )

    def test_004_delete_setter_type(self):
        """ Test delete setter type """
        rv = self.app.get("/setter-types/6/delete", follow_redirects=True)
        self.assertIn(
            b"Deleted setter type, Fiendish",
            rv.data,
            "Cannot find deleted setter type message",
        )
        nr = xwordmodel.setter_types.select().count()
        self.assertEqual(
            nr,
            self.numsy,
            f"Delete setter type failed, expected {self.numsy} rather than {nr}",
        )

    def test_099_clear_data(self):
        """ End of test clear data """
        self.clear_ample_data()
        nr = xwordmodel.setter_types.select().count()
        self.assertEqual(nr, 0, "Failed to empty database after test sequence")

    """
            C R O S S W O R D   S E T T E R S
    """

    def test_101_count_crossword_setters(self):
        """ Test count setters """
        self.load_sample_data()
        nr = xwordmodel.crossword_setters.select().count()
        self.assertEqual(
            nr,
            self.numcs,
            f"Unexpected number of setters, {nr} rather than {self.numcs}",
        )

    def test_101_list_crossword_setters(self):
        """ Test list setters """
        rv = self.app.get("/crossword-setters/")
        self.assertIn(
            b"Unrewarding and easily distracted elsewhere",
            rv.data,
            "Cannot find expected text in setters list",
        )

    def test_102_new_crossword_setter(self):
        """ Test add new setter """
        new_x_setter = {
            "name": "Slideshow",
            "setter_type_id": 2,
            "description": "On the sly side",
        }
        rv = self.app.post(
            "/crossword-setters/new", data=new_x_setter, follow_redirects=True
        )
        self.assertIn(
            b"Saved new crossword setter, ",
            rv.data,
            f"New crossword setter failed for {new_x_setter['name']}",
        )
        nr = xwordmodel.crossword_setters.select().count()
        self.assertEqual(
            nr,
            self.numcs + 1,
            f"New crossword setter failed, expected {self.numcs+1}, found {nr}",
        )

    def test_103_edit_crossword_setter(self):
        """ Test edit existing setter """
        csid = (
            xwordmodel.crossword_setters.select(xwordmodel.crossword_setters.rowid)
            .where(xwordmodel.crossword_setters.name == "Slideshow")
            .scalar()
        )
        upd_x_setter = {
            "name": "Slydeshow",
            "setter_type_id": 3,
            "description": "On the sly side",
        }
        rv = self.app.post(
            f"/crossword-setters/{csid}/edit",
            data=upd_x_setter,
            follow_redirects=True,
            timeout=30,
        )
        self.assertIn(
            b"Updated crossword setter, Slydeshow",
            rv.data,
            "crossword setter update failed",
        )

    def test_104_delete_crossword_setter(self):
        """ Test delete setter """
        csid = (
            xwordmodel.crossword_setters.select(xwordmodel.crossword_setters.rowid)
            .where(xwordmodel.crossword_setters.name == "Slydeshow")
            .scalar()
        )
        rv = self.app.get(
        (f"/crossword-setters/{csid}/delete"), follow_redirects=True
        )
        self.assertIn(
            b"Deleted crossword setter, Slydeshow",
            rv.data,
            "Crossword setter deletion failed to display message",
        )
        nr = xwordmodel.crossword_setters.select().count()
        self.assertEqual(
            nr,
            self.numcs,
            f"Crossword setter deletion failed, found {nr} rather than {self.numcs}",
        )

    def test_199_clear_data(self):
        """ End of test clear data """
        self.clear_ample_data()
        nr = xwordmodel.crossword_setters.select().count()
        self.assertEqual(nr, 0, "Failed to empty database after test sequence")

    """
        S O L U T I O N   T Y P E S
    """

    def test_200_count_solution_types(self):
        """ Test count solution types """
        self.load_sample_data()
        nr = xwordmodel.solution_types.select().count()
        self.assertEqual(
            nr,
            self.numst,
            f"Expected {self.numst} solution types, but found {nr}",
        )

    def test_201_list_solution_types(self):
        """ Test list solution types """
        rv = self.app.get("/solution-types/")
        self.assertIn(
            b"Letter rearrangement",
            rv.data,
            "Cannot find expected text in solution type listing",
        )

    def test_202_new_solution_type(self):
        """ Test add new solution type """
        new_solution_type = {
            "name": "Reverse split",
            "description": "Splice reading backwards across two words",
        }
        rv = self.app.post(
            "/solution-types/new", data=new_solution_type, follow_redirects=True
        )
        assert b"Saved new solution type, " in rv.data
        nr = xwordmodel.solution_types.select().count()
        self.assertEqual(
            nr,
            self.numst + 1,
            f"New solution type failed: (expectecd {self.numst + 1}, found {nr})",
        )

    def test_203_edit_solution_type(self):
        """ Test edit solution type """
        stid = (
            xwordmodel.solution_types.select(xwordmodel.solution_types.rowid)
            .where(xwordmodel.solution_types.name == "Reverse split")
            .scalar()
        )
        upd_solution_type = {
            "name": "Reverse splice",
            "description": "Splice reading backwards across two words",
        }
        rv = self.app.post(
            ("/solution-types/%s/edit" % stid),
            data=upd_solution_type,
            follow_redirects=True,
        )
        self.assertIn(
            b"Updated solution type, Reverse splice",
            rv.data,
            "Cannot find updated solution_type",
        )

    def test_204_delete_solution_type(self):
        """
        Test delete solution type
        """
        stid = (
            xwordmodel.solution_types.select(xwordmodel.solution_types.rowid)
            .where(xwordmodel.solution_types.name == "Reverse splice")
            .scalar()
        )
        rv = self.app.get(f"/solution-types/{stid}/delete", follow_redirects=True)
        assert b"Deleted solution type, Reverse splice" in rv.data
        nr = xwordmodel.solution_types.select().count()
        self.assertEqual(
            nr,
            self.numst,
            f"Delete solution type failed: (expected {self.numst}, found {nr}.)",
        )

    def test_299_clear_data(self):
        """
        End of test clear data
        """
        self.clear_ample_data()
        nr = xwordmodel.solution_types.select().count()
        self.assertEqual(nr, 0, "Failed to empty database after test sequence")

    """
        S O L U T I O N S
    """

    def test_300_count_crossword_solutions(self):
        """
        Load sample data
        """
        self.load_sample_data()
        nr = xwordmodel.crossword_solutions.select().count()
        self.assertEqual(
            nr,
            self.numx,
            "AssertionError(300): Expected {self.numx} rows, but found {nr}.",
        )

    def test_301_list_crossword_solutions(self):
        """ List solutions
        """
        rv = self.app.get("/crossword-solutions/")
        self.assertIn(
            b"New crossword solution",
            rv.data,
            "AssertionError(301): Add solution failed: Received data of {rv.data}",
        )

    def test_302_new_crossword_solution(self):
        """ Test new solution
        """
        csid = (
            xwordmodel.crossword_setters.select(xwordmodel.crossword_setters.rowid)
            .where(xwordmodel.crossword_setters.name == "Hypnos")
            .scalar()
        )
        stid = (
            xwordmodel.solution_types.select(xwordmodel.solution_types.rowid)
            .where(xwordmodel.solution_types.name == "Double meaning")
            .scalar()
        )
        new_solution = {
            "crossword_setter_id": csid,
            "clue": "One son comes down for Christmas and Easter, perhaps",
            "solution": "Islands",
            "solution_hint": "1 Son = I-S; comes down = LANDS; Christmas and Easter are ISLANDS",
            "solution_type_id": stid,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
        }
        rv = self.app.post(
            "/crossword-solutions/new", data=new_solution, follow_redirects=True
        )
        self.assertIn(b"Saved new crossword solution, ", rv.data)
        nr = xwordmodel.crossword_solutions.select().count()
        self.assertEqual(
            nr,
            self.numx + 1,
            f"New solution failed (expected {self.numx}, found {nr})",
        )

    def test_303_edit_crossword_solution(self):
        """ Test edit solution
        """
        csid = (
            xwordmodel.crossword_setters.select(xwordmodel.crossword_setters.rowid)
            .where(xwordmodel.crossword_setters.name == "Klingsor")
            .scalar()
        )
        stid = (
            xwordmodel.crossword_solutions.select(
                xwordmodel.crossword_solutions.solution_type_id
            )
            .where(xwordmodel.crossword_solutions.solution == "Islands")
            .scalar()
        )
        upd_solution = {
            "crossword_setter_id": csid,
            "clue": "One son comes down for Christmas and Easter, perhaps",
            "solution": "islands",
            "solution_hint": "One Son = I-S; comes down = LANDS; Christmas and Easter are ISLANDS",
            "solution_type_id": stid,
            "updated_at": datetime.datetime.now(),
        }
        rv = self.app.post(
            ("/crossword-solutions/{csid}/edit"),
            data=upd_solution,
            follow_redirects=True,
        )
        self.assertIn(
            b"Updated crossword solution, islands",
            rv.data,
            f"Crossword solution update failed for {upd_solution['solution']}",
        )

    def test_304_show_crosword_solution(self):
        """ Test show solution
        """
        soln = xwordmodel.crossword_solutions.get(
            xwordmodel.crossword_solutions.solution == "islands"
        )
        rv = self.app.get("/crossword-solutions/{soln}")
        self.assertIn(
            b"One son comes down for Christmas and Easter, perhaps",
            rv.data,
            "Cannot find updated solution on listing",
        )

    def test_305_delete_crossword_solution(self):
        """ Test delete solution
        """
        csid = xwordmodel.crossword_solutions.get(
            xwordmodel.crossword_solutions.solution == "islands"
        )
        rv = self.app.get(f"/crossword-solutions/{csid}/delete", follow_redirects=True)
        self.assertIn(
            b"Deleted crossword solution, islands", rv.data, "Solution deletion failed"
        )
        nr = xwordmodel.crossword_solutions.select().count()
        self.assertEqual(
            nr,
            self.numx,
            f"Solution deletion failed (expected {self.numx}, found {nr})",
        )

    def test_399_clear_data(self):
        """ End of test clear data
        """
        self.clear_ample_data()
        nr = xwordmodel.crossword_solutions.select().count()
        self.assertEqual(nr, 0, "Failed to empty database after test sequence")

    """
        Pagination tests
    """

    def test_400_solution_pagination(self):
        """ Load sample data
        """
        self.load_sample_data()
        rv = self.app.get("/crossword-solutions/", follow_redirects=True)
        self.assertIn(
            b'<span class="pagination nolink">&laquo; Prev</span>',
            rv.data,
            "Cannot find greyed out prev box",
        )
        self.assertIn(
            b'<a href="/crossword-solutions/page/2?q=">Next &raquo;</a>',
            rv.data,
            "Cannot find next link",
        )

    def test_401_get_next_page(self):
        """ Test pagination next page
        """
        rv = self.app.get("/crossword-solutions/page/2?q=", follow_redirects=True)
        self.assertIn(
            b"ALLEGRETTO",
            rv.data,
            "Cannot find expected solution (ALLEGRETTO) on second page",
        )

    def test_402_get_last_page(self):
        """ Test pagination last page
        """
        rv = self.app.get("/crossword-solutions/page/31?q=", follow_redirects=True)
        self.assertIn(
            b"ZEAL", rv.data, "Cannot find expected solution (ZEAL) on last page"
        )
        self.assertIn(
            b'<span class="pagination nolink">Next &raquo;</span>',
            rv.data,
            "Cannot find greyed out next box",
        )
        self.assertIn(
            b'<a href="/crossword-solutions/page/30?q=">&laquo; Prev</a>',
            rv.data,
            "Cannot find prev link",
        )

    def test_403_more_items_per_page(self):
        """ Test pagination more items
        """
        oldpp = application.config["PER_PAGE"]
        application.config["PER_PAGE"] = 60
        rv = self.app.get("/crossword-solutions/", follow_redirects=True)
        self.assertIn(
            b'<a href="/crossword-solutions/page/13?q=">13</a>',
            rv.data,
            "Cannot find link to last page",
        )
        rv = self.app.get("/crossword-solutions/page/13", follow_redirects=True)
        self.assertIn(
            b'<span class="pagination nolink">Next &raquo;</span>',
            rv.data,
            "Cannot find greyed out next box",
        )
        application.config["PER_PAGE"] = oldpp

    def test_499_clear_data(self):
        """ End of test clear data
        """
        self.clear_ample_data()
        nr = xwordmodel.crossword_solutions.select().count()
        self.assertEqual(nr, 0, "Failed to empty database after test sequence")

    """ Search tests
    """

    def test_500_search_solution(self):
        """ Load sample data
        """
        self.load_sample_data()
        word = {"search_box": "CINEMA"}
        rv = self.app.post(
            "/crossword-solutions/search", data=word, follow_redirects=True
        )
        self.assertIn(
            b"At home in church with mother where Rebecca and Arthur might be seen",
            rv.data,
            f"Clue solution search failed for {word['search_box']}.",
        )

    def test_501_search_many_solutions(self):
        """ Test search many solutions
        """
        word = {"search_box": "AGE"}
        rv = self.app.post(
            "/crossword-solutions/search", data=word, follow_redirects=True
        )
        for res in [
            b"AGENCIES",
            b"AGENT",
            b"BARRAGE",
            b"MIDDLE-AGE SPREAD",
            b"SHRINKAGE",
            b"STAGE WIN",
            b"UPSTAGED",
        ]:
            self.assertIn(
                res,
                rv.data,
                f"Cannot find expected solution {str(res)} in search results",
            )
        self.assertIn(
            b'<span class="pagination nolink">Next &raquo;</span>',
            rv.data,
            "Cannot find greyed out next box",
        )
        self.assertIn(
            b'<span class="pagination nolink">&laquo; Prev</span>',
            rv.data,
            "Cannot find greyed out prev box",
        )

    def test_502_search_solution_pages(self):
        """ Test search solution pages
        """
        word = {"search_box": "dac"}
        rv = self.app.post(
            "/crossword-solutions/search", data=word, follow_redirects=True
        )
        for res in [b"AIGRETTE", b"ALAN SHEARER", b"INVENTOR", b"JACKS"]:
            self.assertIn(
                res,
                rv.data,
                f"Cannot find expected solution {str(res)} in search results",
            )
        self.assertIn(
            b'<span class="pagination nolink">&laquo; Prev</span>',
            rv.data,
            "Cannot find greyed out prev box",
        )
        self.assertIn(
            (
                b'<a href="/crossword-solutions/page/2?q=%s">Next &raquo;</a>'
                % str.encode(word["search_box"])
            ),
            rv.data,
            "Cannot find next link",
        )
        rv = self.app.get(
            ("/crossword-solutions/page/2?q=%s" % word["search_box"]),
            follow_redirects=True,
        )
        for res in [b"JOSEPH", b"LAWSON", b"STERNE", b"SUPERVISION"]:
            self.assertIn(
                res,
                rv.data,
                "Cannot find expected solution %s in search results" % str(res),
            )
        self.assertIn(
            (
                b'<a href="/crossword-solutions/page/3?q=%s">Next &raquo;</a>'
                % str.encode(word["search_box"])
            ),
            rv.data,
            "Cannot find prev link",
        )
        self.assertIn(
            (
                b'<a href="/crossword-solutions/?q=%s">&laquo; Prev</a>'
                % str.encode(word["search_box"])
            ),
            rv.data,
            "Cannot find next link",
        )

    def test_599_clear_data(self):
        """ End of test clear data
        """
        self.clear_ample_data()
        nr = xwordmodel.crossword_solutions.select().count()
        self.assertEqual(nr, 0, "Failed to empty database after test sequence")


__UNITTEST = True

if __name__ == "__main__":
    unittest.main(exit=True)
