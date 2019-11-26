# -*- coding: utf-8 -*-
"""                                                        """
"""  I  N  T  E  R  N  A  L    F  U  N  C  T  I  O  N  S   """
"""                                                        """
from flask import request, url_for
from crossword_hints import application
from crossword_hints.models import crossword_hints as xwordmodel
from peewee import *
import re
from datetime import date, timedelta, datetime
# For use with pagination
from math import ceil
# For input (and output) sanitization. Taken from:
# https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python (comment 16)
from html.parser import HTMLParser

class HTMLStripper(HTMLParser):
    convert_charrefs=True
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def handle_entityref(self, name):
        self.fed.append('&%s;' % name)
    def get_data(self):
        return ''.join(self.fed)

"""
Custom template filter to highlight a given word in a piece of text
regardless of case. This can be used instead of the replace filter
which is case-sensitive.

replace(cue_word,"<span class='highlight-cue'>"+cue_word|upper+"</span>")
Params:
  text: string containing word to highlight
  word: string: the word to highlight
  cls: string: the CSS class used for the highlighting
Returns:
  string: HTML in the form: Text before the <span class='cls'>Word</span> to be highlighted
"""
def highlight_text(text, word, cls):
    p = re.compile(word, re.IGNORECASE)
    m = p.search(text)
    if m:
        hstr = ("<span class='%s'>%s</span>" % (cls, m.group()))
        return(p.sub(hstr, text))
    else:
        return(text)

"""
Function to try to determine if a URL (typically passed as a next parameter
when logging in) is safe to redirect to.
Taken from http://flask.pocoo.org/snippets/62/ although the next parameter
is delivered by the query string rather than hidden form element
Params:
  target: string - URL to forward to
Returns:
  bool: True is the target is safe to redirect to, False otherwise
"""
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

"""
Function to try and determine a suitable referral point that is safe
to redirect the client back after an action such as login.
Params:

Returns:
  string: target URL
"""
def get_redirect_target():
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

"""
Function to verify that a submitted forward URL is safe to redirect to or
use a fallback address instead.
Params:
  endpoint: string - name of fallback location if next parameter is not
            found or is not safe
  values: list of values associated with the fallback target
Returns:
  target to redirect to
"""
def redirect_back(endpoint, **values):
    target = request.args['next']
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)

"""
Function to add an activity log record
The format of entries for activity logging are:
* rowid - auto-assigned unique id for the activity record
* actor - name of the user performing the operation
* action - one of login, insert, update, delete or logout,
* item_type -the table on which the operation has been performed.
* item_id - the numeric id of the item under operation
* activity - details of the content that has been changed
"""
def add_log(actor, action, item_type, item_id, activity):
    log = xwordmodel.activity_logs(actor=actor,
                        action=action,
                        item_type=item_type,
                        item_id=item_id,
                        act_action=activity,
                        created_at=datetime.now(),
                        updated_at=datetime.now())
    log.save()

"""
Construct an array containing the setter_type rowid and name
suitable for use in a SELECT form element
"""
def get_setter_types():
    rs=xwordmodel.setter_types.select(xwordmodel.setter_types.rowid, xwordmodel.setter_types.name).order_by(fn.Lower(xwordmodel.setter_types.name))
    s_types = []
    for row in rs.dicts():
        s_types.append([row['rowid'], row['name']])
    return(s_types)

"""
Construct an array containing the crossword setter rowid and name
suitable for use in a SELECT form element
"""
def get_crossword_setters():
    cs=xwordmodel.crossword_setters.select(xwordmodel.crossword_setters.rowid, xwordmodel.crossword_setters.name).order_by(fn.Lower(xwordmodel.crossword_setters.name))
    setters = []
    for row in cs.dicts():
        setters.append([row['rowid'], row['name']])
    return(setters)

"""
Construct an array containing the solution_type rowid and name
suitable for use in a SELECT form element
"""
def get_solution_types():
    rs=xwordmodel.solution_types.select(xwordmodel.solution_types.rowid, xwordmodel.solution_types.name).order_by(fn.Lower(xwordmodel.solution_types.name))
    s_types = []
    for row in rs.dicts():
        s_types.append([row['rowid'], row['name']])
    return(s_types)

"""
Basic attempt to sanitize submitted form data
Attempt to validate all elements in the form data but if any one element
is bad make sure the whole form is invalidated.
"""
def sanitize_input(form):
    data = {}
    rc = ""
    for elem in request.form:
        if elem == "name":
            (r, data[elem]) = validate_name(form[elem])
        elif re.match(r'^.*_id$', elem):
            (r, data[elem]) = validate_id(form[elem])
        else:
            (r, data[elem]) = validate_text(form[elem])
        if rc == "": rc = r
    return(rc, data)


def validate_name(str):
    if not re.match(r'^[a-zA-Z0-9-_.\' ()]*$', str):
        return("Invalid characters in name field: Only allowed a-zA-Z0-9-_. '", re.sub('[^a-zA-Z0-9-_\'. ]', "", str))
    return("", str)

'''
Initial attempt at stripping any unwanted HTML from the input so that it can be displayed on an output page.
Uses the HTMLStripper to subclass HTMLParser
Params:
  str: string submitted via an HTTP request
Returns:
  (error-msg, sanitized-string)
'''
def validate_text(str):
    s = HTMLStripper()
    s.feed(str)
    return("", s.get_data())

"""
We expect submitted id values to be numeric
"""
def validate_id(str):
    try:
        int(str)
    except ValueError:
        return("id values must be numeric", "0")
    return("", str)

"""
Need to calculate the next rowid value for a table - not used with SQLite3
"""
def nextId(tbl):
    return(xwordmodel.database.execute_sql("SELECT MAX(rowid)+1 FROM %s" % tbl),scalar())


"""                                          """
"""  P A G I N A T I O N    C L A S S        """
"""                                          """
""" From http://flask.pocoo.org/snippets/44/ """
"""                                          """
class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

""" Pagination view helpers             """
""" http://flask.pocoo.org/snippets/44/ """
def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)

"""                                                  """
"""  E N D   O F   P A G I N A T I O N    C L A S S  """
"""                                                  """