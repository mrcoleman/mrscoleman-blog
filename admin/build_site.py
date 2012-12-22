import os
import datetime
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
from jinja2 import Environment, PackageLoader
from os.path import expanduser
import config


TIME_OUT = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
OUTPUT_DIR = os.path.join(config.BASE_DIR,TIME_OUT) 
DB_FILE = os.path.join(config.BASE_DIR,'build.'+TIME_OUT+'.db3')
TMP_DB_FILE = os.path.join(config.BASE_DIR,'build.db3')
LOCK_FILE = os.path.join(config.BASE_DIR,'build.lock')

def render_all_posts():
	current_offset = 0
	posts = db.query(Post).order_by(Post.date_posted.desc()).limit(10).offset(current_offset)
	while posts.count() != 0:
		for post in posts:
			render_post(post)
		current_offset = current_offset + 10
		posts = db.query(Post).order_by(Post.date_posted.desc()).limit(10).offset(current_offset)

def render_post(post):
	html_out = single.render(post=post)
	full_path = os.path.join(OUTPUT_DIR,post.date_posted.strftime('%Y/%m/%d'),post.url)
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
env = Environment(loader=PackageLoader('build_site', os.path.join(config.BASE_DIR,'templates/site')))
index = env.get_template('index.html')
single = env.get_template('single.html')

if os.path.exists(LOCK_FILE) and os.path.exists(TMP_DB_FILE):
	if os.path.exists(OUTPUT_DIR) == False:
		os.mkdir(OUTPUT_DIR)
	os.rename(TMP_DB_FILE,DB_FILE)
	engine = create_engine('sqlite:///'+ DB_FILE)
	db = scoped_session(sessionmaker(bind=engine))
	posts = db.query(Post).order_by(Post.date_posted.desc()).limit(10)
	render_index(posts)
	render_all_posts()
	db.commit()
	os.remove(LOCK_FILE)