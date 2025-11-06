/** @odoo-module **/
debugger
import { ActivityMenu } from "@mail/core/web/activity_menu";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useComponent, useEnv } from "@odoo/owl";

patch(ActivityMenu.prototype,{
    setup() {
        super.setup();
        this.action = useService("action");
    },
    useOpenWizard() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'login.activity',
            target: 'new',
            views: [[false, 'form']],
        });
    }
});