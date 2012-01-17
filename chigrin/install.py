import collections
import os

from chigrin import repository
from chigrin import core
from chigrin import artifacts
from chigrin import commands

InstallResult = collections.namedtuple('InstallResult', ['succeeded', 'failed', 'errors'])

class Installer(object):
    def __init__(self, *repositories):
        self.repositories = repositories

    def on_host(self, host, artifact):
        errors = []

        for repo in self.repositories:
            try:
                artifact.install_on(host, repo)
                return InstallResult(True, False, errors)
            except artifacts.ArtifactError:
                raise
            except core.ChigrinError as e:
                errors.append((repo, e))

        return InstallResult(False, True, errors)

class PackageSource(object):
    def install(self, host, attributes):
        return NotImplemented

class RepositoryPackageSource(PackageSource):
    def __init__(self, repository, work_dir):
        self.repository = repository
        self.work_dir = work_dir

    def install(self, host, attributes):
        for p in self.repository.package(**attributes):
            for uri in p['resources']:
                commands.fetch(uri, self.work_dir, host=host)

