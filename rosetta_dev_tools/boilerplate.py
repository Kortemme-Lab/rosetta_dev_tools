#!/usr/bin/env python

"""\
Write stub source code files with most of the boilerplate filled in.

Usage:
    rdt_stub <type> <name> [options]

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
        
        fwd.hh; hh; cc; mover.hh; mover.cc; creator.hh; creator.ihh; 
        registrator.ihh; src.settings; test.settings; cxxtest.hh
            Create a file with the given extension for a class with the given 
            name and namespace.

    <name>
        The name of the class to write boilerplate for.  If the name doesn't 
        include a namespace, the namespace will be assumed to be the current 
        working directory.

Options:
    -d, --dry-run
        Print out the generated source code rather than printing it to a file.

    -p, --parent
        The parent class of the class to write boilerplate for.  This is only 
        needed if a header file will be written.
"""

import sys, os, re, shutil, glob
from . import helpers

def main():
    import docopt
    args = docopt.docopt(__doc__)
    command = args['<type>']
    name = args['<name>']
    parent = args['--parent']
    dry_run = args['--dry-run']

    try:
        if command == 'mover':
            write_fwd_hh_file(name, dry_run | MORE_FILES)
            write_mover_hh_file(name, parent, dry_run | MORE_FILES)
            write_mover_cc_file(name, dry_run | MORE_FILES)
            write_mover_creator_file(name, dry_run | MORE_FILES)
            write_mover_creator_ihh_line(name, dry_run | MORE_FILES)
            write_mover_registrator_ihh_line(name, dry_run | MORE_FILES)
            write_src_settings_line(name, dry_run | MORE_FILES)
            write_test_settings_line(name, dry_run | MORE_FILES)
            write_cxxtest_hh_file(name + 'Test', dry_run)
        elif command == 'class':
            write_fwd_hh_file(name, dry_run | MORE_FILES)
            write_hh_file(name, parent, dry_run | MORE_FILES)
            write_cc_file(name, dry_run | MORE_FILES)
            write_src_settings_line(name, dry_run | MORE_FILES)
            write_test_settings_line(name, dry_run | MORE_FILES)
            write_cxxtest_hh_file(name + 'Test', dry_run)
        elif command == 'fwd.hh':
            write_fwd_hh_file(name, dry_run)
        elif command == 'hh':
            write_hh_file(name, parent, dry_run)
        elif command == 'cc':
            write_cc_file(name, dry_run)
        elif command == 'mover.hh':
            write_mover_hh_file(name, parent, dry_run)
        elif command == 'mover.cc':
            write_mover_cc_file(name, dry_run)
        elif command == 'creator.hh':
            write_mover_creator_file(name, dry_run)
        elif command == 'creator.ihh':
            write_mover_creator_ihh_line(name, dry_run)
        elif command == 'registrator.ihh':
            write_mover_registrator_ihh_line(name, dry_run)
        elif command == 'src.settings':
            write_src_settings_line(name, dry_run)
        elif command == 'test.settings':
            write_test_settings_line(name, dry_run)
        elif command == 'cxxtest.hh':
            write_cxxtest_hh_file(name, dry_run)
        else:
            print("Unknown filetype: '{}'".format(command))

    except KeyboardInterrupt:
        pass

    except helpers.FatalBuildError as error:
        error.exit_gracefully()


def get_fully_qualified_name(name):
    if '::' in name:
        names = name.split('::')
        return names[-1], names[:-1]
    else:
        rosetta_path = os.path.realpath(helpers.find_rosetta_installation())
        source_path = os.path.join(rosetta_path, 'source', 'src')
        current_path = os.path.realpath('.')[len(source_path):]
        return name, [x for x in current_path.split(os.path.sep) if x != '']

def get_source_dir(namespace):
    return os.path.join(
            helpers.find_rosetta_installation(),
            'source', 'src', *namespace)

def get_source_path(name, namespace, extension):
    return os.path.join(
            get_source_dir(namespace),
            name + extension)

def get_test_dir(namespace):
    return os.path.join(
            helpers.find_rosetta_installation(),
            'source', 'test', *namespace)

def get_test_path(name, namespace, extension):
    return os.path.join(
            get_test_dir(namespace),
            name + extension)

def get_protocols_init_dir():
    return os.path.join(
            helpers.find_rosetta_installation(),
            'source', 'src', 'protocols', 'init')

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
        namespace_cpp='::'.join(namespace),
        license=get_license(),
        include_guard=get_include_guard(name, namespace, include_guard_ext),
        namespace_opener=get_namespace_opener(namespace),
        namespace_closer=get_namespace_closer(namespace),
        tracer=get_tracer(name, namespace),
        cls='class',
    )


DRY_RUN = 0x01
MORE_FILES = 0x02

def write_file(file_path, content, summary=None, dry_run=False):
    from nonstdlib import print_color

    directory = os.path.dirname(file_path)
    rel_directory = os.path.relpath(directory, os.getcwd())
    rel_file_path = os.path.relpath(file_path, os.getcwd())

    # If this is a dry run, simply print out the given content and return.

    if dry_run & DRY_RUN:
        try:
            print_color(rel_file_path, 'magenta', 'bold')
            if not summary:
                print(content)
            else:
                print('...\n{}...'.format(summary))
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

def insert_line_into_file(path, line, dry_run=False):

    # Read the file.  If the line is already in the file, stop right away.

    with open(path) as file:
        lines = file.readlines()

    i = insert_alphabetically(line + '\n', lines)

    # Write the file back to disk with the new line included.

    content = ''.join(lines)
    summary = ''.join(['...\n'] + lines[i-1:i+2] + ['...\n'])
    write_file(path, content, summary, dry_run)

def insert_name_into_settings(path, name, namespace, dry_run):
    # Parse the settings file into a set of blocks, where each block represents 
    # one namespace and all of its files.  The blocks are stored in a ordered 
    # dictionary, where the key is the name of the block's namespace.

    with open(path) as file:
        lines = file.readlines()

    class Block:

        def __init__(self):
            self.lines = []

        def __repr__(self):
            if self.lines:
                return 'Block({})'.format(self.lines[0].strip())
            else:
                return 'Block()'

        def __str__(self):
            return ''.join(self.lines)

        def __bool__(self):
            return bool(self.lines)

        def __eq__(self, other):
            return str(self) == str(other)

        def __lt__(self, other):
            return str(self) < str(other)


    blocks = [Block()]
    relevant_block = None
    begin_block_pattern = re.compile(r'''\s*['"](.+)['"]\s*:\s*\[''')
    end_block_pattern = re.compile(r'''\s*\],''')

    for line in lines:
        begin_block = begin_block_pattern.match(line)
        end_block = end_block_pattern.match(line)

        if begin_block:
            if blocks[-1]:
                blocks.append(Block())
            if '/'.join(namespace) == begin_block.group(1):
                relevant_block = blocks[-1]

        blocks[-1].lines.append(line)

        if end_block:
            if blocks[-1]:
                blocks.append(Block())

    # If the namespace we're trying to add is already present in the file, 
    # insert the new name into the existing block.
    
    if relevant_block:
        line = '\t\t"{name}",\n'.format(name=name)
        insert_alphabetically(line, relevant_block.lines)

    # Otherwise, add a completely new block to the file.

    else:
        fields = get_common_fields(name, namespace)
        relevant_block = Block()
        relevant_block.lines = [
                '	"{namespace}": [\n'.format(**fields),
                '		"{name}",\n'.format(**fields),
                '	],\n',
        ]
        insert_alphabetically(relevant_block, blocks)

    # Write the file.

    content, summary = ''.join(str(x) for x in blocks), str(relevant_block)
    write_file(path, content, summary, dry_run)

def insert_alphabetically(line, lines):
    if line in lines:
        return

    # Make a separate list for the lines that we want to insert our line 
    # alphabetically into.  Then insert our line into that list and sort it to 
    # figure our where our line ends up.

    sorted_lines = list(sorted(lines + [line]))
    sorted_index = sorted_lines.index(line)

    # Find the closest line to our new line in the sorted list, then insert our 
    # line into the list of all the lines in file right next to that closest 
    # line.  The case where our line ends up as the last element in the sorted 
    # list has to be handled specially.

    if sorted_index + 1 == len(sorted_lines):
        closest_line = sorted_lines[-2]
        insert_offset = 1
    else:
        closest_line = sorted_lines[sorted_index + 1]
        insert_offset = 0

    insert_index = lines.index(closest_line) + insert_offset
    lines.insert(insert_index, line)

    # Return the index of the inserted line, in case the caller is interested 
    # in where our line ended up.

    return insert_index


def write_fwd_hh_file(name, dry_run=False):
    name, namespace = get_fully_qualified_name(name)
    path = get_source_path(name, namespace, '.fwd.hh')
    write_file(path, '''\
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
    dry_run=dry_run)

def write_hh_file(name, parent=None, dry_run=False):
    name, namespace = get_fully_qualified_name(name)
    path = get_source_path(name, namespace, '.hh')
    write_file(path, '''\
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
    dry_run=dry_run)

def write_cc_file(name, dry_run=False):
    name, namespace = get_fully_qualified_name(name)
    path = get_source_path(name, namespace, '.cc')
    write_file(path, '''\
{license}

// Unit headers
#include <{namespace}/{name}.hh>

// Core headers
#include <core/types.hh>

// Utility headers
#include <basic/Tracer.hh>

// Namespaces
using namespace std;
using core::Size;
using core::Real;

{namespace_opener}

{tracer}

{namespace_closer}
'''.format(
        **get_common_fields(name, namespace)),
    dry_run=dry_run)

def write_mover_hh_file(name, parent=None, dry_run=False):
    name, namespace = get_fully_qualified_name(name)
    parent=parent or 'protocols::moves::Mover'
    path = get_source_path(name, namespace, '.hh')
    write_file(path, '''\
{include_guard}

// Unit headers
#include <{namespace}/{name}.fwd.hh>

// Protocol headers
#include <{parent_hh}>

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

/// @brief Copy constructor.
{name}({name} const & other);

/// @brief Default destructor.
~{name}();

/// @copydoc {parent}::get_name
std::string get_name() const {{ return "{name}"; }}

/// @copydoc {parent}::fresh_instance
protocols::moves::MoverOP fresh_instance() const;

/// @copydoc {parent}::clone
protocols::moves::MoverOP clone() const;

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
        parent=parent,
        parent_hh='/'.join(parent.split('::')) + '.hh',
        **get_common_fields(name, namespace)),
    dry_run=dry_run)

def write_mover_cc_file(name, dry_run=False):
    name, namespace = get_fully_qualified_name(name)
    path = get_source_path(name, namespace, '.cc')
    write_file(path, '''\
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

// Namespaces
using namespace std;
using core::Size;
using core::Real;
using protocols::moves::MoverOP;

{namespace_opener}

{tracer}

MoverOP {name}Creator::create_mover() const {{
	return MoverOP( new {name} );
}}

string {name}Creator::keyname() const {{
	return "{name}";
}}

{name}::{name}() {{}}

{name}::{name}({name} const & /*other*/) {{}}

{name}::~{name}() {{}}

MoverOP {name}::fresh_instance() const {{
	return MoverOP( new {name} );
}}

MoverOP {name}::clone() const {{
	return MoverOP( new {name}( *this ) );
}}

void {name}::parse_my_tag(
		utility::tag::TagCOP /*tag*/,
		basic::datacache::DataMap & /*data*/,
		protocols::filters::Filters_map const & /*filters*/,
		protocols::moves::Movers_map const & /*movers*/,
		core::pose::Pose const & /*pose*/) {{
}}

void {name}::apply(core::pose::Pose & /*pose*/) {{
	tr << "Hello world!" << endl;
}}

{namespace_closer}
'''.format(
        **get_common_fields(name, namespace)),
    dry_run=dry_run)

def write_mover_creator_file(name, dry_run=False):
    name, namespace = get_fully_qualified_name(name)
    path = get_source_path(name, namespace, 'Creator.hh')
    write_file(path, '''\
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
    dry_run=dry_run)

def write_mover_creator_ihh_line(name, dry_run=False):
    name, namespace = get_fully_qualified_name(name)
    path = os.path.join(
            get_protocols_init_dir(), 'init.MoverCreators.ihh')
    line = '#include <{namespace}/{name}Creator.hh>'.format(
            **get_common_fields(name, namespace))
    insert_line_into_file(path, line, dry_run=dry_run)

def write_mover_registrator_ihh_line(name, dry_run=False):
    name, namespace = get_fully_qualified_name(name)
    path = os.path.join(
        get_protocols_init_dir(), 'init.MoverRegistrators.ihh')
    line = 'static MoverRegistrator< {namespace}::{creator} > reg_{creator};'.format(
            namespace='::'.join(namespace[1:]),
            creator=name + 'Creator',
    )
    insert_line_into_file(path, line, dry_run=dry_run)

def write_cxxtest_hh_file(name, dry_run=False):
    name, namespace = get_fully_qualified_name(name)
    path = get_test_path(name, namespace, '.cxxtest.hh')
    write_file(path, '''\
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
    dry_run=dry_run)

def write_src_settings_line(name, dry_run=False):
    name, namespace = get_fully_qualified_name(name)
    namespace_path = '/'.join(namespace)
    settings_glob = os.path.join(
            helpers.find_rosetta_installation(),
            'source', 'src', namespace[0] + '*src.settings')

    # See if this namespace is already present in any of the relevant settings 
    # files.  If so, update that file.

    for path in glob.glob(settings_glob):
        with open(path) as file:
            if namespace_path in file.read():
                break

    # If we can't automatically decide which settings file to update, ask the 
    # user to make the decision.

    else:
        path = input("Which settings file to use: ")

    # Update the chosen file.

    insert_name_into_settings(path, name, namespace, dry_run)

def write_test_settings_line(name, dry_run=False):
    name, namespace = get_fully_qualified_name(name)
    path = os.path.join(
            helpers.find_rosetta_installation(),
            'source', 'test', namespace[0] + '.test.settings')
    insert_name_into_settings(path, name + 'Test', namespace[1:], dry_run)


