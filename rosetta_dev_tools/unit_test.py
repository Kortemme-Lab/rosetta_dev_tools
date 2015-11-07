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
    rdt_test --new <library> <namespace> <suite>

Options:
    -s, --save-as <alias>       [default: repeat_previous]
        Save the specified library, suite, and test under the given alias so 
        you can quickly and easily rerun the same test in the future.

    -d, --gdb
        Run the unit test in the debugger.  Once the debugger starts, enter 'r' 
        to start running the test.

    -u, --update
        Before compiling the unit test, run CMake to account for source files 
        that have been added or removed.

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
        if args['--new']:
            make_new_unit_test(
                    library=args['<library>'],
                    namespace=args['<namespace>'],
                    suite=args['<suite>'],
            )
        else:
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
                    update=args['--update'],
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

def run_unit_test(library, suite, test=None, gdb=False, update=False, verbose=False):
    # Compile the unit test.

    from .build import build_rosetta

    error_code = build_rosetta(
            'debug', library + '.test',
            update=update,
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
    
    unit_test_cmd += './{}.test'.format(library), suite

    if test is not None:
        unit_test_cmd += test,

    helpers.shell_command(
            unit_test_dir, unit_test_cmd, check=False, verbose=verbose)

def make_new_unit_test(library, namespace, suite):
    # Construct a string containing the dummy unit test.

    test_name = [library] + namespace.split('/') + [suite]
    rosetta_dir = helpers.find_rosetta_installation()
    cxxtest_dir = os.path.join(
            rosetta_dir, 'source', 'test', *test_name[:-1])
    cxxtest_path = os.path.join(
            cxxtest_dir, suite + '.cxxtest.hh')
    include_guard = '_'.join(test_name)
    cxxtest_template = """\
// -*- mode:c++;tab-width:2;indent-tabs-mode:t;show-trailing-whitespace:t;rm-trailing-spaces:t -*-
// vi: set ts=2 noet:
//
// (c) Copyright Rosetta Commons Member Institutions.
// (c) This file is part of the Rosetta software suite and is made available under license.
// (c) The Rosetta software is developed by the contributing members of the Rosetta Commons.
// (c) For more information, see http://www.rosettacommons.org. Questions about this can be
// (c) addressed to University of Washington UW TechTransfer, email: license@u.washington.edu.

#ifndef INCLUDED_{include_guard}_CXXTEST_HH
#define INCLUDED_{include_guard}_CXXTEST_HH

// Test headers
#include <cxxtest/TestSuite.h>
#include <test/core/init_util.hh>

// C++ headers
#include <iostream>

using namespace std;

class {suite} : public CxxTest::TestSuite {{ # (no fold)

public:

	void setUp() {{
		core_init();
	}}

	void test_hello_world() {{
		cout << "Hello world!" << endl;
	}}

}};

#endif
""".replace(' # (no fold)', '')

    # Write the dummy unit test to a file.

    os.makedirs(cxxtest_dir, exist_ok=True)
    with open(cxxtest_path, 'w') as file:
        file.write(cxxtest_template.format(**locals()))

    # Instruct the user to add the new file to the appropriate settings file.  
    # This is hard to do programmatically, because the settings files are 
    # python scripts.  To do it properly, I'd have to compile the python code 
    # into an AST, modify it, then convert it back into source code.

    rel_cxxtest_path = os.path.relpath(cxxtest_path, os.getcwd())
    rel_settings_path = os.path.relpath(
            os.path.join(
                rosetta_dir, 'source', 'test', library + '.test.settings'),
            os.getcwd())

    print("Created '{}'.".format(rel_cxxtest_path))
    print("Add the following entry to '{}':".format(rel_settings_path))
    print()
    print("""\
    "{namespace}": [
        "{suite}",
    ],
""".format(**locals()))


class BadAliasError(helpers.FatalBuildError):
    exit_status = 1
    exit_message = "No such alias '{0}'."

    def __init__(self, alias):
        super().__init__(alias)



