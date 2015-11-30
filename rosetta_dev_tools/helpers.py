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

def shell_command(directory, command, check=True, one_line=False, verbose=False):
    """
    Executes the given command in the given directory.  The command can either 
    be given as a string or a list of words.  If the check flag is set, an 
    exception will be raised if the command returns a non-zero value.  If the 
    one_line flag is set, the output will be kept on one line.
    """

    import select, subprocess, shlex, nonstdlib

    # If the command was given as a tuple, turn it into a string that can be 
    # interpreted by the shell.  This creates a shell injection vulnerability, 
    # but since all the variable arguments come directly from the user, I think 
    # it's worth the added flexibility afforded by using the shell.

    if isinstance(command, tuple) or isinstance(command, list):
        command = ' '.join(shlex.quote(x) for x in command)

    # If verbose output is requested, print the command being run and the 
    # directory its being run from.

    if verbose:
        print('$ cd', directory)
        print('$', command)

    # Run the command.  If the one_line option is given, grab every line 
    # printed to stdout and force it to overwrite the previous line.  Otherwise 
    # just run the command like normal.

    process = subprocess.Popen(
            command, cwd=directory, shell=True,
            stdout=subprocess.PIPE if one_line else None)

    if not one_line:
        process.wait()
    else:
        while process.poll() is None:
            select.select([process.stdout.fileno()], [], [])
            stdout = process.stdout.readline().decode()
            stdout = stdout.replace('\n', ' ')
            stdout = nonstdlib.truncate_to_fit_terminal(stdout)
            if stdout.strip():
                nonstdlib.update(stdout)
        print()

    # Check the return code to see if the command failed.  If it did and the 
    # 'check' flag is set, raise an exception.  Otherwise just pass the return 
    # code on to the caller.

    if check and process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command)

    return process.returncode

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
       
