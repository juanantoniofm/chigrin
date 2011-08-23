import json
import os as _os

class ChigrinError(Exception):
    """Base class for all errors raised in chigrin."""

    def __init__(self, cause):
        super(ChigrinError, self).__init__(cause)

class RepositoryError(ChigrinError):
    """Base class for all repository errors."""

    def __init__(self, cause):
        super(RepositoryError, self).__init__(cause)

class UnknownOSError(RepositoryError):
    """Error raised when a repository is queried for an unknown
    operating system."""

    def __init__(self, cause):
        super(UnknownOSError, self).__init__(cause)

class UnknownPackageError(RepositoryError):
    """Error raised when an operating system is queried for a
    non-existant package."""

    def __init__(self, cause):
        super(UnknownPackageError, self).__init__(cause)

class MetadataNotFoundError(RepositoryError):
    """Error raised when no metadata found for a package."""

    def __init__(self, cause):
        super(MetadataNotFoundError, self).__init__(cause)

class CorruptedMetadataError(RepositoryError):
    """Error raised when a package's metadata is corrupted."""

    def __init__(self, cause):
        super(CorruptedMetadataError, self).__init__(cause)
    
class Repository(object):
    """A repository maintains information about software packages.

    A repository supports the following operations:

    1. Querying for all available operating systems.  See the
    `all_oses' method for more information.

    2. Querying for all packages available for a given operating
    system.  See the `all_packages' method for further information.

    3. Querying for a package matching a criteria.  See the `package'
    method for more information.

    A package is a set of arbitrary key-value pairs, so looking up a
    package is, essentially, searching for a package with a matching
    set of key-value pairs.  The minimum required criteria to lookup a
    package is the operating system and the package name; the
    remaining key-value pairs should be given as keyword arguments to
    the `package' method.
    """

    def all_oses(self):
        """Returns the names of all available operating systems in the
        repository."""

        return NotImplemented

    def all_packages(self, os):
        """Returns the names of all packages available in the given
        operating system."""

        return NotImplemented

    def package(self, os, package, **kwargs):
        """Returns all versions of a package matching all keyword
        arguments."""

        return NotImplemented

class LocalRepository(Repository):
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
        super(Repository, self).__init__()
        self._root_path = root_path
        
    def all_oses(self):
        return _os.listdir(self._root_path)

    def all_packages(self, os):
        os_path = _os.path.join(self._root_path, os)
        if not _os.path.exists(os_path):
            raise UnknownOSError(None)
        else:
            return _os.listdir(os_path)

    def package(self, os, package, **kwargs):
        os_path = _os.path.join(self._root_path, os)

        if not _os.path.exists(os_path):
            raise UnknownOSError(None)

        package_path = _os.path.join(os_path, package)

        if not _os.path.exists(package_path):
            raise UnknownPackageError(
                "package {0}:{1} doesn't exist".format(os, package))

        metadata = _os.path.join(package_path, '.metadata')

        if not _os.path.exists(metadata):
            raise MetadataNotFoundError(
                '.metadata file not found for {0}:{1}:{2}'.format(
                    os, package, kwargs))

        with open(metadata) as data:
            return self._filter_matching_versions(
                self._deserialize(data, os, package, kwargs), kwargs)

    def _deserialize(self, data, os, package, kwargs):
        try:
            return json.load(data)
        except ValueError:
            # TODO: wrap original exception
            raise CorruptedMetadataError(
                'Corrupted .metadata found for {0}:{1}:{2}'.format(
                    os, package, kwargs))


    def _filter_matching_versions(self, versions, query):
        def contains_all_pairs(d1, d2):
            return all(k in d1 and d1[k] == v for (k, v) in d2.iteritems())

        return [version for version in versions
                if contains_all_pairs(version, query)]
