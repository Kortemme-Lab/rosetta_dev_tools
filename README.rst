***********************
Rosetta Developer Tools
***********************
There are a number of reasons why the edit-compile-test cycle is not as 
convenient as it could be in Rosetta.  One is that the source code, the unit 
tests, and the pilot app executables are all kept in very different places, 
which requires you to keep changing directories as changes are made.  Another 
is that a large amount of boilerplate has to be written when adding new 
classes, and yet another is that incremental compilation times can be quite 
slow.

This package attempts to address some of these issues, in particular the ease 
with which code can be compiled and tested.  Towards this end, a set of scripts 
are provided which simplify the process of compiling, testing, and running 
Rosetta.  These scripts are aware of Rosetta's directory structure, so paths do 
not need to be specified.

These scripts also use the ninja build system, which is much faster than scons 
at executing incremental builds.  This takes some external work to configure 
properly, but information is available on the Kortemme lab wiki page.

Installation
============
You can install these tools by cloning this repository and running pip::

   $ git clone git@github.com:Kortemme-Lab/rosetta_dev_tools.git
   $ pip install rosetta_dev_tools

This will install a handful of executable scripts in whichever ``bin/`` 
directory pip is configured to use.  These scripts have pretty long names, so I 
usually alias them to something shorter to make typing them more convenient::

   alias rb='rdt_build debug'
   alias rr='rdt_build release'
   alias ru='rdt_unit_test'
   alias rd='rdt_doxygen'

Usage
=====
To build rosetta in debug mode, just run the following alias from anywhere in 
your checkout of rosetta::

   $ rb

To build in release mode, run the following alias instead::

   $ rr

Both of these commands also have options to build from scratch by deleting all 
the binaries built by previous invocations.

To run a unit test suite, use the following command as a template::

   $ ru protocols MyUnitTest

The first argument is the library that the unit test is part of, which usually 
is ``protocols``.  The second argument is the name of the test suite to run 
(i.e. the name of the class in your ``*.cxxtest.hh`` file).  You can also 
specify a third argument to run just one specific test case (i.e. one 
``test_*()`` method from that class).

Once you've run a unit test using a command like the one above, you can use an 
abbreviated version of that command to run the same test again::

   $ ru

That command will rerun the last unit test that was run.  It is also possible 
to assign names to commonly used tests, so that you can run them in as few 
keystrokes as possible::

   $ ru protocols MyOtherUnitTest -s other
   $ ru other

The unit test command can also create boilerplate unit test files.  Use the 
``--new`` option along with the library, namespace, and test suite names::

   $ ru --new protocols subdir/relative/to/protocols MyThirdUnitTest

To generate doxygen documentation for whichever directory you're currently in, 
run the following command::

   $ rd

This will generate documentation and automatically present it to you in a new 
firefox window.



   
   
