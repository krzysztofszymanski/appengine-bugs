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


class ProjectHandler(BaseRequest):
    "Individual project details and issue adding"

    def get(self, slug):

        # we want canonocal urls so redirect to add a trailing slash if needed
        if self.request.path[-1] != "/":
            self.redirect("%s/" % self.request.path, True)
            return

        user = users.get_current_user()
        status = self.request.get("status")
        if not user:
            self.redirect("/")
        # if not logged in then use a cached version

        # if we don't have a cached version or are logged in
        # if output is None:
        try:
            project = Project.all().filter('slug =', slug).fetch(1)[0]
            issues = Issue.all().filter('project =', project)
            if status != '':
                if "open" == status:
                    issues = issues.filter('fixed =', False)
                if "closed" == status:
                    issues = issues.filter('fixed =', True)
            else:
                issues = issues.filter('fixed =', False)
            issues = issues.order('fixed').order('created_date')
        except IndexError:
            self.render_404()
            return

            # check to see if we have admin rights over this project
        if project.user == user or users.is_current_user_admin():
            owner = True
        else:
            owner = False

        context = {
            'project': project,
            'issues': issues,
            'owner': owner,
        }
        output = self.render("project.html", context)

        if not user:
            # only save a cached version if we're not logged in
            # so as to avoid revelaving user details
            memcache.add("project_%s" % slug, output, 3600)
        self.response.out.write(output)

    def post(self, slug):
        "Create an issue against this project"
        project = Project.all().filter('slug =', slug).fetch(1)[0]
        # get details from the form
        name = self.request.get("name")
        description = self.request.get("description")
        email = self.request.get("email")

        try:
            if Issue.all().filter('name =', name).filter('project =',
                                                         project).count() == 0:
                issue = Issue(
                    name=name,
                    description=description,
                    project=project,
                )
                if email:
                    issue.email = email
                issue.put()
        except Exception, e:
            logging.error("error adding issue: %s" % e)

        self.redirect("/projects/%s/" % slug)


class ProjectDeleteHandler(BaseRequest):
    "Delete projects, including a confirmation page"

    def get(self, slug):
        "Display a confirmation page before deleting"
        # check the url has a trailing slash and add it if not
        if self.request.path[-1] != "/":
            self.redirect("%s/" % self.request.path, True)
            return

        project = Project.all().filter('slug =', slug).fetch(1)[0]

        # if we don't have a user then throw
        # an unauthorised error
        user = users.get_current_user()
        if project.user == user or users.is_current_user_admin():
            owner = True
        else:
            self.render_403()
            return

        context = {
            'project': project,
            'owner': owner,
        }
        # calculate the template path
        output = self.render("project_delete.html", context)
        self.response.out.write(output)

    def post(self, slug):

        # if we don't have a user then throw
        # an unauthorised error
        user = users.get_current_user()
        if not user:
            self.render_403()
            return

        project = Project.all().filter('slug =', slug).fetch(1)[0]

        user = users.get_current_user()
        if project.user == user or users.is_current_user_admin():
            try:
                logging.info("project deleted: %s" % project.name)
                # delete the project
                project.delete()
            except Exception, e:
                logging.error("error deleting project: %s" % e)

        # just head back to the home page, which should list you projects
        self.redirect("/")


class ProjectSettingsHandler(BaseRequest):
    "Display and allowing editing a few per project settings"

    def get(self, slug):
        # make sure we have a trailing slash
        if self.request.path[-1] != "/":
            self.redirect("%s/" % self.request.path, True)
            return

        try:
            project = Project.all().filter('slug =', slug).fetch(1)[0]
        except IndexError:
            self.render_404()
            return

        user = users.get_current_user()

        # check we have the permissions to be looking at settings
        if project.user == user or users.is_current_user_admin():
            owner = True
        else:
            self.render_403()
            return

        context = {
            'project': project,
            'owner': owner,
        }
        # calculate the template path
        output = self.render("project_settings.html", context)
        self.response.out.write(output)

    def post(self, slug):

        # if we don't have a user then throw
        # an unauthorised error
        user = users.get_current_user()
        if not user:
            self.render_403()
            return

        user = users.get_current_user()

        project = Project.all().filter('slug =', slug).fetch(1)[0]

        if project.user == user:
            try:
                other_users = self.request.get("other_users")
                if other_users:
                    list_of_users = other_users.split(" ")
                    project.other_users = list_of_users
                else:
                    project.other_users = []

                if self.request.get("url"):
                    url = self.request.get("url")
                    if not url[:7] == 'http://':
                        url = "http://%s" % url
                    if URL_RE.match(url):
                        project.url = url
                else:
                    project.url = None

                if self.request.get("description"):
                    project.description = self.request.get("description")
                else:
                    project.description = None
                project.put()
                logging.info("project modified: %s" % project.name)
            except db.BadValueError, e:
                logging.error("error modifiying project: %s" % e)

        self.redirect('/projects/%s/settings/' % project.slug)


    # def post(self, project_slug, issue_slug):
    #
    #     # if we don't have a user then throw
    #     # an unauthorised error
    #     user = users.get_current_user()
    #     if not user:
    #         self.render_403()
    #         return
    #
    #     issue = Issue.all().filter('internal_url =', "/%s/%s/" % (
    #         project_slug, issue_slug)).fetch(1)[0]
    #
    #     user = users.get_current_user()
    #     if issue.project.user == user:
    #         try:
    #             logging.info("deleted issue: %s in %s" % (
    #                 issue.name, issue.project.name))
    #             issue.delete()
    #         except Exception, e:
    #             logging.error("error deleting issue: %s" % e)
    #         self.redirect("/projects/%s" % issue.project.slug)
    #     else:
    #         self.render_403()
    #         return
