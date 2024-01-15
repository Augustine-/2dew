"""the application factory lives here, along with some routes."""
# pylint: disable=import-outside-toplevel
import os

from flask import Flask

# behold, the application factory function
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True) # the flask instance
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('TODEW_KEY'),
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # when not testing: load instance conf, if extant
        app.config.from_pyfile('config.py', silent=True)
    else:
        # when testing, load test conf
        app.config.from_mapping(test_config)

    # ensure instance folder
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # yo!
    @app.route('/hello')
    def hello():
        return 'Yo, world!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
