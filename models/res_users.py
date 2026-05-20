from odoo import api, models


_TRUTHY_VALUES = {"1", "true", "on", "yes"}
_PRODUCTION_MODE_GROUP = "production_mode.group_production_mode_restricted"


def _is_enabled(raw_value):
    return str(raw_value or "").strip().lower() in _TRUTHY_VALUES


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _is_production_mode_globally_enabled(self):
        enabled = self.env["ir.config_parameter"].sudo().get_param(
            "production_mode.enabled",
            default="False",
        )
        return _is_enabled(enabled)

    @api.model
    def _is_production_mode_enabled_for_user(self, user=None):
        user = user or self.env.user
        return bool(
            self._is_production_mode_globally_enabled()
            and user
            and user.has_group(_PRODUCTION_MODE_GROUP)
        )

    @api.model
    def has_debug_access(self, ids=None):
        if self._is_production_mode_enabled_for_user():
            return False

        parent = getattr(super(), "has_debug_access", None)
        if callable(parent):
            return parent(ids=ids)
        return False
