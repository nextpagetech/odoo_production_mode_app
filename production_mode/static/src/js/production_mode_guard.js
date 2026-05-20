/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { browser } from "@web/core/browser/browser";
import { Component, onMounted, xml } from "@odoo/owl";
import { ResConfigDevTool } from "@web/webclient/settings_form_view/widgets/res_config_dev_tool";

function isProductionModeEnabled() {
    return Boolean(session.production_mode_enabled);
}

function stripDebugFromLocation() {
    const url = new URL(browser.location.href);
    if (!url.searchParams.has("debug") && !odoo.debug) {
        return;
    }
    url.searchParams.delete("debug");
    browser.location.replace(url.toString());
}

export class ProductionModeGuard extends Component {
    static template = xml`<div class="d-none"/>`;

    setup() {
        onMounted(() => {
            if (!isProductionModeEnabled()) {
                return;
            }
            document.body.classList.add("o_production_mode");
            stripDebugFromLocation();
        });
    }
}

patch(ResConfigDevTool.prototype, {
    setup() {
        super.setup(...arguments);
        this.productionModeEnabled = isProductionModeEnabled();
    },
    activateDebug(value) {
        if (isProductionModeEnabled()) {
            return;
        }
        return super.activateDebug(value);
    },
});

registry.category("main_components").add("production_mode_guard", {
    Component: ProductionModeGuard,
});
