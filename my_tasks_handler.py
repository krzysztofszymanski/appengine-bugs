from google.appengine.api import users
from lib import BaseRequest
from dao import *


class MyTasksHandler(BaseRequest):
    def __init__(self, a, b):
        BaseRequest.__init__(self, a, b)
        self.dao = Dao()

    def get(self):
        if self.request.path[-1] != "/":
            self.redirect("%s/" % self.request.path, True)
            return

        user = users.get_current_user()
        status = self.request.get("status")
        if not user:
            self.redirect('/')

        try:
            issues = self.dao.get_issues_for_user(user.email(), status)

        except IndexError:
            self.render_404()
            return

        context = {
            'issues': issues,
            'owner': user.email,
        }
        output = self.render("my-tasks.html", context)
        self.response.out.write(output)

