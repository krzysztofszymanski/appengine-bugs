from datetime import datetime

from google.appengine.ext import db
from google.appengine.ext import search
from lib import slugify


class Project(db.Model):
    """Represents a single project"""
    name = db.StringProperty(required=True)
    url = db.LinkProperty()
    description = db.TextProperty()
    slug = db.StringProperty()
    created_date = db.DateTimeProperty(auto_now_add=True)
    user = db.UserProperty(required=True)
    other_users = db.StringListProperty()

    @property
    def open_issues(self):
        """Get a list of the open issues against this project"""
        return self.issue_set.filter('fixed =', False)

    @property
    def closed_issues(self):
        """Get a list of previously closed issues for this project"""
        return self.issue_set.filter('fixed =', True)

    def put(self):
        # we set the slug on the first save
        # after which it is never changed
        if not self.slug:
            self.slug = slugify(unicode(self.name))
        super(Project, self).put()


class Counter(db.Model):
    """Project specific counter"""
    count = db.IntegerProperty()
    project = db.ReferenceProperty(Project, required=True)

    # make it easy to retrieve the object based on key
    key_template = 'counter/%(project)s'


class Issue(search.SearchableModel):

    @staticmethod
    def issue_with_request(request):
        Issue()

    """Issue or bug representation"""
    name = db.StringProperty(required=True)
    project = db.ReferenceProperty(Project, required=True)

    description = db.TextProperty()
    created_date = db.DateTimeProperty(auto_now_add=True)
    email = db.EmailProperty()
    internal_url = db.StringProperty()
    fixed = db.BooleanProperty(default=False)
    fixed_date = db.DateTimeProperty()
    fixed_description = db.TextProperty()
    identifier = db.IntegerProperty()
    assignee = db.EmailProperty()
    watchers = db.StringListProperty()

    def put(self):
        # TODO: remove business logic from models
        # internal url is set on first save and then not changed
        # as the admin interface doesn't allow for changing name
        if not self.internal_url:
            slug = slugify(unicode(self.name))
            self.internal_url = "/%s/%s/" % (self.project.slug, slug)

        # each issue has a per project unique identifier which is based
        # on an integer. This integer is stored in counter in the datastore
        # which is associated with the project
        if not self.identifier:
            counter = Counter.get_by_key_name("counter/%s" % self.project.name)
            if counter is None:
                # if it's the first issue we need to create the counter
                counter = Counter(
                    key_name="counter/%s" % self.project.name,
                    project=self.project,
                    count=0,
                )
            # increment the count
            # FIXME: Needs fixing, unsafe.
            counter.count += 1
            counter.put()

            # save the count against the issue for use in the identifier
            self.identifier = counter.count

        # if the bug gets fixed then we store that date
        # if it's later marked as open we clear the date
        if self.fixed:
            self.fixed_date = datetime.now()
        else:
            self.fixed_date = None

        super(Issue, self).put()

    @property
    def comments(self):
        return self.comment_set.order('created_date')


class Comment(db.Model):
    comment = db.StringProperty(required=True, multiline=True)
    deleted = db.BooleanProperty()
    user = db.EmailProperty()
    created_date = db.DateTimeProperty(auto_now_add=True)
    issue = db.ReferenceProperty(Issue,
                                 required=True)