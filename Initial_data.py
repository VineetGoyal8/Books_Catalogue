from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Author, Books_Data

engine = create_engine('sqlite:///bookscatalogue.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

Firstauthor = Author(id="1", name="Vineet")

session.add(Firstauthor)

firstbook = Books_Data(bname="War and Peace", genre="Historical",
                       desc="It is regarded as a central work of world\
                       literature and one of Tolstoy's finest literary\
                       achievements", author_id="1")

session.add(firstbook)

secondbook = Books_Data(bname="Emma", genre="Romantic",
                        desc="novel about youthful hubris and the perils\
                        of misconstrued romance.", author_id="1")

session.add(secondbook)

Secondauthor = Author(id="2", name="Varun")

session.add(Secondauthor)

firstbook = Books_Data(bname="Dubliners", genre="Historical",
                       desc="Dubliners is a collection of \
                       fifteen short stories by James Joyce, first \
                       published in 1914.", author_id="2")

session.add(firstbook)

secondbook = Books_Data(bname="The Sound and the Fury", genre="Fiction",
                        desc="novel centers on the Compson \
                        family, former Southern aristocrats who \
                        are struggling to deal with the dissolution of \
                        their family and its reputation", author_id="2")

session.add(secondbook)

Thirdauthor = Author(id="3", name="Yashodhan")

session.add(Thirdauthor)

firstbook = Books_Data(bname="In Search of Lost Time", genre="Romantic",
                       desc="The novel recounts the experiences\
                       of the Narrator while he is growing up, \
                       learning about art, participating in society,\
                       and falling in love.", author_id="3")

session.add(firstbook)

secondbook = Books_Data(bname="To the Lighthouse", genre="Fiction",
                        desc="The novel centres on the Ramsay \
                        family and their visits to the Isle of \
                        Skye in Scotland between 1910 \
                        and 1920.", author_id="3")

session.add(secondbook)
session.commit()

print('Initial data added !!')
