Toxicwebui: A (not so) nice web interface for toxicbuild
========================================================


Install
-------

To install it use pip:

.. code-block:: sh

   $ pip install toxicwebui --extra-index-url=https://pypi.poraodojuca.dev



Setup & config
--------------

Before executing builds you must create an environment for toxicwebui.
To do so use:

.. code-block:: sh

   $ toxicwebui create ~/webui-env

This is going to create a ``~/webui-env`` directory with a ``toxicwebui.conf``
file in it. This file is used to configure toxicwebui.

Check the configuration instructions for details

.. toctree::
   :maxdepth: 1

   config


Run the server
--------------

When the configuration is done you can run the server with:

.. code-block:: sh

   $ toxicwebui start ~/webui-env


For all options for the toxicwebui command execute

.. code-block:: sh

   $ toxicwebui --help



CHANGELOG
---------

.. toctree::
   :maxdepth: 1

   CHANGELOG
