#!/usr/bin/env python

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from project_handler import *
from projects_handler import *
from issue_handler import *
import json as simplejson
from lib import BaseRequest, get_cache, slugify
import settings
from models import Project, Issue




class Index(BaseRequest):
    "Home page. Shows either introductory info or a list of the users projects"

    def get(self):
        if users.get_current_user():
            # if we have a user then get their projects
            projects = Project.all().filter('user =',
                                            users.get_current_user()).order(
                '-created_date').fetch(50)
            context = {
                'projects': projects,
            }
            output = self.render("index.html", context)
        else:
            # otherwise it's a static page so cache for a while
            output = get_cache("home")
            if output is None:
                output = self.render("home.html")
                memcache.add("home", output, 3600)
        self.response.out.write(output)



class NotFoundPageHandler(BaseRequest):
    def get(self):
        self.error(404)
        user = users.get_current_user()
        output = None
        if not user:
            output = get_cache("error404")
        if output is None:
            output = self.render("404.html")
            if not user:
                memcache.add("error404", output, 3600)
        self.response.out.write(output)


def application():
    "Run the application"
    # wire up the views
    ROUTES = [
        ('/', Index),
        ('/projects/?$', ProjectsHandler),
        ('/projects/([A-Za-z0-9-]+)/delete/?$', ProjectDeleteHandler),
        ('/projects/([A-Za-z0-9-]+)/settings/?$', ProjectSettingsHandler),
        ('/projects/([A-Za-z0-9-]+)/([A-Za-z0-9-]+)/?$', IssueHandler),
        ('/projects/([A-Za-z0-9-]+)/?$', ProjectHandler),
        ('/.*', NotFoundPageHandler),
    ]
    application = webapp.WSGIApplication(ROUTES, debug=settings.DEBUG)
    return application


def main():
    "Run the application"
    run_wsgi_app(application())


if __name__ == '__main__':
    main()