from chigrin import repository
from chigrin import artifacts
from chigrin import install

from chigrin.tests import utils
from nose.tools import assert_equals, assert_true

PACKAGE_SOURCES = [1, 2, 3] # anything with a sane __eq__ suffices.
HOST = 'host.com'

installer = None # initialized in `setup_module'.

def setup_module():
    global installer

    installer = install.Installer(*PACKAGE_SOURCES)
    
@utils.with_mockery
def test_installer_delegates_on_artifact_and_succeeds(mockery):
    artifact = mockery.CreateMock(artifacts.Artifact)
    artifact.install_on(HOST, PACKAGE_SOURCES[0])
    mockery.ReplayAll()

    assert_true(installer.on_host(HOST, artifact).succeeded())

@utils.with_mockery
def test_installer_tries_all_repos_in_order(mockery):
    artifact = mockery.CreateMock(artifacts.Artifact)

    artifact.install_on(HOST, PACKAGE_SOURCES[0]).AndRaise(repository.UnknownPackageError(None))
    artifact.install_on(HOST, PACKAGE_SOURCES[1]).AndRaise(repository.UnknownOSError(None))
    artifact.install_on(HOST, PACKAGE_SOURCES[2])

    mockery.ReplayAll()

    assert_true(installer.on_host(HOST, artifact).succeeded())
    
@utils.with_mockery
def test_installer_should_collect_all_errors(mockery):
    artifact = mockery.CreateMock(artifacts.Artifact)

    for repo in PACKAGE_SOURCES:
        artifact.install_on(HOST, repo).AndRaise(repository.UnknownPackageError(None))

    mockery.ReplayAll()

    result = installer.on_host(HOST, artifact)

    assert_true(result.failed())
    assert_equals(3, len(result.errors))
