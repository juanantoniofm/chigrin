import chigrin
from chigrin.tests import utils
from nose.tools import assert_true, with_setup
import contextlib
import functools
import os
import shutil

def test_proxy_delegates_all_methods():
    class Dummy(object):
        def foo(self, a):
            return a
            
    proxy = chigrin.Proxy('localhost', Dummy())
    assert_true(proxy.foo(True))

def test_proxy_updates_settings_with_given_host():
    class Dummy(object):
        def foo(self):
            pass

    state = {}

    @contextlib.contextmanager
    def stub_settings(*args, **kwargs):
        state.update(kwargs)
        yield

    proxy = chigrin.Proxy('frobboz.com', Dummy(), settings=stub_settings)
    proxy.foo()

    assert_true(state['host_string'] == 'frobboz.com')

def cleanup_tmp_dirs():
    def remove(filename):
        if os.path.exists(filename):
            if os.path.isdir(filename):
                shutil.rmtree(filename)
            else:
                os.remove(filename)

    remove('/tmp/foo')
    remove('/tmp/bar')
    remove('/tmp/robots.txt')
    remove('/tmp/dummy-zip-file.zip')

def using_host(host):
    def decorator(f):
        @functools.wraps(f)
        def wrapper():
            return f(chigrin.detect_os(host))
        return wrapper
    return decorator

@with_setup(cleanup_tmp_dirs)
@using_host('localhost')
def test_fetch_downloads_file(host):
    result = host.fetch('http://www.google.com/robots.txt', '/tmp')

    assert_true(result.succeeded)
    utils.assert_file_exists('/tmp/robots.txt')

@with_setup(cleanup_tmp_dirs)
@using_host('localhost')
def test_touch_creates_file(host):
    host.touch('/tmp/foo')

    utils.assert_file_exists('/tmp/foo')

@with_setup(cleanup_tmp_dirs)
@using_host('localhost')
def test_touch_updated_file_times(host):
    host.touch('/tmp/foo')
    old_stat = os.stat('/tmp/foo')

    host.touch('/tmp/foo')
    new_stat = os.stat('/tmp/foo')

    assert_true(new_stat.st_atime > old_stat.st_atime)
    assert_true(new_stat.st_mtime > old_stat.st_mtime)

@with_setup(cleanup_tmp_dirs)
@using_host('localhost')
def test_mv_fails_when_source_file_doesnt_exist(host):
    result = host.mv('/tmp/foo', '/tmp/bar')

    assert_true(result.failed)

@with_setup(cleanup_tmp_dirs)
@using_host('localhost')
def test_mv_moves_files(host):
    host.touch('/tmp/foo')
    result = host.mv('/tmp/foo', '/tmp/bar')

    assert_true(result.succeeded)
    utils.assert_file_exists('/tmp/bar')

@with_setup(cleanup_tmp_dirs)
@using_host('localhost')
def test_mkdir_fails_if_directory_exists(host):
    host.mkdir('/tmp/foo')
    result = host.mkdir('/tmp/foo')

    assert_true(result.failed)

@with_setup(cleanup_tmp_dirs)
@using_host('localhost')
def test_mkdir_creates_directory(host):
    result = host.mkdir('/tmp/foo')

    assert_true(result.succeeded)
    assert_true(os.path.exists('/tmp/foo'))

@with_setup(cleanup_tmp_dirs)
@using_host('localhost')
def test_unzip_works_on_zip_files(host):
    host.fetch('https://github.com/downloads/adolfopa/chigrin/dummy-zip-file.zip', '/tmp')
    result = host.unzip('/tmp/dummy-zip-file.zip', '/tmp/foo')

    assert_true(result.succeeded)
    utils.assert_file_exists('/tmp/foo/README.test')
