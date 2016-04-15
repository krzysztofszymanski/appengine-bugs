from google.appengine.api import users
from lib import BaseRequest
from service import *
from models import Issue
from google.appengine.ext.webapp import template

template.register_template_library('tags.br')

class IssueHandler(BaseRequest):

    def get(self, project_slug, issue_slug):
        if self.request.path[-1] != "/":
            self.redirect("%s/" % self.request.path, True)
            return

        user = users.get_current_user()

        if not user:
            self.redirect('/')

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

        output = self.render("issue.html", context)
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
        Service.update_issue_with_request_values(issue, self.request)
        issue.put()
        service = Service()
        if issue.fixed:
            service.send_fixed_email(issue)
        else:
            service.send_issue_updated_email(issue)

        self.redirect("/projects{}".format(issue.internal_url))
