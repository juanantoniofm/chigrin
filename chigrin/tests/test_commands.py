from chigrin import commands
from chigrin.tests import utils
from nose.tools import assert_true, with_setup
import os
import shutil

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

@with_setup(cleanup_tmp_dirs)
def test_fetch_downloads_file():
    result = commands.fetch('http://www.google.com/robots.txt', '/tmp')

    assert_true(result.succeeded)
    utils.assert_file_exists('/tmp/robots.txt')

@with_setup(cleanup_tmp_dirs)
def test_touch_creates_file():
    commands.touch('/tmp/foo')

    utils.assert_file_exists('/tmp/foo')

@with_setup(cleanup_tmp_dirs)
def test_touch_updated_file_times():
    commands.touch('/tmp/foo')
    old_stat = os.stat('/tmp/foo')

    commands.touch('/tmp/foo')
    new_stat = os.stat('/tmp/foo')

    assert_true(new_stat.st_atime > old_stat.st_atime)
    assert_true(new_stat.st_mtime > old_stat.st_mtime)

@with_setup(cleanup_tmp_dirs)
def test_mv_fails_when_source_file_doesnt_exist():
    result = commands.mv('/tmp/foo', '/tmp/bar')

    assert_true(result.failed)

@with_setup(cleanup_tmp_dirs)
def test_mv_moves_files():
    commands.touch('/tmp/foo')
    result = commands.mv('/tmp/foo', '/tmp/bar')

    assert_true(result.succeeded)
    utils.assert_file_exists('/tmp/bar')

@with_setup(cleanup_tmp_dirs)
def test_mkdir_fails_if_directory_exists():
    commands.mkdir('/tmp/foo')
    result = commands.mkdir('/tmp/foo')

    assert_true(result.failed)

@with_setup(cleanup_tmp_dirs)
def test_mkdir_creates_directory():
    result = commands.mkdir('/tmp/foo')

    assert_true(result.succeeded)
    assert_true(os.path.exists('/tmp/foo'))

@with_setup(cleanup_tmp_dirs)
def test_unzip_works_on_zip_files():
    commands.fetch('https://github.com/downloads/adolfopa/chigrin/dummy-zip-file.zip', '/tmp')
    result = commands.unzip('/tmp/dummy-zip-file.zip', '/tmp/foo')

    assert_true(result.succeeded)
    utils.assert_file_exists('/tmp/foo/README.test')
