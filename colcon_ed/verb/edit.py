# Copyright 2020 Chen Bainian
# Licensed under the Apache License, Version 2.0

import argparse

from colcon_core.package_discovery import add_package_discovery_arguments
from colcon_core.package_discovery import discover_packages
from colcon_core.package_identification \
    import get_package_identification_extensions
from colcon_core.plugin_system import satisfies_version
from colcon_core.verb import VerbExtensionPoint


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

        add_package_discovery_arguments(parser)

    def main(self, *, context):  # noqa: D102
        args = context.args
        extensions = get_package_identification_extensions()
        descriptors = discover_packages(args, extensions)
        for pkg in descriptors:
            if(pkg.name == args.package_name):
                print(str(pkg.path))


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
