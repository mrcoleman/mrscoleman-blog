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
    "/edit","edit")



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
        	print "failed login"
        	return render.index(errormessage="Invalid Login")
        else:
            set_login(u)
            print "logged in"
            return web.seeother("/home")

class home:
    @authorized
    def GET(self):
        posts = web.ctx.orm.query(Post).order_by(Post.date_posted.desc())
        return render.home(posts = posts,building=os.path.isfile(os.path.join(config.BASE_DIR,"build.lock")))
        
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
		print form.title
		p.title = form.title
		p.url = form.url
		p.body = form.body_text
		p.summary = form.summary
		print p.id
		if p.id == None:
			web.ctx.orm.add(p)
		web.ctx.orm.commit()
		web.redirect("/home")

class build:
    @authorized
    def GET(self):
        copyfile(os.path.join(config.BASE_DIR,"data.db3"),os.path.join(config.BASE_DIR,"build.db3"))
        lock_file = file(os.path.join(config.BASE_DIR,'build.lock'),'w')
        lock_file.write('building')
        lock_file.close()
        subprocess.call(["python","build_site.py"])
        return web.seeother("/home")


if __name__ == "__main__":
    app.run()