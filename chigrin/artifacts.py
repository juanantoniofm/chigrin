import copy
from chigrin import core

class Artifact(object):
    """An artifact is the basic installable unit.  A typical example
    of an artifact is a software package, but it could be almost
    anything.  In a more general sense, an artifact is a set of
    commands to be executed in a target host."""

    def install_on(self, host, package_source):
        """Install this artifact in the given HOST, using PACKAGE_SOURCE
        to get all necessary resources."""
        return NotImplemented

    def package_name(self):
        """Return the default package name for this artifact.  This
        value should be overridable by the user by supplying the
        `package' configuration parameter at construction time."""
        return self.__class__.__name__.lower()

class ArtifactError(core.ChigrinError):
    def __init__(self, message, cause=None):
        super(ArtifactError, self).__init__(message, cause)

class Liferay(Artifact):
    def __init__(self, **kwargs):
        self.parameters = self.__insert_defaults(kwargs)

    def __insert_defaults(self, parameters):
        params = copy.copy(parameters)
        if 'package' not in params:
            params['package'] = self.package_name()
        return params

    def install_on(self, host, package_source):
        return NotImplemented
