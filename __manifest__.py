# -*- coding: utf-8 -*-
{
    "name": "Production Mode",
    "summary": "Restrict debug access and mask tracebacks in live databases",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "author": "Next Page Technologies Pvt Ltd",
    "website": "https://nextpagetechnologies.com",
    "support": "hello@nextpagetechnologies.com",
    "description": """
Production Mode adds a controlled restriction layer for live Odoo databases.
After the setting is enabled, restrictions apply to users assigned to the
Production Mode Restricted group.

Features:
    - Block developer mode for restricted users.
    - Remove debug flags from restricted user sessions.
    - Hide backend developer controls.
    - Mask unexpected technical errors with a generic message.
    - Keep UserError and ValidationError messages visible.
    - Block public database manager routes when production mode is active.

The module does not send data to external services.
""",
    "depends": ["web", "base_setup"],
    "post_load": "post_load",
    "data": [
        "security/production_mode_security.xml",
        "views/login_templates.xml",
        "views/res_config_settings_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "production_mode/static/src/js/error_override.js",
            "production_mode/static/src/js/production_mode_guard.js",
            "production_mode/static/src/scss/production_mode.scss",
        ],
    },
    "images": [
        "static/description/banner.png",
        "static/description/screenshot_settings.png",
        "static/description/screenshot_error.png",
        "static/description/screenshot_database_lock.png",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
