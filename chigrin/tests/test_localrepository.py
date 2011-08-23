from chigrin.tests import utils

from nose.tools import assert_equal, raises

from chigrin.repository import UnknownOSError
from chigrin.repository import UnknownPackageError
from chigrin.repository import LocalRepository
from chigrin.repository import MetadataNotFoundError
from chigrin.repository import CorruptedMetadataError

repository = None

def setup_module():
    global repository
    repository = LocalRepository(utils.create_stub_repository(utils.TEST_PACKAGES))

def test_all_oses_returns_all_available_oses():
    assert_equal(['freebsd'], repository.all_oses())

@raises(UnknownOSError)
def test_querying_packages_from_unknown_os_raises_error():
    repository.all_packages(os='unknown')

def test_querying_packages_from_known_os_returns_all_available_packages():
    expected = [pkg['name'] for pkg in utils.TEST_PACKAGES]
    assert_equal(expected, repository.all_packages(os='freebsd'))

@raises(UnknownOSError)
def test_querying_in_a_unknown_os_raises_error():
    repository.package(os='unknown', package='simple-package')

@raises(UnknownPackageError)
def test_querying_an_unknown_package_raises_error():
    repository.package(os='freebsd', package='unknown')

def test_querying_a_known_package_returns_metadata():
    expected = utils.TEST_PACKAGES[0]['metadata']

    assert_equal(expected, repository.package(os='freebsd', package='simple-package'))

def test_a_simple_query_returns_all_versions():
    expected = utils.TEST_PACKAGES[1]['metadata']

    assert_equal(expected, repository.package(os='freebsd', package='versioned-package'))

def test_a_complex_query_returns_matching_versions():
    expected = utils.TEST_PACKAGES[1]['metadata'][:1]

    assert_equal(
        expected,
        repository.package(os='freebsd', package='versioned-package', version='1.0'))

@raises(CorruptedMetadataError)
def test_a_broken_package_with_empty_metadata_raises_error():
    repository.package(os='freebsd', package='broken-package-with-empty-metadata')

@raises(MetadataNotFoundError)
def test_a_broken_package_with_no_metadata_raises_error():
    repository.package(os='freebsd', package='broken-package-with-no-metadata')

@raises(CorruptedMetadataError)
def test_a_broken_package_with_garbage_in_metadata_raises_error():
    repository.package(os='freebsd', package='broken-package-with-garbage-in-metadata')
