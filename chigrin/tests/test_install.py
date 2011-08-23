from chigrin import repository
from chigrin import artifacts
from chigrin.installer import Installer, InstallErrors

from chigrin.tests import utils
from nose.tools import assert_equals, assert_true

REPOSITORIES = [1, 2, 3] # anything with a sane __eq__ suffices.
HOST = 'host.com'

installer = None # initialized in `setup_module'.
package_source = None # same as above

def setup_module():
    global installer

    installer = Installer(*REPOSITORIES)
    
@utils.with_mockery
def test_installer_delegates_on_artifact_and_succeeds(mockery):
    artifact = mockery.CreateMock(artifacts.Artifact)
    artifact.install_on(HOST, REPOSITORIES[0])
    mockery.ReplayAll()

    assert_true(installer.on_host(HOST, artifact).succeeded())

@utils.with_mockery
def test_installer_tries_all_repos_in_order(mockery):
    artifact = mockery.CreateMock(artifacts.Artifact)

    artifact.install_on(HOST, REPOSITORIES[0]).AndRaise(repository.UnknownPackageError(None))
    artifact.install_on(HOST, REPOSITORIES[1]).AndRaise(repository.UnknownOSError(None))
    artifact.install_on(HOST, REPOSITORIES[2])

    mockery.ReplayAll()

    assert_true(installer.on_host(HOST, artifact).succeeded())
    
@utils.with_mockery
def test_installer_should_collect_all_errors(mockery):
    artifact = mockery.CreateMock(artifacts.Artifact)

    for repo in REPOSITORIES:
        artifact.install_on(HOST, repo).AndRaise(repository.UnknownPackageError(None))

    mockery.ReplayAll()

    result = installer.on_host(HOST, artifact)

    assert_true(result.failed())
    assert_equals(3, len(result.errors))
