from fabric.api import run, local, env
from fabric.context_managers import settings
import functools
import json
import os
import socket

class ChigrinError(Exception):
    """Base class for all errors raised in chigrin."""

    def __init__(self, message, cause=None):
        super(ChigrinError, self).__init__((message, cause))



class RepositoryError(ChigrinError):
    """Base class for all repository errors."""

    def __init__(self, message, cause=None):
        super(RepositoryError, self).__init__(message, cause)

class UnknownOSError(RepositoryError):
    """Error raised when a repository is queried for an unknown
    operating system."""

    def __init__(self, message, cause=None):
        super(UnknownOSError, self).__init__(message, cause)

class UnknownPackageError(RepositoryError):
    """Error raised when an operating system is queried for a
    non-existant package."""

    def __init__(self, message, cause=None):
        super(UnknownPackageError, self).__init__(message, cause)

class MetadataNotFoundError(RepositoryError):
    """Error raised when no metadata found for a package."""

    def __init__(self, message, cause=None):
        super(MetadataNotFoundError, self).__init__(message, cause)

class CorruptedMetadataError(RepositoryError):
    """Error raised when a package's metadata is corrupted."""

    def __init__(self, message, cause=None):
        super(CorruptedMetadataError, self).__init__(message, cause)
    
# A repository maintains information about software packages.
#
# A repository supports the following operations:
#
#     1. Querying for all available operating systems.  See the
#     `all_oses' method for more information.
#
#     2. Querying for all packages available for a given operating
#     system.  See the `all_packages' method for further information.
#
#     3. Querying for a package matching a criteria.  See the `package'
#     method for more information.
#
#     A package is a set of arbitrary key-value pairs, so looking up a
#     package is, essentially, searching for a package with a matching
#     set of key-value pairs.  The minimum required criteria to lookup a
#     package is the operating system and the package name; the
#     remaining key-value pairs should be given as keyword arguments to
#     the `package' method.

class LocalRepository(object):
    """A local repository is a repository residing in the local
    filesystem.

    The structure of a local repository in the fs is as follows:

    1. There a root directory, where all repository info hangs
    from.

    2. In the root directory there is a directory for each supported
    operating system.  The name of the directory is the operating
    system id.

    3. In each os directory, there is a directory for each package.
    The name of these directories are the package identifiers.

    4. In each package directory there is a `.metadata' file.  This
    file contains all information about the package serialized as a
    JSON object.

    The package metadata file has the following form:

        [ version1, version2, ..., versionN ]

    that is, the package metadata is a sequence of version objects.
    Each version is a JSON object wich defines the set of key value
    pairs for that version.  These are the key-value pairs matched by
    the `package' method."""

    def __init__(self, root_path):
        self._root_path = root_path
        
    def all_oses(self):
        return os.listdir(self._root_path)

    def all_packages(self, platform):
        os_path = os.path.join(self._root_path, platform)
        if not os.path.exists(os_path):
            raise UnknownOSError(
                "This repository doesn't support the OS '{0}'".format(platform))
        else:
            return os.listdir(os_path)

    def package(self, platform, package, **kwargs):
        os_path = os.path.join(self._root_path, platform)

        if not os.path.exists(os_path):
            raise UnknownOSError(
                "This repository doesn't support the OS '{0}'".format(platform))

        package_path = os.path.join(os_path, package)

        if not os.path.exists(package_path):
            raise UnknownPackageError(
                "package {0}:{1} doesn't exist in the repository".format(
                    platform, package))

        metadata = os.path.join(package_path, '.metadata')

        if not os.path.exists(metadata):
            raise MetadataNotFoundError(
                '.metadata file not found for {0}:{1}:{2}'.format(
                    platform, package, kwargs))

        with open(metadata) as data:
            return self._filter_matching_versions(
                self._deserialize(data, platform, package, kwargs), kwargs)

    def _deserialize(self, data, platform, package, kwargs):
        try:
            return json.load(data)
        except ValueError as e:
            raise CorruptedMetadataError(
                'Corrupted .metadata found for {0}:{1}:{2}'.format(
                    platform, package, kwargs), e)

    def _filter_matching_versions(self, versions, query):
        def contains_all_pairs(d1, d2):
            return all(k in d1 and d1[k] == v for (k, v) in d2.iteritems())

        return [version for version in versions
                if contains_all_pairs(version, query)]
        



class OS(object):
    def __init__(self, execute):
        self._execute = execute

    def _cmd(self, fmt, *args):
        return self._execute(fmt.format(*args))

    def _do_fetch(self, cmd_template, uri, destination):
        filename = os.path.basename(uri)
        out_file = os.path.join(destination, filename)

        return self._cmd(cmd_template, out_file, uri)

    def fetch(self, uri, destination):
        raise NotImplementedError

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

class Proxy(object):
    def __init__(self, host, target, settings=settings):
        self._host = host
        self._target = target
        self._settings = settings

    def __getattr__(self, name):
        env = { 'warn_only': True }

        if self._host:
            env['host_string'] = self._host

        original_method = getattr(self._target, name)

        @functools.wraps(original_method)
        def wrapper(*args, **kwargs):
            with self._settings(**env):
                return original_method(*args, **kwargs)

        return wrapper

def _is_localhost(host):
    return socket.gethostbyname(host) == '127.0.0.1'

_local_executor = functools.partial(local, capture=True)

def _executor_factory(host):
    return _local_executor if host == None or _is_localhost(host) else run

def _available_oses():
    found = []
    pending = [OS]

    while pending:
        cls = pending.pop()
        for os in cls.__subclasses__():
            if os not in found:
                found.append(os)
            pending.append(os)

    return found

class UnsupportedOSError(ChigrinError):
    pass

def detect_os(host, executor_factory=_executor_factory, available_oses=_available_oses):
    executor = executor_factory(host)

    for os in available_oses():
        if os.installed_on(host, executor):
            return Proxy(host, os(executor))

    raise UnsupportedOSError(
        'No supported operating system found at {0}'.format(host))
