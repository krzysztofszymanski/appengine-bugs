from google.appengine.api import users
from lib import BaseRequest
from models import Issue
from models import Comment
from service import *


class CommentsHandler(BaseRequest):
    def post(self, project_slug, issue_slug):
        # if we don't have a user then throw
        # an unauthorised error
        user = users.get_current_user()
        if not user:
            self.render_403()
            return
        service = Service()

        issue = Issue.all().filter('internal_url =', "/%s/%s/" % (
            project_slug, issue_slug)).fetch(1)[0]
        comment = self.request.get('comment')
        comment = Comment(issue=issue, comment=comment,
                          user=users.get_current_user().email())
        comment.put()
        service.send_comment_email(issue, comment)
        self.redirect("/projects{}".format(issue.internal_url))

