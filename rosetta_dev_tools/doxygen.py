#!/usr/bin/env python3

import os
import shutil
import helpers
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--fast', '-f', action='store_true')
parser.add_argument('--quiet', '-q', action='store_true')
arguments = parser.parse_args()

root = '/tmp/rosetta_doxygen'
html = os.path.join(root, 'html', 'annotated.html')

if os.path.exists(root):
    shutil.rmtree(root)

os.mkdir(root)

doxygen_config = [
        'OUTPUT_DIRECTORY = ' + root,
        'EXTRACT_ALL = YES',
        'EXTRACT_PRIVATE = YES',
        'RECURSIVE = ' + 'YES' if not arguments.fast else 'NO',
        'SOURCE_BROWSER = YES',
        'INLINE_SOURCES = YES',
]
doxygen_command =  'echo "{}" | doxygen -'.format('\n'.join(doxygen_config))
firefox_command = 'firefox -new-window {}'.format(html)

helpers.shell_command('.', doxygen_command)
if not arguments.quiet:
    helpers.shell_command('.', firefox_command)

