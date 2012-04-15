import chigrin.core
from fabric.api import run, local
from fabric.context_managers import settings
import functools
import os
import socket

class OS(object):
    def __init__(self, executor):
        self._execute = executor

    def _cmd(self, fmt, *args):
        return self._execute(fmt.format(*args))

    def _do_fetch(self, cmd_template, uri, destination):
        filename = os.path.basename(uri)
        out_file = os.path.join(destination, filename)

        return self._cmd(cmd_template, out_file, uri)

    def fetch(self, uri, destination):
        return NotImplemented

    def unzip(self, zip_file, target_dir, flags=''):
        return self._cmd('unzip {0} {1} -d {2}', flags, zip_file, target_dir)

    def mv(self, source, destination):
        return self._cmd('mv {0} {1}', source, destination)

    def mkdir(self, dirname):
        return self._cmd('mkdir {0}', dirname)

    def touch(self, filename):
        return self._cmd('touch {0}', filename)            

class FreeBSD(OS):
    def fetch(self, uri, destination):
        return self._do_fetch('fetch -o {0} {1}', uri, destination)

    @staticmethod
    def installed_on(_, executor):
        return executor('uname -a').find('FreeBSD') != -1

class Ubuntu(OS):
    def fetch(self, uri, destination):
        return self._do_fetch('wget -O {0} {1}', uri, destination)

    @staticmethod
    def installed_on(_, executor):
        return executor('uname -a').find('Ubuntu') != -1

def is_localhost(host):
    return socket.gethostbyname(host) == '127.0.0.1'

local_executor = functools.partial(local, capture=True)

def executor_factory(host):
    return local_executor if host == None or is_localhost(host) else run

def available_oses():
    found = []
    pending = [OS]

    while pending:
        cls = pending.pop()
        for os in cls.__subclasses__():
            if os not in found:
                found.append(os)
            pending.append(os)

    return found

class UnsupportedOSError(chigrin.core.ChigrinError):
    pass

def detect_os(host, executor_factory=executor_factory, available_oses=available_oses):
    executor = executor_factory(host)

    for os in available_oses():
        if os.installed_on(host, executor):
            return os(executor)

    raise UnsupportedOSError(
        'No supported operating system found at {0}'.format(host))

def execute(host, fn):
    env = { 'warn_only': True }

    if host:
        env['host_string'] = host

    with settings(**env):
        return fn(detect_os(host))

def fetch(uri, destination, host=None):
    return execute(host, lambda os: os.fetch(uri, destination))

def unzip(zip_file, target_dir, flags='', host=None):
    return execute(host, lambda os: os.unzip(zip_file, target_dir, flags))

def mv(source, destination, host=None):
    return execute(host, lambda os: os.mv(source, destination))

def mkdir(dirname, host=None):
    return execute(host, lambda os: os.mkdir(dirname))

def touch(filename, host=None):
    return execute(host, lambda os: os.touch(filename))
