from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_production_mode = fields.Boolean(string="Enable Production Mode")

    @api.model
    def get_values(self):
        values = super().get_values()
        enabled = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("production_mode.enabled", default="False")
        )
        values["enable_production_mode"] = str(enabled).strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        return values

    def set_values(self):
        super().set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "production_mode.enabled",
            bool(self.enable_production_mode),
        )
