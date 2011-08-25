import os
from chigrin import repository
from chigrin import core
from chigrin import artifacts
from chigrin import commands

# TODO: rename this class to InstallResult
class InstallErrors(object):
    def __init__(self, errors, success=False):
        self.errors = errors
        self.success = success

    def succeeded(self):
        return self.success

    def failed(self):
        return not self.succeeded()

class Installer(object):
    def __init__(self, *repositories):
        self.repositories = repositories

    def on_host(self, host, artifact):
        errors = []

        for repo in self.repositories:
            try:
                artifact.install_on(host, repo)
                return InstallErrors(errors, success=True)
            except artifacts.ArtifactError:
                raise
            except core.ChigrinError as e:
                errors.append((repo, e))

        return InstallErrors(errors)

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
                commands.fetch(uri, self.work_dir)

