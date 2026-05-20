/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ConnectionLostError, RPCError } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { WarningDialog } from "@web/core/errors/error_dialogs";
import {
    ThirdPartyScriptError,
    UncaughtClientError,
    UncaughtPromiseError,
} from "@web/core/errors/error_service";
import { session } from "@web/session";

const GENERIC_MESSAGE = _t("Something went wrong. Please contact administrator.");
const FUNCTIONAL_EXCEPTIONS = new Set([
    "odoo.exceptions.UserError",
    "odoo.exceptions.ValidationError",
    "odoo.exceptions.RedirectWarning",
    "odoo.http.SessionExpiredException",
]);

function isProductionModeEnabled() {
    return Boolean(session.production_mode_enabled);
}

function isFunctionalRpcError(originalError) {
    const exceptionName =
        originalError?.exceptionName ||
        originalError?.data?.name ||
        originalError?.data?.context?.exception_class ||
        "";
    return FUNCTIONAL_EXCEPTIONS.has(exceptionName);
}

function showGenericDialog(env) {
    env.services.dialog.add(WarningDialog, {
        title: _t("Error"),
        message: GENERIC_MESSAGE,
        exceptionName: "odoo.exceptions.UserError",
        data: {
            arguments: [GENERIC_MESSAGE],
        },
    });
}

function productionRpcErrorHandler(env, error, originalError) {
    if (!isProductionModeEnabled()) {
        return false;
    }
    if (!(error instanceof UncaughtPromiseError) || !(originalError instanceof RPCError)) {
        return false;
    }
    if (isFunctionalRpcError(originalError)) {
        return false;
    }
    error.unhandledRejectionEvent.preventDefault();
    showGenericDialog(env);
    return true;
}

function productionClientErrorHandler(env, error, originalError) {
    if (!isProductionModeEnabled()) {
        return false;
    }
    if (originalError instanceof ConnectionLostError) {
        return false;
    }
    if (originalError instanceof RPCError) {
        return false;
    }
    if (
        error instanceof UncaughtClientError ||
        error instanceof ThirdPartyScriptError ||
        error instanceof UncaughtPromiseError
    ) {
        showGenericDialog(env);
        return true;
    }
    return false;
}

registry.category("error_handlers").add("productionRpcErrorHandler", productionRpcErrorHandler, {
    sequence: 96,
});
registry
    .category("error_handlers")
    .add("productionClientErrorHandler", productionClientErrorHandler, { sequence: 99 });
