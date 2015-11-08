#!/usr/bin/env python3

"""\
Generate documentation for a small number of files you're actively developing.

Usage:
    rdt_doxygen [<directory>] [options]

Arguments:
    <directory>         [default: .]
        The directory to generate documentation for.

Options:
    -r, --recursive
        Recurse into subdirectories of the specified directory.  This is off by 
        default, because it can be noticeably slower.

    -q, --quiet
        Don't launch a new Firefox window after generating the documentation.  
        Usually you wouldn't specify this option the first time you run this 
        command, because otherwise you'd have to open a web browser window 
        yourself.  After that, though, you would specify this option and reuse 
        the window you already have.
"""

import os, shutil, docopt
from . import helpers

def main():
    args = docopt.docopt(__doc__)
    target_dir = args['<directory>'] or '.'

    # Make a temporary directory for the doxygen build.

    root = '/tmp/rosetta_doxygen'
    html = os.path.join(root, 'html', 'annotated.html')
    if os.path.exists(root):
        shutil.rmtree(root)
    os.mkdir(root)

    # Run doxygen on the specified directory, then show the resulting 
    # documentation in a Firefox window (unless the user specified '-q').

    doxygen_config = [
            'OUTPUT_DIRECTORY = ' + root,
            'EXTRACT_ALL = YES',
            'EXTRACT_PRIVATE = YES',
            'RECURSIVE = ' + 'YES' if not args['--recursive'] else 'NO',
            'SOURCE_BROWSER = YES',
            'INLINE_SOURCES = YES',
            'GENERATE_HTML = YES',
    ]
    doxygen_command =  'echo "{}" | doxygen -'.format('\n'.join(doxygen_config))
    firefox_command = 'firefox -new-window {}'.format(html)

    helpers.shell_command(target_dir, doxygen_command)
    if not args['--quiet']:
        helpers.shell_command(target_dir, firefox_command)

