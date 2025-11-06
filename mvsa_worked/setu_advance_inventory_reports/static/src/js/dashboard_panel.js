/** @odoo-module **/

import { loadJS } from "@web/core/assets";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

const { Component, onMounted, onWillStart, useState } = owl;
import { renderToFragment,renderToElement } from "@web/core/utils/render";
export class SetuDashboardPanel extends Component {
    setup() {
        this.actionService = useService("action");
        this.orm = useService("orm");
        this.context = session.user_context;


        onWillStart(async () => {
        });

        onMounted(() => {
            this.initializeDashboard();
        });
    }
    async initializeDashboard() {
        const actionRequest = {
            type: "ir.actions.client",
            tag: "setu_fsn_dashboard",
        };
//        const options = { stackPosition: "replaceCurrentAction" };

        try {
            await this.actionService.doAction(actionRequest, options);
        } catch (error) {
            console.error("Error performing action:", error);
        }

//        document.querySelectorAll('.context-button').forEach(button => {
//            button.addEventListener('click', async (event) => {
//                const selectedOption = event.target.getAttribute('data-option');
//                if (selectedOption === "overstock_dashboard") {
//                    console.log('overstock');
//                    var fsn = $('div.outer_div').append(renderToElement(
//                    'SetuOverstockDashboard'
//
//                ));
//                console.log(fsn)
////                    const actionRequest = {
////                        type: "ir.actions.client",
////                        tag: "setu_overstock_dashboard",
////                    };
////                    const options = { stackPosition: "replaceCurrentAction" };
////
////                    try {
////                        await this.actionService.doAction(actionRequest, options);
////                    } catch (error) {
////                        console.error("Error performing action:", error);
////                    }
//                }
//            });
//        });


        document.querySelectorAll('.context-button').forEach(button => {
            button.addEventListener('click', async (event) => {
                const selectedOption = event.target.getAttribute('data-option');
                console.log(selectedOption)
                if (selectedOption === "overstock_dashboard") {
                    console.log('overstock');

                    const actionRequest = {
                        type: "ir.actions.client",
                        tag: "setu_overstock_dashboard",
                    };
//                    const options = { stackPosition: "replaceCurrentAction" };

                    try {
                        await this.actionService.doAction(actionRequest, options);
                    } catch (error) {
                        console.error("Error performing action:", error);
                    }
                }
            });
        });
    }
}
SetuDashboardPanel.template = "SetuDashboardPanel";
registry.category("actions").add("setu_inventory_dashboard", SetuDashboardPanel);



