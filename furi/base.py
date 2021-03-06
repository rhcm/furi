""" Base File Operations. """


import collections
import os
import re
import urlparse


MODES = 'r', 'rb', 'r+', 'rb+', 'w', 'wb', 'w+', 'wb+', 'a', 'ab', 'a+', 'ab+'


class File(collections.Iterable):
    """ Local File implentation.

        Exs. file:///abs/path/to/file.ext
             /abs/path/to/file.ext """

    modes = set(MODES)

    def __init__(self, uri, mode='r'):
        if mode not in self.modes and not set(mode).issubset(self.modes):
            raise ValueError("Cannot open %s in %s-mode" % (type(self).__name__, mode))
        self.uri  = urlparse.urlparse(uri)
        self.path = self.uri.path
        self.mode = mode
        self.workdir, self.filename = os.path.split(self.path)

    def __str__(self):
        return self.uri.geturl()

    def __repr__(self):
        return "<%s: %s>" % (type(self).__name__, str(self))

    def __iter__(self):
        return self.stream()

    def matches(self, pattern):
        """ Filename matches pattern.

            Arguments:
                pattern (regex or str):  Regular Expression to match.

            Returns:
                RegEx match object. """
        return re.compile(pattern).match(self.filename)

    def exists(self):
        """ Test file existence. """
        return os.path.exists(self.path)

    def read(self, *size):
        """ Read file stream. """
        return self.stream().read(*size)

    def write(self, stream):
        """ Write stream to file. """
        return self.stream().write(stream)

    def stream(self):
        """ Get file contents as stream. """
        try:
            return self._stream
        except AttributeError:
            if not self.exists() and 'w' not in self.mode:
                raise ValueError("%s does not exist" % self.uri.geturl())
            self._stream = self._stream_impl()
            return self._stream

    def _stream_impl(self):
        """ Implementation of stream(). """
        return open(self.path, self.mode)


class RemoteFile(File):
    """ Remote file implentation. """

    @property
    def connection(self):
        """ Remote connection. """
        try:
            return self._connection
        except AttributeError:
            self._connection = self.connect()
            return self._connection

    def connect(self, **kwargs):
        """ Connect to remote. """
        raise NotImplementedError

    def download(self, target):
        """ Download remote file to local target URI. """
        raise NotImplementedError

    def exists(self):
        """ Test file existence. """
        raise NotImplementedError

    def write(self, stream):
        """ Write stream to file. """
        raise NotImplementedError

    def _stream_impl(self):
        """ Implementation of stream(). """
        raise NotImplementedError
