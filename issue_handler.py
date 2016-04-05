from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from project_handler import *
import json as simplejson
from lib import BaseRequest, get_cache, slugify
import settings
from models import Project, Issue


class IssueHandler(BaseRequest):
    def get(self, project_slug, issue_slug):
        if self.request.path[-1] != "/":
            self.redirect("%s/" % self.request.path, True)
            return

        user = users.get_current_user()

        output = None
        if not user:
            self.redirect('/')

        if output is None:
            try:
                issue = Issue.all().filter('internal_url =', "/%s/%s/" % (
                project_slug, issue_slug)).fetch(1)[0]
                issues = Issue.all().filter('project =', issue.project).filter(
                    'fixed =', False).fetch(10)
            except IndexError:
                self.render_404()
                return

            on_list = False
            try:
                if user.email() in issue.project.other_users:
                    on_list = True
            except:
                pass

            if issue.project.user == user or users.is_current_user_admin() or on_list:
                owner = True
            else:
                owner = False
            context = {
                'issue': issue,
                'issues': issues,
                'owner': owner,
            }
            # calculate the template path
            output = self.render("issue.html", context)

        if not user:
            memcache.add("/%s/%s/" % (project_slug, issue_slug), output, 60)

        self.response.out.write(output)

    def post(self, project_slug, issue_slug):

        # if we don't have a user then throw
        # an unauthorised error
        user = users.get_current_user()
        if not user:
            self.render_403()
            return

        issue = Issue.all().filter('internal_url =', "/%s/%s/" % (
        project_slug, issue_slug)).fetch(1)[0]

        user = users.get_current_user()

        name = self.request.get("name")
        description = self.request.get("description")
        email = self.request.get("email")
        fixed = self.request.get("fixed")
        fixed_description = self.request.get("fixed_description")

        issue.name = name
        issue.description = description
        if email:
            issue.email = email
        else:
            issue.email = None
        issue.fixed = bool(fixed)
        if fixed:
            issue.fixed_description = fixed_description
        else:
            issue.fixed_description = None

        issue.put()
        logging.info(
            "issue edited: %s in %s" % (issue.name, issue.project.name))

        self.redirect("/projects%s" % issue.internal_url)

