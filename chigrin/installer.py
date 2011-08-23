from chigrin import repository

class InstallErrors(object):
    def __init__(self, errors, success=False):
        self.errors = errors
        self.success = success

    def succeeded(self):
        return self.success

    def failed(self):
        return not self.succeeded()

class Installer(object):
    def __init__(self, *repos):
        self.repositories = repos

    def on_host(self, host, artifact):
        errors = []

        for repo in self.repositories:
            try:
                artifact.install_on(host, repo)
                return InstallErrors(errors, success=True)
            except repository.ChigrinError as e:
                errors.append((repo, e))

        return InstallErrors(errors)

class PackageSource(object):
    def install(self, host, attributes):
        pass
