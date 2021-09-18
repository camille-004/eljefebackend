"""
Google Cloud Datastore helpers.
"""
from django.conf import settings
from django.test.runner import DiscoverRunner

# For running emulator in development mode
from google.auth.credentials import AnonymousCredentials
from google.cloud import ndb


def get_client():
    """Create and return a Datastore client."""
    if settings.IS_GAE:
        # If running Google App Engine, return NDB client with namespace from
        # settings
        return ndb.Client(namespace=settings.DATASTORE_NAMESPACE)
    
    # In development mode, specify credentials and project as well
    return ndb.Client(
        credentials=AnonymousCredentials(),
        project=settings.GOOGLE_CLOUD_PROJECT,
        namespace=settings.DATASTORE_NAMESPACE,
    )


class NDBMiddleware:
    """Middleware for handling NDB context."""

    def __init__(self, get_response):
        """Create client."""
        self.get_response = get_response
        self.client = get_client()

    def __call__(self, request):
        """Create a context using context() method from client."""
        context = self.client.context()
        request.ndb_context = context
        with context:
            response = self.get_response(request)

        return response


class TestRunner(DiscoverRunner):
    """A test suite runner that uses Datastore."""

    def setup_database(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass
