Production Mode
===============

Production Mode adds a restriction layer for live Odoo databases. It is meant
for installations where selected users should not see developer tools, debug
mode, or technical error details in the web client.

Features
--------

* Enable or disable the module from General Settings.
* Apply restrictions only to users in the Production Mode Restricted group.
* Block developer mode for restricted users.
* Remove debug flags from restricted user sessions.
* Hide backend developer controls.
* Show a generic administrator message for unexpected technical errors.
* Keep UserError and ValidationError messages visible.
* Block public database manager routes when production mode is active.

Configuration
-------------

1. Install the Production Mode module.
2. Go to Settings > Production Mode.
3. Enable the Production Mode option.
4. Open the user records that should be restricted.
5. Add those users to the Production Mode Restricted group.

How It Works
------------

The global setting is stored in ``ir.config_parameter`` using the key
``production_mode.enabled``. A user is restricted only when this setting is
enabled and the user belongs to the Production Mode Restricted group.

For restricted users, the module clears debug mode from the session and removes
debug parameters from backend session data. The backend assets hide developer
controls and show a generic dialog for unexpected server or client errors.
Functional business errors remain visible.

Database Protection
-------------------

When production mode is detected for a database, public database manager routes
such as create, duplicate, drop, backup, restore, and change password are
blocked.

Limitations
-----------

This module does not replace Odoo access rights, database backups, reverse proxy
security, server monitoring, or log management. Technical details may still be
available in server logs for administrators.

Data Privacy
------------

This module does not collect, transmit, or process customer data through any
external service.
