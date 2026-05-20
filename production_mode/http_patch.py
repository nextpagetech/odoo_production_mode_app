import odoo.http as odoo_http
from odoo import sql_db
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo.addons.web.controllers import home as web_home
from odoo.addons.web.controllers import utils as web_utils


_TRUTHY_VALUES = {"1", "true", "on", "yes"}
_GENERIC_MESSAGE = "Something went wrong. Please contact administrator."
_GENERIC_EXCEPTION_NAME = "odoo.exceptions.UserError"
_ORIGINAL_SERIALIZE_EXCEPTION = odoo_http.serialize_exception
_ORIGINAL_JSONRPC_HANDLE_ERROR = odoo_http.JsonRPCDispatcher.handle_error
_ORIGINAL_ENSURE_DB = web_utils.ensure_db
_INSTALLED = False


def _is_truthy(value):
    return str(value or "").strip().lower() in _TRUTHY_VALUES


def _should_mask_exception(exception):
    if isinstance(exception, (UserError, ValidationError)):
        return False
    try:
        if not request or not getattr(request, "env", None):
            return False
        if request.env.user._is_production_mode_enabled_for_user():
            return True
        session = getattr(request, "session", None)
        if session is not None:
            session_flag = session.get("production_mode_enabled")
            if session_flag is not None:
                return bool(session_flag)
        return False
    except Exception:
        return False


def _db_has_production_mode_enabled(dbname):
    cr = None
    try:
        cr = sql_db.db_connect(dbname).cursor()
        cr.execute(
            "SELECT value FROM ir_config_parameter WHERE key = %s",
            ["production_mode.enabled"],
        )
        row = cr.fetchone()
        return bool(row and _is_truthy(row[0]))
    except Exception:
        return False
    finally:
        if cr:
            cr.close()


def _get_production_mode_db():
    try:
        dbs = odoo_http.db_list(force=True)
    except Exception:
        return None
    if len(dbs) == 1:
        return dbs[0] if _db_has_production_mode_enabled(dbs[0]) else None
    enabled_dbs = [db for db in dbs if _db_has_production_mode_enabled(db)]
    if len(enabled_dbs) == 1:
        return enabled_dbs[0]
    return None


def ensure_db(redirect="/web/database/selector", db=None):
    # Odoo's login flow may arrive without an explicit database. If exactly one
    # database has production mode enabled, route the request to that database.
    if db is None:
        db = request.params.get("db") and request.params.get("db").strip()
    if not db and not getattr(request.session, "db", None):
        production_db = _get_production_mode_db()
        if production_db:
            db = production_db
    return _ORIGINAL_ENSURE_DB(redirect=redirect, db=db)


def serialize_exception(exception):
    data = _ORIGINAL_SERIALIZE_EXCEPTION(exception)
    if not _should_mask_exception(exception):
        return data
    data["name"] = _GENERIC_EXCEPTION_NAME
    data["debug"] = ""
    data["message"] = _GENERIC_MESSAGE
    data["arguments"] = [_GENERIC_MESSAGE]
    data["context"] = {}
    return data


def jsonrpc_handle_error(self, exception):
    error = {
        "code": 200,
        "message": _GENERIC_MESSAGE if _should_mask_exception(exception) else "Odoo Server Error",
        "data": serialize_exception(exception),
    }
    if isinstance(exception, odoo_http.NotFound):
        error["code"] = 404
        error["message"] = "404: Not Found"
    elif isinstance(exception, odoo_http.SessionExpiredException):
        error["code"] = 100
        error["message"] = "Odoo Session Expired"

    return self._response(error=error)


def install():
    global _INSTALLED
    if _INSTALLED:
        return
    # These hooks sit below regular model/controller code, so they are installed
    # once at server load and guarded against duplicate patching.
    odoo_http.serialize_exception = serialize_exception
    odoo_http.JsonRPCDispatcher.handle_error = jsonrpc_handle_error
    web_utils.ensure_db = ensure_db
    web_home.ensure_db = ensure_db
    _INSTALLED = True
