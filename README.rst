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
You can install these tools by cloning this repository and running ``pip``.  
Note that these tools depend on ``python3``, so the installation won't work if 
you use a ``pip`` associated with ``python2``::

   $ git clone git@github.com:Kortemme-Lab/rosetta_dev_tools.git
   $ pip3 install ./rosetta_dev_tools

This will install a handful of executable scripts in whichever ``bin/`` 
directory ``pip`` is configured to use.  These scripts have pretty long names, 
so I usually alias them to something shorter to make typing them more 
convenient.  For example, put these lines in ``~/.bashrc``::

   alias rk='rdt_stub'
   alias rb='rdt_build debug'
   alias rr='rdt_build release'
   alias ru='rdt_unit_test'
   alias rd='rdt_doxygen'

If you want to install these tools on the QB3 cluster, you'll have to take a 
couple extra steps.  First, you have to be on an interactive node (e.g.  
``iqint``) or git clone won't work.  Second, the cluster doesn't have ``pip`` 
installed, so you'll have to run ``setup.py`` manually.  Third, the cluster 
doesn't make ``python3`` available by default, so you have to explicitly enable 
it using the ``scl enable python33`` command::

   $ ssh iqint
   $ git clone git@github.com:Kortemme-Lab/rosetta_dev_tools.git
   $ cd rosetta_dev_tools
   $ scl enable python33 'python setup.py build'
   $ scl enable python33 'python setup.py install --user'

You'll also have to use the ``scl enable python33`` command every time you want 
to use any of these tools, so it's easiest to simply wrap them in functions.  
For example, put these lines in ``~/.bashrc``::

   function rb {} (
       scl enable python33 'rdt_build debug $*'
   }
   function rr {} (
       scl enable python33 'rdt_build release $*'
   }

Filling in boilerplate
======================
To create all the boilerplate files for a new mover, run the following 
command::

   $ rk mover protocols::moves::MyMover

This command will create new ``*.fwd.hh``, ``*.hh``, ``*Creator.hh``, ``*.cc``, 
and ``*.cxxtest.hh`` files.  It will also add the mover to the relevant 
``*.src.settings`` and ``*.test.settings`` files, and it will register the 
mover in ``init.MoverCreators.ihh`` and ``init.MoverRegistrators.ihh``.  When 
the command finishes, your new class will be completely ready to compile.

The first argument specifies what kind of file(s) to make and the second 
argument specifies the name of the new class.  The second argument doesn't have 
to be a fully qualified name (i.e. it doesn't have to include a namespace).  If 
you don't specify a namespace, one will be automatically inferred from the 
current working directory.  So the above command could be abbreviated like so::

   $ cd $rosetta/source/src/protocols/moves
   $ rk mover MyMover

This command also has a convenient ``--dry-run`` option you can use to look at 
the stub files being generated before they are actually written to disk.

Compiling rosetta
=================
To build rosetta in debug mode, just run the following alias from anywhere in 
your checkout of rosetta::

   $ rb

To build in release mode, run the following alias instead::

   $ rr

These aliases require that either ```ninja`` or ``make`` be installed.  Most 
systems will have ``make`` installed by default, so you shouldn't have to worry 
about this.  However, ``ninja`` is preferred if both build tools are installed 
because it's faster and more succinct.

Running unit tests
==================
To compile and run a unit test suite, use the following command as a template::

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

Writing documentation
=====================
To generate doxygen documentation for whichever directory you're currently in, 
run the following command::

   $ rd

This will generate documentation and automatically present it to you in a new 
``firefox`` window.



   
   
