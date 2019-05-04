import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


# Class formed to store the data of the author of the book
class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer,  primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return{
            'name': self.name,
            'id': self.id
        }


# Class formed to store the data of the Books
class Books_Data(Base):
    __tablename__ = 'booksdb'
    bookid = Column(Integer, primary_key=True)
    bname = Column(String(100), nullable=False)
    genre = Column(String(100), nullable=False)
    desc = Column(String(1000), nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'))
    own = relationship(Author)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return{
            'bname': self.bname,
            'desc': self.desc,
            'bookid': self.bookid,
            'genre': self.genre,
        }


engine = create_engine('sqlite:///bookscatalogue.db')


Base.metadata.create_all(engine)
