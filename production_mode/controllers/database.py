from odoo import http, sql_db
from odoo.addons.web.controllers.database import Database as WebDatabase
from odoo.http import request
from werkzeug.exceptions import NotFound


_TRUTHY_VALUES = {"1", "true", "on", "yes"}


def _is_truthy(value):
    return str(value or "").strip().lower() in _TRUTHY_VALUES


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
        dbs = http.db_list(force=True)
    except Exception:
        return None
    if len(dbs) == 1:
        return dbs[0] if _db_has_production_mode_enabled(dbs[0]) else None
    enabled_dbs = [db for db in dbs if _db_has_production_mode_enabled(db)]
    if len(enabled_dbs) == 1:
        return enabled_dbs[0]
    return None


def _database_surface_locked():
    try:
        dbname = getattr(request.session, "db", None) or request.params.get("db")
        if not dbname:
            return False
        return _db_has_production_mode_enabled(dbname)
    except Exception:
        return False


def _database_redirect_target():
    dbname = _get_production_mode_db()
    if dbname:
        return f"/web/login?db={dbname}"
    return "/web/login"


class ProductionModeDatabase(WebDatabase):
    # Database manager routes are public in Odoo. When production mode is active,
    # keep that surface unavailable instead of relying only on the page UI.
    @http.route('/web/database/selector', type='http', auth="none")
    def selector(self, **kw):
        if _database_surface_locked():
            return request.redirect(_database_redirect_target(), 303)
        production_db = _get_production_mode_db()
        if production_db:
            return request.redirect(_database_redirect_target(), 303)
        return super().selector(**kw)

    @http.route('/web/database/manager', type='http', auth="none")
    def manager(self, **kw):
        if _database_surface_locked() or _get_production_mode_db():
            raise NotFound()
        return super().manager(**kw)

    @http.route('/web/database/create', type='http', auth="none", methods=['POST'], csrf=False)
    def create(self, *args, **kwargs):
        if _database_surface_locked() or _get_production_mode_db():
            raise NotFound()
        return super().create(*args, **kwargs)

    @http.route('/web/database/duplicate', type='http', auth="none", methods=['POST'], csrf=False)
    def duplicate(self, *args, **kwargs):
        if _database_surface_locked() or _get_production_mode_db():
            raise NotFound()
        return super().duplicate(*args, **kwargs)

    @http.route('/web/database/drop', type='http', auth="none", methods=['POST'], csrf=False)
    def drop(self, *args, **kwargs):
        if _database_surface_locked() or _get_production_mode_db():
            raise NotFound()
        return super().drop(*args, **kwargs)

    @http.route('/web/database/backup', type='http', auth="none", methods=['POST'], csrf=False)
    def backup(self, *args, **kwargs):
        if _database_surface_locked() or _get_production_mode_db():
            raise NotFound()
        return super().backup(*args, **kwargs)

    @http.route('/web/database/restore', type='http', auth="none", methods=['POST'], csrf=False, max_content_length=None)
    def restore(self, *args, **kwargs):
        if _database_surface_locked() or _get_production_mode_db():
            raise NotFound()
        return super().restore(*args, **kwargs)

    @http.route('/web/database/change_password', type='http', auth="none", methods=['POST'], csrf=False)
    def change_password(self, *args, **kwargs):
        if _database_surface_locked() or _get_production_mode_db():
            raise NotFound()
        return super().change_password(*args, **kwargs)

    @http.route('/web/database/list', type='json', auth='none')
    def list(self, *args, **kwargs):
        if _database_surface_locked():
            return []
        return super().list(*args, **kwargs)
