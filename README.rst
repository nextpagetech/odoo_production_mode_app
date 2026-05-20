Production Mode
===============

Production Mode is an Odoo 18 addon for live databases where selected users
should not access developer mode or see technical error details in the web
client.

Main behavior
-------------

* Adds a Production Mode setting under General Settings.
* Adds a Production Mode Restricted user group.
* Blocks developer mode for restricted users when the setting is enabled.
* Removes debug flags from restricted user sessions.
* Hides backend developer controls for restricted users.
* Shows a generic administrator message for unexpected technical errors.
* Keeps normal UserError and ValidationError messages visible.
* Blocks public database manager routes when production mode is active.

Configuration
-------------

1. Install the module.
2. Enable Production Mode from Settings.
3. Add selected users to the Production Mode Restricted group.
4. Log in as one of those users and verify that debug mode is unavailable.

Notes
-----

This addon is a restriction layer for the Odoo web client and public database
manager routes. It does not replace access rights, backups, server hardening,
reverse proxy rules, monitoring, or log management.

The module does not send data to external services.
