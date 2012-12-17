import os
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('build_site', 'templates/site'))
template = env.get_template('index.html')

print template.render()
