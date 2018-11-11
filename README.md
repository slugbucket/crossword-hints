# Crossword solutions and hints

An online reference for cryptic crossword solutions with an
indication as how the answer can be derived from the clue and
linked to the setter with a measure of the difficulty level
associated with their clues.

Python environment

## Python Flask

## virtualenv

## uwsgi

# Application routes
Accessing the sections of the application is achieved through a RESTful
interface in the following forms:
* /<controllor>/ - index list of all items in the database model
* /<controller>/new - form to add a new record to the database
* /<controller>/:id - display the details of the record with rowid of :id
* /<controller>/:id/edit - edit the details of the record with rowid of :id

## route methods
The routes can specify the methods over which data can be submitted.
index and show routes should only accept GET requests, while new and
edit routes can also accept POST requests when new or updated data
is submitted via a form.

## JQuery AJAX
The front page of the application provides an input box to prompt
for a cue word that is often found in clues. a JQuery AJAX request is
used to pass at least two letters to a route that searches  particular
table and presents an autocomplete list from which a matching word
can be selected.
The request includes a callback reference in the query string which
needs to be included in the JSONP response.

# Database model
The database schema is modelled in the application using the Peewee module.

## peewee
Peewee is used as the ORM for the database because of its and the database's simplicity.

### Limitations
Despite looking that it should be possible to retrieve columns from
multiple tables using inner joins it doesn't actually seem to work.

The following tables are solution_types_edit

### activity_logs
Records the inserts, updates and deletions of records from the tables.

### crossword_setters
Records the name and brief description of a published crossword setter.
There is also an indication as to the general skill level required to
solve the clues.

### crossword_solutions
Records the details of a crossword clues and solutions along with the
type of clue and a hint showing how to get the solution from the clue.

### cue_words
A lookup table of key words in a clue that can indicate the method
required to solve part or all of the clue.
This will often, but not always, indicate the type of clue; sometimes
the cue is just for a few letters of the solution.

### setter_types
Records a simple ranking order for the level of difficulty associated
with the setter.

### solution_types
Stores the name a brief description of the type of clue.

# Templates
If the template directory structure has more than a passing resemblance to
Ruby on Rails, it's not a coincidence; perhaps Rails took the ideas from
elsewhere, but it works well and encourages consistency.

The display-related templates are kept in the views sub-directory of the
templates folder.
There is a template directory for each route 'controller' or database
model class:
* templates/views/crossword-hints
* templates/views/crossword-setters
* templates/views/crossword-solutions
* templates/views/setter-types
* templates/views/solution-types

Each of these template directories will typically contain the following
Jinja2 templates
* index.html - main listing page for the section
* show.html - detail page for a specific item
* _form.html - partial template for new and edit forms
* new.html - display the form with prompts for a new item
* edit.html - display the form to edit an existing item

There are two general template directories that can be used by any of
the main application templates.

* partials - section of page (e.g., navigation bar) frequently used
* layouts - The whole page layout with placeholders (blocks) for content

# Testing
One of the goals for developing this project is to get an insight into
maintaining a test regime as features are developed.

# Unit Tests
The unit tests are written using the Python unittest framework. The emphasis
is on checking the database functionality, trying to trigger integrity
violations where we'd expect them, and emulating page navigation and
form submission, including responses to bad input.

To run the tests use,

```bash
APP_SETTINGS='test-settings.py' python crossword-hints-test.py
```

# Development

# Updating

# TODO
* Investigte WTForms for form validation

# References
Sources of additional information.
* https://stackoverflow.com/questions/11574850/jsonp-web-service-with-python -
  help describing how to handle JSONP data with JQuery.
