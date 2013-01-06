import os
import datetime
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
from jinja2 import Environment, PackageLoader
from os.path import expanduser
import ftplib
import config


TIME_OUT = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
OUTPUT_DIR = os.path.join(config.BASE_DIR,TIME_OUT) 
DB_FILE = os.path.join(config.BASE_DIR,'build.'+TIME_OUT+'.db3')
TMP_DB_FILE = os.path.join(config.BASE_DIR,'build.db3')
LOCK_FILE = os.path.join(config.BASE_DIR,'build.lock')

class BuildSettings():
	pass
def GetSettingByKey(key):
    setting = db.query(Setting).filter(Setting.key == key).first()
    return setting

def SetSettingByKey(key, value):
    setting = GetSettingByKey(key)
    isNew = False
    print setting
    if(setting == None):
        setting = Setting()
        setting.key = key
        isNew = True
    setting.value = value
    if(isNew):
        db.add(setting)
    db.commit()
def get_settings():
    setting_items = db.query(Setting).all()
    settings = BuildSettings()
    for setting_item in setting_items:
        setattr(settings,setting_item.key,setting_item.value)
    return settings

def makeDirAndSaveIndex(path_out,textOut):
	if os.path.isdir(path_out) != True:
		os.makedirs(path_out)
	file_out = file(os.path.join(path_out,"index.html"),'w')
	file_out.write(textOut)
	file_out.close()

def render_all_posts():
	current_offset = 0
	posts = db.query(Post).order_by(Post.date_posted.desc()).limit(10).offset(current_offset)
	while posts.count() != 0:
		for post in posts:
			render_post(post)
		current_offset = current_offset + 10
		posts = db.query(Post).order_by(Post.date_posted.desc()).limit(10).offset(current_offset)

def render_post(post):
	html_out = single.render(post=post,settings = settings)
	full_path = os.path.join(OUTPUT_DIR,post.date_posted.strftime('%Y/%m/%d'),post.url)
	makeDirAndSaveIndex(full_path,html_out)

def render_index(posts):
	html_out = index.render(posts=posts, settings = settings)
	makeDirAndSaveIndex(OUTPUT_DIR,html_out)

def render_archives():
	
	pages = post_count /10
	if (post_count % 10) > 0:
		pages = pages + 1
	for page in range(pages):
		has_next = True
		if page == (pages -1):
			has_next = False
		render_archivePage(page, has_next)

def render_archivePage( pageNumber, has_next):
	posts = db.query(Post).order_by(Post.date_posted.desc()).limit(10).offset(pageNumber*10)
	html_out = archivePage.render(posts=posts,pageNumber = (pageNumber+1),has_next = has_next, settings = settings)
	page_path = os.path.join(OUTPUT_DIR,str.format("archives/{0}",(pageNumber+1)))
	makeDirAndSaveIndex(page_path,html_out)

def uploadStaticFiles():
	ftp = ftplib.FTP()
	ftp.connect(config.FTP_HOST,config.FTP_PORT)
	ftp.login(config.FTP_USER)
	ftp.cwd(config.FTP_STATIC_ROOT)
	doUploadDir(ftp,OUTPUT_DIR)
	ftp.close()

def doUploadDir(ftp, currentDir):
	pass

env = Environment(loader=PackageLoader('build_site', os.path.join(config.BASE_DIR,'templates/site')))
index = env.get_template('index.html')
single = env.get_template('single.html')
archivePage = env.get_template('archivePage.html')
settings = BuildSettings()


if os.path.exists(LOCK_FILE) and os.path.exists(TMP_DB_FILE):
	print "doing it"
	if os.path.exists(OUTPUT_DIR) == False:
		os.mkdir(OUTPUT_DIR)
	os.rename(TMP_DB_FILE,DB_FILE)
	engine = create_engine('sqlite:///'+ DB_FILE)
	db = scoped_session(sessionmaker(bind=engine))
	settings=get_settings()
	posts = db.query(Post).order_by(Post.date_posted.desc()).limit(10)
	post_count = db.query(Post).count()
	render_index(posts)
	render_all_posts()
	render_archives()
	db.commit()
	#uploadStaticFiles()
	os.remove(LOCK_FILE)