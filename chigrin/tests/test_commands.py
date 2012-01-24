from chigrin import commands
from chigrin.tests import utils
from nose.tools import assert_true
import os

def test_fetch_downloads_file():
    result = commands.fetch('http://www.google.com/robots.txt', '/tmp')

    assert_true(result.succeeded)
    utils.assert_file_exists('/tmp')

def remove(filename):
    if os.path.exists(filename):
        if os.path.isdir(filename):
            os.rmdir(filename)
        else:
            os.remove(filename)

def test_touch_creates_file():
    remove('/tmp/foo')

    commands.touch('/tmp/foo')

    utils.assert_file_exists('/tmp/foo')

def test_touch_updated_file_times():
    remove('/tmp/foo')

    commands.touch('/tmp/foo')

    old_stat = os.stat('/tmp/foo')

    commands.touch('/tmp/foo')

    new_stat = os.stat('/tmp/foo')

    assert_true(new_stat.st_atime > old_stat.st_atime)
    assert_true(new_stat.st_mtime > old_stat.st_mtime)

def test_mv_fails_when_source_file_doesnt_exist():
    remove('/tmp/foo')

    result = commands.mv('/tmp/foo', '/tmp/bar')

    assert_true(result.failed)

def test_mv_moves_files():
    remove('/tmp/foo')
    commands.touch('/tmp/foo')
    result = commands.mv('/tmp/foo', '/tmp/bar')

    assert_true(result.succeeded)

def test_mkdir_fails_if_directory_exists():
    remove('/tmp/foo')

    commands.mkdir('/tmp/foo')
    result = commands.mkdir('/tmp/foo')

    assert_true(result.failed)

def test_mkdir_creates_directory():
    remove('/tmp/foo')

    assert not os.path.exists('/tmp/foo')

    result = commands.mkdir('/tmp/foo')

    assert_true(result.succeeded)
    assert_true(os.path.exists('/tmp/foo'))

def test_unzip_works_on_zip_files():
    commands.fetch('https://github.com/downloads/adolfopa/chigrin/dummy-zip-file.zip', '/tmp')
    result = commands.unzip('/tmp/dummy-zip-file.zip', '/tmp/master_output')

    utils.assert_file_exists('/tmp/master_output/README.test')
