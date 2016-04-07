from models import *


class Dao(object):
    """
    Dao singleton
    """
    _instance = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(
                Dao, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def get_issues_for_project(self, project, status):
        issues = Issue.all().filter('project =', project)
        if status != '':
            if "open" == status:
                issues = issues.filter('fixed =', False)
            if "closed" == status:
                issues = issues.filter('fixed =', True)
        else:
            issues = issues.filter('fixed =', False)
        issues = issues.order('fixed').order('created_date')
        return issues

    def get_issues_for_user(self, user, status):
        issues = Issue.all().filter('assignee =', user)

        if status != '':
            if "open" == status:
                issues = issues.filter('fixed =', False)
            if "closed" == status:
                issues = issues.filter('fixed =', True)
        else:
            issues = issues.filter('fixed =', False)
        issues = issues.order('fixed').order('created_date')
        return issues