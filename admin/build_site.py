import os
import datetime
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
from jinja2 import Environment, PackageLoader

OUTPUT_DIR = os.path.dirname(os.path.realpath("../static/")) #by default we're going to go up one directory and save to the static folder

env = Environment(loader=PackageLoader('build_site', os.path.realpath('templates/site')))
index = env.get_template('index.html')
single = env.get_template('single.html')


engine = create_engine('sqlite:///build.db3', echo=True)
db = scoped_session(sessionmaker(bind=engine))



def render_all_posts(posts):
	for post in posts:
		render_post(post)

def render_post(post):
	html_out = single.render(post=post)
	full_path = os.path.join(OUTPUT_DIR,post.date_posted.strftime('%Y-%m-%d'),post.url)
	if os.path.isdir(full_path) != True:
		os.makedirs(full_path)
	file_out = file(os.path.join(full_path,"index.html"),'w')
	file_out.write(html_out)
	file_out.close()

def render_index(posts):
	html_out = index.render(posts=posts)
	file_out = file(os.path.join(OUTPUT_DIR,'index.html'),'w')
	file_out.write(html_out)
	file_out.close()



posts = db.query(Post).all()
render_index(posts[:10])
render_all_posts(posts)
db.close()
engine.dispose()
os.rename('build.db3','build.'+datetime.datetime.now().strftime('%Y-%m-%d')+'.db3')