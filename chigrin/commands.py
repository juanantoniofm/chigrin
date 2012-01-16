import os

from fabric.api import run, local
from fabric.context_managers import settings
from contextlib import contextmanager

class OS(object):
    def fetch(self, uri, destination):
        return NotImplemented

def executable(cls):
    def cons(executor):
        instance = cls()
        instance.execute = executor
        return instance

    return cons

@executable
class FreeBSD(OS):
    def fetch(self, uri, destination):
        self.execute('fetch -o {0} {1}'.format(
                os.path.join(destination, os.path.basename(uri)), uri))

@executable
class Ubuntu(OS):
    def fetch(self, uri, destination):
        self.execute('wget -O {0} {1}'.format(
                os.path.join(destination, os.path.basename(uri)), uri))

def is_localhost(host):
    return host == 'localhost' or host == '127.0.0.1'

def detect_os(host):
    executor = local if is_localhost(host) else run

    uname = executor('uname -a')

    if uname.find('Ubuntu') != -1:
        return Ubuntu(executor)
    elif uname.contains('FreeBSD') != -1:
        return FreeBSD(executor)
    else:
        raise ValueError # TODO: pick a more specific exception

@contextmanager
def machine(host):
    if is_localhost(host):
        yield
    else:
        with settings(host_string=host):
            yield

def execute(host, fn):
    with machine(host):
        fn(detect_os(host))
    
def fetch(uri, destination, host):
    execute(host, lambda os: os.fetch(uri, destination))
