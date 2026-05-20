from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _is_production_mode_enabled_for_request(cls):
        try:
            if request and getattr(request, "env", None):
                return request.env.user._is_production_mode_enabled_for_user()
            if request and getattr(request, "session", None) is not None:
                session_flag = request.session.get("production_mode_enabled")
                if session_flag is not None:
                    return bool(session_flag)
        except Exception:
            return False
        return False

    @classmethod
    def _handle_debug(cls):
        super()._handle_debug()
        if cls._is_production_mode_enabled_for_request() and getattr(request, "session", None) is not None:
            request.session.debug = ""

    def _append_production_mode_session_info(self, info):
        enabled = self.env.user._is_production_mode_enabled_for_user()
        info["production_mode_enabled"] = enabled
        info["production_mode_hide_developer_tools"] = enabled
        if request and getattr(request, "session", None) is not None:
            request.session["production_mode_enabled"] = enabled
            if enabled:
                request.session.debug = ""
        if enabled and isinstance(info.get("bundle_params"), dict):
            info["bundle_params"].pop("debug", None)
        return info

    def session_info(self):
        info = super().session_info()
        return self._append_production_mode_session_info(info)

    def get_frontend_session_info(self):
        info = super().get_frontend_session_info()
        return self._append_production_mode_session_info(info)
