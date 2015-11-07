Rosetta Developer Tools
=======================
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
usually alias them to something shorter to make typing them more convenient.
   
