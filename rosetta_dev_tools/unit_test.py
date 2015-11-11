#!/usr/bin/env python3

"""\
Compile and run a unit test.

Note that if you accidentally specify a test that doesn't exists, you'll get a 
rather cryptic error about an "unused free argument".  I think this happens 
because the CxxTest executable passes unrecognized arguments onto rosetta, and 
rosetta doesn't know what to do with it.

Usage:
    rdt_test [<alias>] [options]
    rdt_test <library> <suite> [<test>] [options]

Options:
    -s, --save-as <alias>       [default: repeat_previous]
        Save the specified library, suite, and test under the given alias so 
        you can quickly and easily rerun the same test in the future.

    -d, --gdb
        Run the unit test in the debugger.  Once the debugger starts, enter 'r' 
        to start running the test.

    -v, --verbose
        Output each command line that gets run, in case something needs to be 
        debugged.
"""

import sys, os
from . import helpers

def main():
    import docopt
    args = docopt.docopt(__doc__)

    if not args['<library>'] and not args['<alias>']:
        args['<alias>'] = 'repeat_previous'

    try:
        library, suite, test = pick_unit_test(
                library=args['<library>'],
                suite=args['<suite>'],
                test=args['<test>'],
                alias=args['<alias>'],
                save_as=args['--save-as'],
        )
        run_unit_test(
                library, suite, test,
                gdb=args['--gdb'],
                verbose=args['--verbose'],
        )
    except helpers.FatalBuildError as error:
        error.exit_gracefully()

def pick_unit_test(library, suite, test=None, alias=None, save_as=None):
    # Read the unit testing config file, which gives aliases to commonly used 
    # test settings.

    import configparser

    rosetta_path = helpers.find_rosetta_installation()
    config_path = os.path.join(rosetta_path, '.rdt_test.conf')

    config = configparser.ConfigParser()
    config.read(config_path)

    # If an alias is given, read the library, suite, and test settings from the 
    # config file.  Complain if the given alias is not in the config file.

    if alias is not None:
        try:
            library = config[alias]['library']
            suite = config[alias]['suite']
            test = config[alias].get('test')
        except KeyError:
            raise BadAliasError(alias)

    # If a "Save As" alias is given, save the library, suite, and test settings 
    # under that alias.

    if save_as is not None:
        if save_as not in config:
            config.add_section(save_as)

        config[save_as]['library'] = library
        config[save_as]['suite'] = suite
        if test is not None:
            config[save_as]['test'] = test

        with open(config_path, 'w') as file:
            config.write(file)

    return library, suite, test

def run_unit_test(library, suite, test=None, gdb=False, verbose=False):
    # Compile the unit test.

    from .build import build_rosetta

    error_code = build_rosetta(
            'debug', library + '.test',
            verbose=verbose,
    )
    if error_code:
        sys.exit(error_code)

    # Run the unit test.

    unit_test_cmd = ()
    unit_test_dir = os.path.join(
            helpers.find_rosetta_installation(),
            'source', 'cmake', 'build_debug')
    if gdb:
        unit_test_cmd += 'gdb', '--args'
    
    # The "-mute all" argument is actually critically important because it 
    # covers up a bug in core_init().  If only one argument is passed the unit 
    # test script, core_init() tries to add "-mute all" and ends up failing, I 
    # think because it gets $0 wrong.

    unit_test_cmd += './{}.test'.format(library), suite,
    if test is not None: unit_test_cmd += test,
    unit_test_cmd += '-unmute' if verbose else '-mute', 'all'

    helpers.shell_command(
            unit_test_dir, unit_test_cmd, check=False, verbose=verbose)


class BadAliasError(helpers.FatalBuildError):
    exit_status = 1
    exit_message = "No such alias '{0}'."

    def __init__(self, alias):
        super().__init__(alias)



