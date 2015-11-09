#!/usr/bin/env python

"""\
Write stub source code files with most of the boilerplate filled in.

Usage:
    rdt_stub <type> <name> [<namespace>] [options]

Arguments:
    <type>
        What type of file or files to generate.  This may either be a keyword, 
        to generate several related files, or an extension, to generate single 
        specific files:

        mover:
            Create *.fwd.hh, *.hh, *.cc, *Creator.hh, and *.cxxtest.hh 
            files for a mover with the given name and namespace.  The *.hh and 
            *.cc files are pre-filled with mover-specific definitions.

        class:
            Create *.fwd.hh, *.hh, and *.cc files for a class with the given 
            name and namespace.
        
        fwd.hh; hh; cc; mover.hh; mover.cc; creator.hh; cxxtest.hh:
            Create a file with the given extension for a class with the given 
            name and namespace.

    <name>
        The name of the class to write boilerplate for.

    <namespace>
        The namespace of the class to write boilerplate for.  If not specified, 
        this will be inferred from the current working directory.

Options:
    -d, --dry-run
        Print out the generated source code rather than printing it to a file.

    -p, --parent
        The parent class of the class to write boilerplate for.  This is only 
        needed if a header file will be written.
"""

import sys, os, re, shutil
from . import helpers

def main():
    import docopt
    args = docopt.docopt(__doc__)
    command = args['<type>']
    name = args['<name>']
    namespace = args['<namespace>']
    parent = args['--parent']
    dry_run = args['--dry-run']

    try:
        if command == 'mover':
            write_fwd_hh_file(name, namespace, dry_run | MORE_FILES)
            write_mover_hh_file(name, namespace, parent, dry_run | MORE_FILES)
            write_mover_cc_file(name, namespace, dry_run | MORE_FILES)
            write_mover_creator_file(name, namespace, dry_run | MORE_FILES)
            write_cxxtest_hh_file(name + 'Test', namespace, dry_run)
        elif command == 'class':
            write_fwd_hh_file(name, namespace, dry_run | MORE_FILES)
            write_hh_file(name, namespace, parent, dry_run | MORE_FILES)
            write_cc_file(name, namespace, dry_run | MORE_FILES)
            write_cxxtest_hh_file(name + 'Test', namespace, dry_run)
        elif command == 'fwd.hh':
            write_fwd_hh_file(name, namespace, dry_run)
        elif command == 'hh':
            write_hh_file(name, namespace, parent, dry_run)
        elif command == 'cc':
            write_cc_file(name, namespace, dry_run)
        elif command == 'mover.hh':
            write_mover_hh_file(name, namespace, parent, dry_run)
        elif command == 'mover.cc':
            write_mover_cc_file(name, namespace, dry_run)
        elif command == 'creator.hh':
            write_mover_creator_file(name, namespace, dry_run)
        elif command == 'cxxtest.hh':
            write_cxxtest_hh_file(name, namespace, dry_run)
        else:
            print("Unknown filetype: '{}'".format(command))

    except KeyboardInterrupt:
        pass

    except helpers.FatalBuildError as error:
        error.exit_gracefully()


def get_namespace(namespace=None):
    if namespace is not None:
        return re.split('::|/', namespace)
    else:
        rosetta_path = os.path.realpath(helpers.find_rosetta_installation())
        source_path = os.path.join(rosetta_path, 'source', 'src')
        current_path = os.path.realpath('.')[len(source_path):]
        return [x for x in current_path.split(os.path.sep) if x != '']

def get_source_dir(namespace):
    return os.path.join(
            helpers.find_rosetta_installation(),
            'source', 'src', *namespace)

def get_test_dir(namespace):
    return os.path.join(
            helpers.find_rosetta_installation(),
            'source', 'test', *namespace)

def get_license():
    return '''\
// -*- mode:c++;tab-width:2;indent-tabs-mode:t;show-trailing-whitespace:t;rm-trailing-spaces:t -*-
// vi: set ts=2 noet:
//
// (c) Copyright Rosetta Commons Member Institutions.
// (c) This file is part of the Rosetta software suite and is made available under license.
// (c) The Rosetta software is developed by the contributing members of the Rosetta Commons.
// (c) For more information, see http://www.rosettacommons.org. Questions about this can be
// (c) addressed to University of Washington UW TechTransfer, email: license@u.washington.edu.'''

def get_include_guard(name, namespace, extension):
    return '''\
{license}

#ifndef INCLUDED_{namespace}_{name}_{extension}
#define INCLUDED_{namespace}_{name}_{extension}'''.format(
        license=get_license(),
        name=name,
        namespace='_'.join(namespace),
        extension=extension.upper())

def get_namespace_opener(namespace):
    lines = []
    for layer in namespace:
        lines.append('namespace {} {{'.format(layer))
    return '\n'.join(lines)

def get_namespace_closer(namespace):
    return '\n'.join('}' for x in namespace)
    
def get_tracer(name, namespace):
    return 'static basic::Tracer tr("{}");'.format(
            '.'.join(namespace + [name]))

def get_common_fields(name, namespace, include_guard_ext='HH'):
    return dict(
        name=name,
        namespace='/'.join(namespace),
        license=get_license(),
        include_guard=get_include_guard(name, namespace, include_guard_ext),
        namespace_opener=get_namespace_opener(namespace),
        namespace_closer=get_namespace_closer(namespace),
        tracer=get_tracer(name, namespace),
        cls='class',
    )


def write_file(directory, file_name, content, dry_run=False):
    file_path = os.path.join(directory, file_name)
    rel_directory = os.path.relpath(directory, os.getcwd())
    rel_file_path = os.path.relpath(file_path, os.getcwd())

    # If this is a dry run, simply print out the given content and return.

    if dry_run & DRY_RUN:
        try:
            from nonstdlib import print_color
            print_color(rel_file_path, 'magenta', 'bold')
            print(content)
            if dry_run & MORE_FILES:
                input("Next file? ")
        except KeyboardInterrupt:
            print()
            sys.exit()
        else:
            return

    # Check to see if a directory already exists for this namespace.  If it 
    # doesn't, ask the user if one should be created.

    print("Writing {}".format(rel_file_path))

    if not os.path.exists(directory):
        make_dir = input("'{}' doesn't exist.  Create it? [y/N] ".format(
            rel_directory))
        if make_dir == 'y':
            os.makedirs(directory, exist_ok=True)
        else:
            return

    # Write the given content to the given file.

    with open(file_path, 'w') as file:
        file.write(content)

DRY_RUN = 0x01
MORE_FILES = 0x02

def write_fwd_hh_file(name, namespace=None, dry_run=False):
    namespace = get_namespace(namespace)
    directory = get_source_dir(namespace)
    write_file(directory, name + '.fwd.hh', '''\
{include_guard}

#include <utility/pointer/owning_ptr.hh>

{namespace_opener}

{cls} {name};

typedef utility::pointer::shared_ptr<{name}> {name}OP;
typedef utility::pointer::shared_ptr<{name} const> {name}COP;

{namespace_closer}

#endif
'''.format(
        **get_common_fields(name, namespace, 'FWD_HH')),
    dry_run)

def write_hh_file(name, namespace=None, parent=None, dry_run=False):
    namespace = get_namespace(namespace)
    directory = get_source_dir(namespace)
    write_file(directory, name + '.hh', '''\
{include_guard}

// Unit headers
#include <{namespace}/{name}.fwd.hh>

{namespace_opener}

{cls} {name}{inheritance} {{

public:

/// @brief Default constructor.
{name}();

/// @brief Default destructor.
~{name}();

}};

{namespace_closer}

#endif
'''.format(
        inheritance=' : public ' + parent if parent else '',
        **get_common_fields(name, namespace)),
    dry_run)

def write_cc_file(name, namespace=None, dry_run=False):
    namespace = get_namespace(namespace)
    directory = get_source_dir(namespace)
    write_file(directory, name + '.cc', '''\
{license}

// Unit headers
#include <{namespace}/{name}.hh>

// Utility headers
#include <basic/Tracer.hh>
#include <boost/foreach.hpp>
#define foreach BOOST_FOREACH

// Namespaces
using namespace std;
using core::Size;
using core::Real;

{namespace_opener}

{tracer}

{namespace_closer}
'''.format(
        **get_common_fields(name, namespace)),
    dry_run)

def write_mover_hh_file(name, namespace=None, parent=None, dry_run=False):
    namespace = get_namespace(namespace)
    directory = get_source_dir(namespace)
    write_file(directory, name + '.hh', '''\
{include_guard}

// Unit headers
#include <{namespace}/{name}.fwd.hh>

// RosettaScripts headers
#include <utility/tag/Tag.fwd.hh>
#include <basic/datacache/DataMap.fwd.hh>
#include <protocols/filters/Filter.fwd.hh>
#include <protocols/moves/Mover.fwd.hh>
#include <core/pose/Pose.fwd.hh>

{namespace_opener}

{cls} {name} : public {parent} {{

public:

/// @brief Default constructor.
{name}();

/// @brief Default destructor.
~{name}();

/// @copydoc {parent}::get_name
std::string get_name() const {{ return "{name}"; }}

/// @copydoc {parent}::parse_my_tag
void parse_my_tag(
        utility::tag::TagCOP tag,
        basic::datacache::DataMap & data,
        protocols::filters::Filters_map const & filters,
        protocols::moves::Movers_map const & movers,
        core::pose::Pose const & pose);

/// @brief ...
void apply(core::pose::Pose & pose);

}};

{namespace_closer}

#endif
'''.format(
        parent=parent or 'protocols::moves::Mover',
        **get_common_fields(name, namespace)),
    dry_run)

def write_mover_cc_file(name, namespace=None, dry_run=False):
    namespace = get_namespace(namespace)
    directory = get_source_dir(namespace)
    write_file(directory, name + '.cc', '''\
{license}

// Unit headers
#include <{namespace}/{name}.hh>
#include <{namespace}/{name}Creator.hh>

// RosettaScripts headers
#include <utility/tag/Tag.hh>
#include <basic/datacache/DataMap.hh>
#include <protocols/filters/Filter.hh>
#include <protocols/moves/Mover.hh>

// Utility headers
#include <basic/Tracer.hh>
#include <boost/foreach.hpp>
#define foreach BOOST_FOREACH

// Namespaces
using namespace std;
using core::Size;
using core::Real;

{namespace_opener}

{tracer}

protocols::moves::MoverOP {name}Creator::create_mover() const {{
	return new {name};
}}

std::string {name}Creator::keyname() const {{
	return "{name}";
}}

{name}::{name}() {{}}

void {name}::parse_my_tag(
		utility::tag::TagCOP tag,
		basic::datacache::DataMap & data,
		protocols::filters::Filters_map const & filters,
		protocols::moves::Movers_map const & movers,
		core::pose::Pose const & pose) {{
}}

void {name}::apply(core::pose::Pose & pose) {{
}}

{namespace_closer}
'''.format(
        **get_common_fields(name, namespace)),
    dry_run)

def write_mover_creator_file(name, namespace=None, dry_run=False):
    namespace = get_namespace(namespace)
    directory = get_source_dir(namespace)
    write_file(directory, name + 'Creator.hh', '''\
{include_guard}

#include <protocols/moves/MoverCreator.hh>

{namespace_opener}

{cls} {name}Creator : public protocols::moves::MoverCreator {{
public:
	virtual protocols::moves::MoverOP create_mover() const;
	virtual std::string keyname() const;
}};

{namespace_closer}

#endif
'''.format(
        **get_common_fields(name, namespace, 'CREATOR_HH')),
    dry_run)

def write_cxxtest_hh_file(name, namespace=None, dry_run=False):
    namespace = get_namespace(namespace)
    directory = get_test_dir(namespace)
    write_file(directory, name + '.cxxtest.hh', '''\
{include_guard}

// Test headers
#include <cxxtest/TestSuite.h>
#include <test/core/init_util.hh>

// C++ headers
#include <iostream>

using namespace std;

{cls} {name} : public CxxTest::TestSuite {{

public:

	void setUp() {{
		core_init();
	}}

	void test_hello_world() {{
		cout << "Hello world!" << endl;
	}}

}};

#endif
'''.format(
        **get_common_fields(name, namespace, 'CXXTEST_HH')),
    dry_run)

    # Instruct the user to add the new file to the appropriate settings file.  
    # This is hard to do programmatically, because the settings files are 
    # python scripts.  To do it properly, I'd have to compile the python code 
    # into an AST, modify it, then convert it back into source code.

    if not dry_run:
        rel_settings_path = os.path.relpath(
                os.path.join(
                    helpers.find_rosetta_installation(),
                    'source', 'test', namespace[0] + '.test.settings'),
                os.getcwd())

        print()
        print("Add the following entry to '{}':".format(rel_settings_path))
        print()
        print('''\
        "{namespace}": [
            "{name}",
        ],
'''.format(
            name=name,
            namespace='/'.join(namespace),
        ))


