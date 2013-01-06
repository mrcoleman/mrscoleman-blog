from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Text
import os
import datetime
import config

engine = create_engine('sqlite:///'+os.path.join(config.BASE_DIR,'data.db3'),echo=True)

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)

    def __init__(self, name,first_name, last_name, password):
        self.name = name
        self.first_name = first_name
        self.last_name = last_name
        self.password = password

    def __repr__(self):
       return "<User('%s','%s','%s', '%s')>" % (self.name, self.first_name,self.last_name, self.password)

class Post(Base):
	__tablename__ = 'posts'
	id = Column(Integer, primary_key=True)
	title = Column(String)
	url = Column(String)
	body = Column(Text)
	summary = Column(Text)
	date_posted = Column(DateTime, default = datetime.datetime.now)

	def __init__(self):
		self.title=""
		self.url=""
		self.body=""
		self.summary=""

class Setting(Base):
    __tablename__ = 'settings'
    key = Column(String, primary_key=True)
    value = Column(String)

    def __init__(self):
        self.key = ""
        value = ""





users_table = User.__table__
post_table = Post.__table__

metadata = Base.metadata

if __name__ == "__main__":
    from sqlalchemy.orm import scoped_session, sessionmaker
    import hashlib
    def create_password(in_pass):
        hashout = hashlib.md5(in_pass).hexdigest()
        for i in range(1,50):
            hashout = hashlib.md5(hashout).hexdigest()
        return hashout
    metadata.create_all(engine)
    db = scoped_session(sessionmaker(bind=engine))
    u = User(name="test@example.com"
        ,first_name="Test"
        ,last_name ="User"
        ,password =create_password("pass"))
    db.add(u)
    p = Post()
    p.title="First Post"
    p.url="first_post"
    p.summary="This is my First Post in my new blog."
    p.body="<p>Here is the first post in my new blog. You can delete this post and create a new one.</p>"
    db.add(p)
    db.commit()

