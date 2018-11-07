# Crossword solutions and hints

An online reference for cryptic crossword solutions with an
indication as how the answer can be derived from the clue and
linked to the setter with a measure of the difficulty level
associated with their clues.

# Python Flask



# uwsgi



# Database model
The database schema is modelled in the application using the Peewee module.

## peewee



# Templates
If the template directory structure has more than a passing resemblance to
Ruby on Rails, it's not a coincidence; perhaps Rails took the ideas from
elsewhere, but it works well and encourages consistency.

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
