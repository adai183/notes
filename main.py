import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
template = JINJA_ENVIRONMENT.get_template('index.html')



def guestbook_key(guestbook_name= "guestbook"):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)


class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(webapp2.RequestHandler):

    def get(self):

        blank_entry = self.request.get('blank_entry','')

        
        guestbook_name = self.request.get('guestbook_name',
                                          'guestbook')
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        num_greetings = 10
        greetings = greetings_query.fetch(num_greetings)


        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'blank_entry': blank_entry,
            'user': user,
            'greetings': greetings,           
            'url': url,
            'url_linktext': url_linktext,
        }

        self.response.write(template.render(template_values))

class Guestbook(webapp2.RequestHandler):
    def post(self):
        blank_entry = ""
        
        guestbook_name = self.request.get('guestbook_name',
                                          'guestbook')
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())


        greeting.content = self.request.get('content')
        if greeting.content == "":
             blank_entry = "No text was entered, please try again"
             
        else:    
            greeting.put()

        query_params = {'guestbook_name': guestbook_name,'blank_entry': blank_entry}
        self.redirect('/?blank_entry=No text was entered, please try again') 
        self.redirect('/?index.html' + urllib.urlencode(query_params))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
], debug=True)