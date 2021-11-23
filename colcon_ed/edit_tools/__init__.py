# Copyright 2020 Chen Bainian
# Licensed under the Apache License, Version 2.0

import os
import subprocess

from colcon_core.package_discovery import discover_packages
from colcon_core.package_identification \
    import get_package_identification_extensions


def get_package_path(package_name, args):
    """
    Get the relative package path.

    Use the `package_discovery` extension to find package path.

    :param str package_name: The name of the package to find path
    :param args: The positional arguments to `add_argument()`
    :returns: The package path or None
    """
    extensions = get_package_identification_extensions()
    descriptors = discover_packages(args, extensions)
    package_path = ''
    for pkg in descriptors:
        if(pkg.name == args.package_name):
            package_path = pkg.path
    return package_path


def find_all_files(package_path):
    """
    Get all the files within the path given.

    Ignore certain files like hidden files and `.pyc` files.

    :param str package_path: The relative path
    :return: a list of relative paths of all the files
    """
    paths = []
    for dirpath, dirnames, filenames in os.walk(package_path):
        # ignore folder starting with .
        dirnames[:] = [d for d in dirnames if not d[0] == '.']

        # ignore hidden files and those ending with .pyc
        filenames = [f for f in filenames
                     if f[0] != '.' and f[-4:] != '.pyc']

        for name in filenames:
            paths.append(os.path.join(dirpath, name))

    return paths


def find_file(package_path, filename):
    """
    Get all the files with the same filename in the path given.

    :param str package_path: The relative path
    :param str filename: The filenames to search for
    :return: a list of relative paths
    """
    paths = []
    all_paths = find_all_files(package_path)
    for path in all_paths:
        if filename == os.path.basename(path):
            paths.append(path)
    return paths


def edit_target_file(path):
    """
    Edit the target file given by the path.

    if the `EDITOR` environment variable is set, a command
    `$EDITOR <filename>` will be called. Otherwise, if `EDITOR`
    is not set or set to empty, `vim` will be use by default

    :param str path: The path of the file to be edited
    :return: process return code
    """
    editor = os.environ.get('EDITOR', 'vim')
    if not editor:
        editor = 'vim'
    process = subprocess.Popen([editor, path],
                               shell=(os.name == 'nt'))
    while process.returncode is None:
        try:
            process.communicate()
        except KeyboardInterrupt:
            pass
    return process.returncode


class FileCompleter:
    """Callable returning a list of file names within a package."""

    def __init__(self, *, package_name_key=None): # noqa D107
        self.package_name_key = package_name_key

    def __call__(self, prefix, parsed_args, **kwargs): # noqa D102
        package_name = parsed_args.package_name
        if not package_name:
            return []
        path = get_package_path(package_name, parsed_args)
        if not path:
            return []

        return [os.path.basename(file_path)
                for file_path in find_all_files(path)]
