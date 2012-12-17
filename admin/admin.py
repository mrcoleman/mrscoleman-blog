import web
import os
import hashlib
from web.contrib.template import render_jinja
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *

render = render_jinja(
        'templates/admin',   # Set template directory.
        encoding = 'utf-8',                         # Encoding.
    )
OUTPUT_DIR = os.path.dirname(os.path.realpath("../static")) #by default we're going to go up one directory and save to the static folder


urls = ("/","index",
    "/home","home",
    "/login","login",
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
		u_Lookup = web.ctx.orm.query(User).filter(User.name == "test@example.com").first()
		if u_Lookup == None:
			u = User(name="test@example.com"
		            ,first_name="Test"
		            ,last_name ="User"
		            ,password =create_password("pass"))
			web.ctx.orm.add(u)
			web.ctx.orm.commit()
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
    def GET(self):
    	print "home"
        if is_loggedin():
        	posts = web.ctx.orm.query(Post).order_by(Post.date_posted.desc())
        	return render.home(posts = posts)
        else:
        	print "fail"
        	return web.seeother("/")
class edit:
	def GET(self):
		post_id = web.input().post_id
		if post_id == None:
			post_id = 0
		post = web.ctx.orm.query(Post).filter(Post.id == int(post_id)).first()
		if post == None:
			post = Post()
			post.id = 0		
		return render.edit(post = post)
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
		form = web.input()
		print form.title
		p.title = form.title
		p.url = form.url
		p.body = form.body_text
		print p.id
		if p.id == None:
			web.ctx.orm.add(p)
		web.ctx.orm.commit()
		web.redirect("/home")
if __name__ == "__main__":
	app.run()