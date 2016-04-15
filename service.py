import re

from email_service import *

from google.appengine.api import users


class Service(object):
    """
    Service layer singleton
    """
    _instance = None

    def __init__(self):
        self.email_service = EmailService()
        pass

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(
                Service, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @staticmethod
    def update_issue_with_request_values(issue, request):

        name = request.get("name")
        description = request.get("description")
        assignee = request.get("assignee")
        fixed = request.get("fixed")
        fixed_description = request.get("fixed_description")
        watchers = request.get("watchers")
        if watchers:
            issue.watchers = []
            watchers_list = re.split(",| |\n", watchers)

            for watcher in watchers_list:
                watcher = watcher.strip()
                if watcher and watcher != '':
                    issue.watchers.append(watcher)
        else:
            issue.watchers = []

        issue.name = name
        issue.description = description
        if assignee:
            issue.assignee = assignee
        else:
            issue.assignee = None
        issue.fixed = bool(fixed)
        if fixed:
            issue.fixed_description = fixed_description
        else:
            issue.fixed_description = None
        return issue

    def to_emails(self, issue):
        to = [issue.assignee]
        if issue.watchers:
            to.extend(issue.watchers)

        user = users.get_current_user()
        to.append(user.email())
        return to

    def send_comment_email(self, issue, comment):

        body = "New comment for task:\n %s" \
               "\n%s" % (issue.name, comment.comment)

        to = self.to_emails(issue)
        if len(to):
            user = users.get_current_user()
            self.email_service.send_email(to,
                                          "New comment for %s" % issue.name,
                                          body)
        pass

    def send_issue_updated_email(self, issue):
        fixed_description = ""
        if issue.fixed_description:
            fixed_description = issue.fixed_description
        body = "Task updated:" \
               "\n name: %s" \
               "\n description: %s" % (issue.name,
                                       issue.description)
        to = self.to_emails(issue)

        if len(to):
            self.email_service.send_email(to,
                                          "Task updated: %s" % issue.name,
                                          body=body)

    def send_issue_created_email(self, issue):

        body = "New task created:" \
               "\nName: %s" \
               "\nDescription: %s" \
               "\nAssignee: %s" % (issue.name,
                                   issue.description,
                                   issue.assignee)
        to = self.to_emails(issue)

        if len(to):
            self.email_service.send_email(to,
                                          "Task created: %s" % issue.name,
                                          body=body)

    def send_fixed_email(self, issue):
        fixed_description = ""
        if issue.fixed_description:
            fixed_description = issue.fixed_description
        body = "Finished task:" \
               "\n Name: %s" \
               "\n Description: %s" \
               "\n Fix description: %s" % (issue.name,
                                         issue.description,
                                         fixed_description)
        to = self.to_emails(issue)

        if len(to):
            self.email_service.send_email(to,
                                          "Task finished: %s" % issue.name,
                                          body=body)
