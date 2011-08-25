import os

from fabric.api import local

def fetch(uri, destination):
    # TODO: implement OS detection.  Right not, this only works
    # with freebsd.
    local('fetch -o {0} {1}'.format(
            os.path.join(destination, os.path.basename(uri)), uri))
