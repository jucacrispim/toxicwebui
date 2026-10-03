Changelog
=========

* v0.12.0

  - Bind the ToxicBuild user id to the oauth ``state`` in the import urls
    (``_get_import_url`` helper), so the integrations service can identify
    the user without relying on the session cookie.
  - GitHub: also send the signed ``state`` in the import url
    (``_get_github_import_url``).
  - Requires ``toxiccore>=0.14.0`` (``create_validation_string`` now
    supports carrying data).

* v0.11.1

  - Fix ``create`` to read the config template from the ``toxicwebui``
    package instead of ``toxicmaster``

* v0.11.0

  - Migrated `toxicwebui` from HTTP transport to TCP for notifications using
    `toxiccore`'s `BaseToxicClient`.

* V0.10.1

  - Fix packaging

* v0.10.0

  - First version on its own repo outside toxicuild
