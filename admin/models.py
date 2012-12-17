from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Text
import datetime

engine = create_engine('sqlite:///data.db3', echo=True)

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

users_table = User.__table__
post_table = Post.__table__

metadata = Base.metadata


if __name__ == "__main__":
    metadata.create_all(engine)