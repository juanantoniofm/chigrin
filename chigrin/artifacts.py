import copy

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
        `package_name' configuration parameter at construction time."""
        return self.__class__.__name__.lower()

class Liferay(Artifact):
    def __init__(self, **kwargs):
        self.parameters = self.__insert_defaults(kwargs)

    def __insert_defaults(self, parameters):
        params = copy.copy(parameters)
        if 'package_name' not in params:
            params['package_name'] = self.package_name()
        return params

    def install_on(self, host, package_source):
        package_source.install(host, self.parameters)
