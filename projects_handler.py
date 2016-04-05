from lib import BaseRequest, get_cache, slugify
from google.appengine.api import users
import re
import os
import logging
from datetime import datetime

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from project_handler import *
from models import *


class ProjectsHandler(BaseRequest):
    def get(self):
        if self.request.path[-1] != "/":
            self.redirect("%s/" % self.request.path, True)
            return

        user = users.get_current_user()
        output = None
        if not user:
            output = get_cache("projects")
        if output is None:
            projects = Project.all().order('-created_date').fetch(50)
            context = {
                'projects': projects,
            }
            # calculate the template path
            output = self.render("projects.html", context)
            if not user:
                memcache.add("projects", output, 3600)
        self.response.out.write(output)

    def post(self):

        # if we don't have a user then throw
        # an unauthorised error
        user = users.get_current_user()
        if not user:
            self.render_403()
            return

        name = self.request.get("name")

        # check we have a value
        if name:
            # then check we have a value which isn't just spaces
            if name.strip():
                if Project.all().filter('name =', name).count() == 0:
                    # we also need to check if we have something with the same slug
                    if Project.all().filter('slug =', slugify(
                            unicode(name))).count() == 0:
                        try:
                            project = Project(
                                name=name,
                                user=users.get_current_user(),
                            )
                            project.put()
                            logging.info("project added: %s" % project.name)
                        except db.BadValueError, e:
                            logging.error("error adding project: %s" % e)
        self.redirect('/')

