"""
Liberouter GUI 2016
File: __init__.py
Author: Petr Stehlik <stehlik@cesnet.cz>

The basic initialization of the REST API happens within this file.
The basic steps:
    * app init and its configuration
    * configuration init
    * SSL init (if enabled)
    * base database connection to MongoDB (for users mainly)
    * Session manager
    * Authorization manager
    * Check if there are any users, if not set up a new admin
    * Enable CORS if requested
    * import all modules and its Blueprints
"""
import logging
from flask_socketio import SocketIO
from .Router import Router
log = logging.getLogger("INIT")

log.info("Setting up the application")
app = Router(__name__)

from .configurator import Config
"""
Load user config specified by an argument or in default path.
"""
try:
    config = Config()
except KeyError as e:
    import sys
    print("Missing item in config %s" % e)
    sys.exit(1)

from .dbConnector import dbConnector
from .session import SessionManager
from .bootstrap import routes, import_modules, check_users
from .Auth import Auth
from .role import Role

# System tools
if config["api"].getboolean("ssl", False):
    import ssl
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(config['ssl']['certificate'], config['ssl']['key'])

log.info("Connecting to database")
db = dbConnector()

log.info("Setting up session manager")
session_manager = SessionManager.from_object(config)

log.info("Setting up authorization module")
auth = Auth(db, session_manager)

check_users()

log.info("Configuring server application")
app.config.from_object(config)

if config['api'].getboolean('cors', False):
    log.info("CORS enabled")
    try:
        from flask.ext.cors import CORS
        CORS(app)
    except:
        log.error("Failed to initialize CORS. Is it installed?")
        exit(1)

log.info("Setting up SocketIO")
socketio = SocketIO(app)

"""
Import all modules from module path
"""
log.info("Importing modules")
import_modules()

app.add_url_rule('/', view_func = routes, methods=['GET'])

log.info("All is setup, ready to rock")
