#!/usr/bin/env python

from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import make_response, flash
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.pool import SingletonThreadPool
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from database_setup import Base, Author, Books_Data, User
import httplib2
import json
import requests
import random
import string

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

engine = create_engine('sqlite:///bookscatalogue.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # for Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # to Obtain authorization code
    code = request.data

    try:
        # to Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # to Check that the access token gained is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error found in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token gained is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this application.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for the later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get the user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    print data['email']
    if session.query(User).filter_by(email=data['email']).count() != 0:
        current_user = session.query(User).filter_by(email=data['email']).one()
    else:
        newUser = User(name=data['name'],
                       email=data['email'])
        session.add(newUser)
        session.commit()
        current_user = newUser

    login_session['user_id'] = current_user.id
    print current_user.id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output
# DISCONNECT - Revoke a current user's access token and then reset
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/catalogue/')
def showCatalogue():
    """Show all Authors"""
    author = session.query(Author).all()
    return render_template('listdetail.html', tauthor=author)


@app.route('/aftercatalogue/')
def aftershowCatalogue():
    """Show all Authors with the edit , delete options"""
    author = session.query(Author).all()
    return render_template('listdetails.html', tauthor=author)


@app.route('/catalogue/new/', methods=['GET', 'POST'])
def newAuthor():
    """Add new Author"""
    if 'username' not in login_session:
        return redirect('/login')

    user_id = login_session['user_id']

    if request.method == 'POST':
        newAuthor = Author(name=request.form['name'], user_id=user_id)
        session.add(newAuthor)
        flash('New Author %s Successfully Created' % newAuthor.name)
        session.commit()
        return redirect(url_for('aftershowCatalogue'))
    else:
        return render_template('createdetails.html')


@app.route('/catalogue/<int:author_id>/edit/', methods=['GET', 'POST'])
def editAuthor(author_id):
    """Edit Author"""
    if 'username' not in login_session:
        return redirect('/login')

    user_id = login_session['user_id']

    author = session.query(Author).filter_by(id=author_id).one()

    if author.user_id != login_session['user_id']:
        flash("""Author was created by another user and can only
                be edited by creator""")
        return redirect(url_for('aftershowCatalogue'))

    if request.method == 'POST':
        if request.form['name']:
            author.name = request.form['name']
            flash('Author Successfully Updated %s' % author.name)
            return redirect(url_for('aftershowCatalogue'))
    else:
        return render_template('editauthor.html', author=author)


@app.route('/catalogue/<int:author_id>/delete/', methods=['GET', 'POST'])
def deleteAuthor(author_id):
    """Delete Author"""
    if 'username' not in login_session:
        return redirect('/login')

    author = session.query(Author).filter_by(id=author_id).one()

    if author.user_id != login_session['user_id']:
        flash("""Author was created by another user and can only be
        deleted by creator""")
        return redirect(url_for('aftershowCatalogue'))

    if request.method == 'POST':
        session.delete(author)
        flash('%s Successfully Deleted' % author.name)
        session.commit()
        return redirect(url_for('aftershowCatalogue', author_id=author_id))
    else:
        return render_template('authordelete.html', author=author)


@app.route('/catalogue/<int:author_id>/')
@app.route('/catalogue/<int:author_id>/item/')
def showBooks(author_id):
    """Show all Books"""

    author = session.query(Author).filter_by(id=author_id).one()
    book = session.query(Books_Data).filter_by(author_id=author_id).all()
    return render_template('listdetailss.html', author=author, book=book)


@app.route('/catalogue/<int:author_id>/item/new', methods=['GET', 'POST'])
def newBook(author_id):
    """Add new Book"""
    if 'username' not in login_session:
        return redirect('/login')

    user_id = login_session['user_id']

    if request.method == 'POST':
        newBook = Books_Data(bname=request.form['bname'],
                             genre=request.form['genre'],
                             desc=request.form['desc'],
                             author_id=author_id,
                             user_id=user_id)
        session.add(newBook)
        session.commit()
        flash('%s Successfully Created' % (newBook.bname))
        return redirect(url_for('showBooks', author_id=author_id))
    else:
        return render_template('listdetailsss.html', author_id=author_id)

    return render_template('listdetailsss.html', tbook=author)


@app.route('/catalogue/<int:author_id>/item/<int:book_id>/edit',
           methods=['GET', 'POST'])
def editBook(author_id, book_id):
    """Edit Book"""
    if 'username' not in login_session:
        return redirect('/login')
    book = session.query(Books_Data).filter_by(bookid=book_id).one()

    if book.user_id != login_session['user_id']:
        flash("""Book was created by another user and can only be
        edited by creator""")
        return redirect(url_for('showBooks', author_id=author_id))

    if request.method == 'POST':
        if request.form['bname']:
            book.bname = request.form['bname']
        if request.form['desc']:
            book.genre = request.form['genre']
        if request.form['desc']:
            book.desc = request.form['desc']
        session.add(book)
        session.commit()
        flash('%s Successfully Updated' % (book.bname))
        return redirect(url_for('showBooks', author_id=author_id))
    else:
        return render_template('editbook.html',
                               author_id=author_id,
                               book_id=book_id,
                               book=book)


@app.route('/catalogue/<int:author_id>/item/<int:book_id>/delete',
           methods=['GET', 'POST'])
def deleteBook(author_id, book_id):
    """Delete Book"""
    if 'username' not in login_session:
        return redirect('/login')
    book = session.query(Books_Data).filter_by(bookid=book_id).one()

    if book.user_id != login_session['user_id']:
        flash("""Book was created by another user and can only be
        deleted by creator""")
        return redirect(url_for('showBooks', author_id=author_id))

    if request.method == 'POST':
        session.delete(book)
        session.commit()
        flash('%s Successfully Deleted' % (book.bname))
        return redirect(url_for('showBooks', author_id=author_id))
    else:
        return render_template('bookdelete.html',
                               author_id=author_id,
                               book=book)


@app.route('/author/JSON')
def authorsJSON():
    """Return JSON for all the authors"""
    authors = session.query(Author).all()
    return jsonify(authors=[c.serialize for c in authors])


@app.route('/author/<int:author_id>/JSON')
def authorBookJSON(author_id):
    """Return JSON of all the books for a author"""
    author = session.query(Author).filter_by(id=author_id).one()
    books = session.query(Books_Data).filter_by(
        bookid=author_id).all()
    return jsonify(Books=[i.serialize for i in books])


@app.route('/author/<int:author_id>/book/<int:book_id>/JSON')
def bookJSON(author_id, book_id):
    """Return JSON for a book"""
    book = session.query(Books_Data).filter_by(bookid=book_id).one()
    return jsonify(book=book.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
