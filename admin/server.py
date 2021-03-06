import web
import os
import hashlib
import subprocess
from web.contrib.template import render_jinja
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
from shutil import copyfile
import config

render = render_jinja(
        'templates/admin',   # Set template directory.
        encoding = 'utf-8',                         # Encoding.
    )

urls = ("/","index",
    "/home","home",
    "/login","login",
    "/build","build",
    "/edit","edit",
    "/settings","settings")



def load_sqla(handler):
    web.ctx.orm = scoped_session(sessionmaker(bind=engine))
    try:
        return handler()
    except web.HTTPError:
       web.ctx.orm.commit()
       raise
    except:
        web.ctx.orm.rollback()
        raise
    finally:
        web.ctx.orm.commit()
        # If the above alone doesn't work, uncomment 
        # the following line:
        #web.ctx.orm.expunge_all()

app = web.application(urls, globals())
app.add_processor(load_sqla)

class BuildSettings():
    pass
def GetSettingByKey(key):
    setting = web.ctx.orm.query(Setting).filter(Setting.key == key).first()
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
        web.ctx.orm.add(setting)
    web.ctx.orm.commit()

def get_settings():
    setting_items = web.ctx.orm.query(Setting).all()
    settings = BuildSettings()
    for setting_item in setting_items:
        setattr(settings,setting_item.key,setting_item.value)
    return settings

def create_password(in_pass):
        hashout = hashlib.md5(in_pass).hexdigest()
        for i in range(1,50):
            hashout = hashlib.md5(hashout).hexdigest()
        return hashout

def is_loggedin():
    c = web.cookies().get("mrsc_id")
    if c == None:
        return False
    else:
        return True
def authorized(func):
    def execute(*args ):
        if is_loggedin() != True:
            return web.seeother("/")
        return func(*args )
    return execute

def login_attempt(username, password):
    q = web.ctx.orm.query(User).filter(User.name == username).filter(User.password == password)
    u_Lookup = q.first()
    return u_Lookup

def set_login(user):
    web.setcookie("mrsc_id",user.id)



class index:
	def GET (self):
		if is_loggedin():
			return web.seeother("/home")
		return render.index(errormessage="")


class login:
    def GET(self):
        if is_loggedin():
            return web.seeother("/home")
        else:
            return render.index()
    def POST(self):
        form = web.input()
        u = login_attempt(form.username,create_password(form.password))
        if u == None:
        	return render.index(errormessage="Invalid Login")
        else:
            set_login(u)
            return web.seeother("/home")

class home:
    @authorized
    def GET(self):
        posts = web.ctx.orm.query(Post).order_by(Post.date_posted.desc())
        settings = get_settings()
        return render.home(posts = posts,building=os.path.isfile(os.path.join(config.BASE_DIR,"build.lock")), settings=settings)
        
class edit:
    @authorized
    def GET(self):
		post_id = web.input().post_id
		if post_id == None:
			post_id = 0
		post = web.ctx.orm.query(Post).filter(Post.id == int(post_id)).first()
		if post == None:
			post = Post()
			post.id = 0		
		return render.edit(post = post)
    @authorized
    def POST(self):
		post_id = web.input().post_id
		if post_id == None:
			post_id = 0
		p = web.ctx.orm.query(Post).filter(Post.id == int(post_id)).first()
		if p == None:
			p = Post()
			p.title =""
			p.url = ""
			p.body = ""
			p.summary = ""
		form = web.input()
		p.title = form.title
		p.url = form.url
		p.body = form.body_text
		p.summary = form.summary
		if p.id == None:
			web.ctx.orm.add(p)
		web.ctx.orm.commit()
		web.redirect("/home")

class settings:
    @authorized
    def POST(self):
        form = web.input()
        print "saving settings"
        print form.Google_Analytics_Id
        print form.Domain
        SetSettingByKey("Google_Analytics_Id",form.Google_Analytics_Id)
        SetSettingByKey("Domain",form.Domain)
        web.seeother("/home")

class build:
    @authorized
    def GET(self):
        copyfile(os.path.join(config.BASE_DIR,"data.db3"),os.path.join(config.BASE_DIR,"build.db3"))
        lock_file = file(os.path.join(config.BASE_DIR,'build.lock'),'w')
        lock_file.write('building')
        lock_file.close()
        subprocess.Popen(["python","build_site.py"])
        return web.seeother("/home")


if __name__ == "__main__":
    app.run()