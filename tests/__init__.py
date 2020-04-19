import click
from flask.cli import with_appcontext

@click.command('test')
@with_appcontext
def test():
    ''' Run all the tests '''
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

def test_init_app(app):
    app.cli.add_command(test)
