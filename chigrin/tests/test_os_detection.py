from nose.tools import assert_equals, assert_true, assert_false, raises
from chigrin.tests import utils
import fabric
import mox

import chigrin
import chigrin.core

def test_localhost_is_detected_for_loopback():
    for hostname in ['localhost', '127.0.0.1']:
        assert_true(chigrin.core._is_localhost(hostname))

def test_external_host_is_not_localhost():
    assert_false(chigrin.core._is_localhost('www.google.com'))

def test_executor_factory_returns_local_executor_for_localhost():
    assert_equals(chigrin.core._executor_factory('localhost'), chigrin.core._local_executor)

def test_executor_factory_returns_remote_executor_for_remote_host():
    assert_equals(chigrin.core._executor_factory('www.google.com'), fabric.api.run)

@raises(chigrin.UnsupportedOSError)
def test_raises_error_when_no_os_installed_on_host():
    stub_efactory = lambda h: lambda c: None
    stub_oslister = lambda : []

    chigrin.detect_os('any.host.com', stub_efactory, stub_oslister)

@utils.with_mockery
def test_first_os_found_is_returned(mockery):
    class AlwaysFail(object):
        def installed_on(*args):
            raise ValueError

    not_installed = mockery.CreateMockAnything()
    installed = mockery.CreateMockAnything()

    executor = lambda _: None

    not_installed.installed_on('any.host.com', executor).AndReturn(False)
    installed.installed_on('any.host.com', executor).AndReturn(True)
    installed.__call__(executor)

    mockery.ReplayAll()

    chigrin.detect_os('any.host.com',
                      lambda _: executor,
                      lambda : [not_installed, installed, AlwaysFail()])
