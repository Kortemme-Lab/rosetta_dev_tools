#!/usr/bin/env python3

import os

def find_rosetta_installation():
    import subprocess

    try: 
        with open(os.devnull, 'w') as devnull:
            command = 'git', 'rev-parse', '--show-toplevel'
            stdout = subprocess.check_output(command, stderr=devnull)
            path = stdout.strip()

    except subprocess.CalledProcessError:
        raise RosettaNotFound()

    return path.decode('utf8')

def shell_command(directory, command, check=True, verbose=False):
    """ Executes the given command in the given directory.  The command can 
    either be given as a string or a list of words.  If the check flag is set, 
    an exception will be raised if the command returns a non-zero value. """

    import subprocess

    if isinstance(command, tuple) or isinstance(command, list):
        command = ' '.join(command)

    if verbose:
        print('$ cd', directory)
        print('$', command)

    call = subprocess.call if not check else subprocess.check_call
    return call(command, cwd=directory, shell=True)


class FatalBuildError (Exception):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def exit_gracefully(self):
        import sys, re, textwrap

        header = "Error: "
        indent = len(header) * ' '
        trailing_whitespace = re.compile(' *\\n')

        message = self.exit_message.format(*self.args, **self.kwargs)
        message = trailing_whitespace.sub('\\n', message)
        message = header + textwrap.dedent(message)
        message = textwrap.fill(message, subsequent_indent=indent)

        print(message)
        sys.exit(self.exit_status)

    def get_info_message(self):
        import textwrap

        message = self.info_message.format(*self.args, **self.kwargs)
        message = textwrap.dedent(message)
        message = textwrap.fill(message, drop_whitespace=True,
                initial_indent='  ', subsequent_indent='  ')

        return message


class RosettaNotFound (FatalBuildError):
    exit_status = 1
    exit_message = """\
            This command must be run from within a rosetta installation.  
            Presently, only installations that are stored in a git repository 
            can be detected."""
       
class MissingCMakeFiles (FatalBuildError):
    exit_status = 2
    exit_message = """\
            Could not find '{0}'.  This might indicate that this script was 
            unable to properly locate your Rosetta installation, or it may 
            indicate that your installation has somehow been corrupted. """

    def __init__(self, *sub_paths):
        path = os.path.join('source', 'cmake', *sub_paths)
        FatalBuildError.__init__(self, path)


