import os
import tempfile
import json
import mox
from functools import wraps

TEST_PACKAGES = [
    {'os': 'freebsd',
     'name': 'simple-package',
     'metadata': [
            {'os': 'freebsd',
             'package': 'simple-package',
             'version': '1.0',
             'resources': [ '/freebsd/simple-package/resource-1.0.tar.gz' ]}]},
    {'os': 'freebsd',
     'name': 'versioned-package',
     'metadata': [
            {'os': 'freebsd',
             'package': 'versioned-package',
             'version': '1.0',
             'resources': [ '/freebsd/versioned-package/resource-1.0.tar.gz' ]},
            {'os': 'freebsd',
             'package': 'versioned-package',
             'version': '1.1',
             'resources': [ '/freebsd/versioned-package/resource-1.1.tar.gz' ]}]},
    {'os': 'freebsd',
     'name': 'broken-package-with-no-metadata',
     'metadata': None },
    {'os': 'freebsd',
     'name': 'broken-package-with-empty-metadata',
     'metadata': ''},
    {'os': 'freebsd',
     'name': 'broken-package-with-garbage-in-metadata',
     'metadata': '%%%!# zdla ~~2123'}]

def create_file(fname, contents=None):
    """Creates the `fname' file with the given contents.  If
    `contents' is a false value (except None), it will touch the
    file."""
    if contents is not None:
        with open(fname, 'w') as f:
            if not contents:
                os.utime(fname, None)
            else:
                f.write(contents)

def create_stub_repository(repository_data):
    """Creates a stub repository in a temporal directory."""
    tmpdir = tempfile.mkdtemp()

    for package in repository_data:
        dirname = os.path.join(tmpdir, package['os'], package['name'])
        os.makedirs(dirname)
        
        metadata = package['metadata']

        if isinstance(metadata, list):
            metadata = json.dumps(metadata)

        create_file(os.path.join(dirname, '.metadata'), metadata)

    return tmpdir

def with_mockery(test_fn):
    @wraps(test_fn)
    def wrapper():
        mockery = mox.Mox()
        test_fn(mockery)
        mockery.VerifyAll()

    return wrapper
