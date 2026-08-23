# -*- coding: utf-8 -*-
"""
     I  N  T  E  R  N  A  L    F  U  N  C  T  I  O  N  S
"""
from datetime import datetime
from html.parser import HTMLParser
from math import ceil # For use with pagination
import re
from urllib.parse import urljoin, urlparse
from flask import request, url_for, redirect
from peewee import fn
# from crossword_hints import application
from crossword_hints.models import crossword_hints as xwordmodel
# For input (and output) sanitization. Taken from:
# https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python (comment 16)


class HTMLStripper(HTMLParser):
    """
    Custom class for stripping HTML tags and entity references
    """
    convert_charrefs = True


    def __init__(self):
        """Class constructor
        """
        super().__init__()
        self.reset()
        self.fed = []


    def handle_data(self, data):
        """Class method for handling parsed data
        """
        self.fed.append(data)


    def handle_entityref(self, name):
        """Class method for handling entity references
        """
        self.fed.append(f"&{name};")


    def get_data(self):
        """Class method for returing data as a string"""
        return "".join(self.fed)


def highlight_text(text: str, word: str, cls: str) -> str:
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
    p = re.compile(word, re.IGNORECASE)
    m = p.search(text)
    if m:
        hstr = f"<span class='{cls}'>{m.group()}</span>"
        return p.sub(hstr, text)
    return text


def is_safe_url(target) -> str:
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
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def get_redirect_target() -> str:
    """
    Function to try and determine a suitable referral point that is safe
    to redirect the client back after an action such as login.
    Params:

    Returns:
    string: target URL
    """
    for target in request.args.get("next"), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target
    return ""


def redirect_back(endpoint, **values) -> str:
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
    target = request.args["next"]
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)


def add_log(actor, action, item_type, item_id, activity) -> None:
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
    log = xwordmodel.activity_logs(
        actor=actor,
        action=action,
        item_type=item_type,
        item_id=item_id,
        act_action=activity,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    log.save()


def get_setter_types() -> list:
    """
    Construct an array containing the setter_type rowid and name
    suitable for use in a SELECT form element
    """
    rs = xwordmodel.setter_types.select(
        xwordmodel.setter_types.rowid, xwordmodel.setter_types.name
    ).order_by(fn.Lower(xwordmodel.setter_types.name))
    s_types = []
    for row in rs.dicts():
        s_types.append([row["rowid"], row["name"]])
    return s_types


def get_crossword_setters() -> list:
    """
    Construct an array containing the crossword setter rowid and name
    suitable for use in a SELECT form element
    """
    cs = xwordmodel.crossword_setters.select(
        xwordmodel.crossword_setters.rowid, xwordmodel.crossword_setters.name
    ).order_by(fn.LOWER(xwordmodel.crossword_setters.name))
    setters = []
    for row in cs.dicts():
        setters.append([row["rowid"], row["name"]])
    return setters


def get_solution_types() -> list:
    """
    Construct an array containing the solution_type rowid and name
    suitable for use in a SELECT form element
    """
    rs = xwordmodel.solution_types.select(
        xwordmodel.solution_types.rowid, xwordmodel.solution_types.name
    ).order_by(fn.LOWER(xwordmodel.solution_types.name))
    s_types = []
    for row in rs.dicts():
        s_types.append([row["rowid"], row["name"]])
    return s_types


def sanitize_input(form) -> tuple:
    """
    Basic attempt to sanitize submitted form data
    Attempt to validate all elements in the form data but if any one element
    is bad make sure the whole form is invalidated.
    """
    data = {}
    rc = ""
    for elem in request.form:
        if elem == "name":
            (r, data[elem]) = validate_name(form[elem])
        elif re.match(r"^.*_id$", elem):
            (r, data[elem]) = validate_id(form[elem])
        else:
            (r, data[elem]) = validate_text(form[elem])
        if rc == "":
            rc = r
    return (rc, data)


def validate_name(vstr) -> tuple:
    """
    Validation function to check that input is a string
    """
    if not re.match(r"^[a-zA-Z0-9-_.\' ()]*$", vstr):
        return (
            "Invalid characters in name field: Only allowed a-zA-Z0-9-_. '",
            re.sub("[^a-zA-Z0-9-_'. ]", "", vstr),
        )
    return ("", vstr)


def validate_text(vstr) -> tuple:
    """
    Initial attempt at stripping any unwanted HTML from the input
    so that it can be displayed on an output page.
    Uses the HTMLStripper to subclass HTMLParser
    Params:
    vstr: string submitted via an HTTP request
    Returns:
    (error-msg, sanitized-string)
    """
    s = HTMLStripper()
    s.feed(vstr)
    return ("", s.get_data())


def validate_id(vstr) -> tuple:
    """
    We expect submitted id values to be numeric
    """
    try:
        int(vstr)
    except ValueError:
        return ("id values must be numeric", "0")
    return ("", vstr)


# def next_id(tbl): Not used
#     """
#     Need to calculate the next rowid value for a table - not used with SQLite3
#     """
#     return (xwordmodel.database.execute_sql("SELECT MAX(rowid)+1 FROM {tbl}", scalar()))


class Pagination:
    """
     P A G I N A T I O N    C L A S S

    From http://flask.pocoo.org/snippets/44/
    """


    def __init__(self, page, per_page, total_count):
        """ Pagination class constructor
        """
        self.page = page
        self.per_page = per_page
        self.total_count = total_count


    @property
    def pages(self) -> int:
        """Class method for pages count
        """
        return int(ceil(self.total_count / float(self.per_page)))


    @property
    def has_prev(self) -> bool:
        """Class method for a previous pagination page
        """
        return self.page > 1


    @property
    def has_next(self) -> bool:
        """Class method for a next pagination page
        """
        return self.page < self.pages


    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        """Class iterator for pagination Generator
        """
        last = 0
        for num in range(1, self.pages + 1):
            if (
                num <= left_edge
                or (
                    num > self.page - left_current - 1
                    and num < self.page + right_current
                )
                or num > self.pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num


def url_for_other_page(page) -> str:
    """Pagination view helpers
    http://flask.pocoo.org/snippets/44/
    """
    args = request.view_args.copy()
    args["page"] = page
    return url_for(request.endpoint, **args)
