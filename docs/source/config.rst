Toxicwebui config
=================

The configuration of toxicwebui is done using the a configuration file. The configuration
file can be passed using the  ``-c`` flag to the ``toxicwebui`` command
or settings the environment variable ``TOXICWEBUI_SETTINGS``.

This file is a python file, so do what ever you want with it.

Config values
-------------

.. note::

   Although the config is done using a config file, the default
   configuration file created by ``toxicwebui create`` can use
   environment variables instead.


* ``PORT`` - The port for the server to listen. Defaults to `8888`.
  Environment variable: ``WEBUI_PORT``

* ``HOLE_HOST`` - Toxicmaster hole server
  Environment variable: ``HOLE_HOST``

* ``HOLE_PORT`` - Toxicmaster hole port
  Environment variable: ``HOLE_PORT``

* ``HOLE_TOKEN`` - Access token for the master.
  Environment variable: ``HOLE_TOKEN``

* ``MASTER_USES_SSL`` - Indicates if the master uses ssl connection
  Environment variable: ``MASTER_USES_SSL``

* ``VALIDADES_CERT_MASTER`` - Validate the master ssl certificate?
  Environment variable: ``VALIDATE_MASTER_CERTS``
