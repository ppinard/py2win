######
py2win
######

.. image:: https://ci.appveyor.com/api/projects/status/github/ppinard/py2win?svg=true
   :target: https://ci.appveyor.com/project/ppinard/py2win

Utility to create a stand-alone distribution of a Python program,
either a console or GUI program. 
*py2win* uses `Python embedded distribution <https://docs.python.org/3.6/using/windows.html#embedded-distribution>`_ 
and *pip* to create the stand-alone distribution.

Installation
============

You first need to install Microsoft Visual Studio, compatible with your current 
Python installation. Then simply run:

.. code:: 

   pip install py2win

How to use
==========

As a command in ``setup.py``
----------------------------

1. Define at least one entry point in your ``setup.py``.

.. code:: python

   setup(
        ...
        entry_points={
            'gui_scripts': ['sample-gui=sample.gui:main'],
            'console_scripts': ['sample-console=sample.console:main'],
        },
        ...
        )
        
2. Run the ``bdist_windows`` command

.. code:: 

   python setup.py --command-packages py2win bdist_windows
   
As a separate script to create an embedded distribution
-------------------------------------------------------

.. code:: python

   from py2win.embed import EmbedPython
   
   embed = EmbedPython('sample', '1.2.0')
   embed.add_wheel(filepath_to_wheel_of_your_project)
   embed.add_script('project.gui', 'main', 'project-gui', console=False)
   embed.run(destination_directory)
   
Release notes
=============

0.1.0
-----

* First release

License
=======

The library is provided under the MIT license.

Copyright (c) 2017 Philippe Pinard
