from chigrin import artifacts
from chigrin import install

from nose.tools import assert_equals, assert_true
from chigrin.tests import utils

@utils.with_mockery
def test_artifact_should_request_installation_to_package_source(mockery):
    package_source = mockery.CreateMock(install.PackageSource)
    package_source.install('host.com',
                           {'package_name': 'liferay', 'version': '6.0.6'})
    mockery.ReplayAll()


    ins = install.Installer(package_source)
    result = ins.on_host('host.com', artifacts.Liferay(version='6.0.6'))

    assert_true(result.succeeded())

