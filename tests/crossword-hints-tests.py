"""                                       """
""" http://flask.pocoo.org/docs/0.12/testing/ """
"""                                       """
class XwordhintsTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, crossword_hints.app.config['DATABASE'] = tempfile.mkstemp()
        self.app = crossword_hints.app.test_client()
        #with crossword_hints.app.app_context():
        crossword_hints.init_db()

    def tearDown(self):
        #os.close(self.db_fd)
        os.unlink(crossword_hints.app.config['DATABASE'])

    def loadSampleData(self):
        #with crossword_hints.app.app_context():
            for sql in ('crossword_solutions', 'solution_types', 'crossword_setters', 'setter_types'):
                with crossword_hints.app.open_resource(('tests/%s.sql' % sql), mode='r') as f:
                    crossword_hints.database.execute_sql(f.read())

    def clearSampleData(self):
        crossword_hints.database.execute_sql("DELETE FROM solutions")

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
            rs = crossword_hints.query_db(("SELECT selfCOUNT(id) AS count FROM %s" % table), one=True)
            return rs[0]


    """                   """
    """   T  E  S  T  S   """
    """                   """
    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'There are no profiles saved in the database' in rv.data

    def test_initial_data(self):
        self.loadSampleData()
        nr = crossword_hints.solutions.select().count()
        assert nr == 4
        self.clearSampleData()
        nr = crossword_hints.solutions.select().count()
        assert nr == 0
