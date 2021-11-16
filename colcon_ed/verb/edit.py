# Copyright 2020 Chen Bainian
# Licensed under the Apache License, Version 2.0

import argparse

from colcon_core.package_discovery import add_package_discovery_arguments
from colcon_core.plugin_system import satisfies_version
from colcon_core.verb import VerbExtensionPoint
from colcon_ed.edit_tools import edit_target_file
from colcon_ed.edit_tools import FileCompleter
from colcon_ed.edit_tools import find_file
from colcon_ed.edit_tools import get_package_path


class EditVerb(VerbExtensionPoint):
    """Edit a file within a package."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(VerbExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):  # noqa: D102
        parser.add_argument(
            'package_name', nargs='?', metavar='PKG_NAME',
            type=argument_package_name,
            help='Package name')

        args = parser.add_argument(
            'filename', nargs='?', metavar='FILE_NAME',
            type=argument_package_name,
            help='File name')
        args.completer = FileCompleter(package_name_key='package_name')

        add_package_discovery_arguments(parser)

    def main(self, *, context):  # noqa: D102
        args = context.args
        package_path = get_package_path(args.package_name, args)
        if not package_path:
            return (("Package '{args.package_name}' " +
                     'not found').format_map(locals()))

        file_paths = find_file(package_path, args.filename)
        if not file_paths:
            return (("File '{args.filename}' not found " +
                     'in package {args.package_name}').format_map(locals()))

        # Ask the user to choose when there are more than one file found
        if len(file_paths) > 1:
            msg = 'Multiple files found:'
            for i in range(len(file_paths)):
                msg += '\n ' + str(i + 1) + ') ' + file_paths[i]
            print(msg)
            try:
                index = input('Please enter a number: ')
                index = int(index) - 1
            except KeyboardInterrupt:
                return '\n'
            except ValueError:
                return 'Not an integer'
            if index < 0 or index >= len(file_paths):
                return 'Index out of range'
            path = file_paths[index]
        else:
            path = file_paths[0]

        return edit_target_file(path)


def argument_package_name(value):
    """
    Check if an argument is a valid package name.

    Used as a ``type`` callback in ``add_argument()`` calls.
    Package names starting with a dash must be prefixed with a space to avoid
    collisions with command line arguments.

    :param str value: The command line argument
    :returns: The package name
    :raises argparse.ArgumentTypeError: if the value starts with a dash
    """
    if value.startswith('-'):
        raise argparse.ArgumentTypeError('unrecognized argument: ' + value)
    return value.lstrip()
