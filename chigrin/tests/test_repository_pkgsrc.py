import os

from chigrin.tests import utils
from nose.tools import assert_equals, assert_true, with_setup

from chigrin import repository
from chigrin import install

REPOSITORY_INFO = [
    {'os': 'freebsd',
     'name': 'robots',
     'metadata': [
            {'os': 'freebsd',
             'package': 'robots',
             'version': '1.0',
             'resources': ['http://www.python.org/robots.txt']}]}]

def cleanup_work_dir():
    """Make sure none of the files expected by the test assertions
    exist before test execution.  This is needed to guarantee that
    assertions fail when the package source is not able to downloaded
    all the files correcty."""

    try:
        os.remove('/tmp/robots.txt')
    except OSError as e:
        if e.errno != 2: # File not found
            raise

@with_setup(cleanup_work_dir)
def test_repository_package_source_should_download_files():
    """A RepositoryPackageSource should download all files with
    matching attributes into the host."""

    repo = repository.LocalRepository(utils.create_stub_repository(REPOSITORY_INFO))
    pkgsrc = install.RepositoryPackageSource(repo, '/tmp/')

    pkgsrc.install('localhost', {'os': 'freebsd', 'package': 'robots'})

    utils.assert_file_exists('/tmp/robots.txt')
