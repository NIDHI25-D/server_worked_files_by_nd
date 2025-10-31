/** @odoo-module **/
import { patch } from "@web/core/utils/patch";

import { BankRecKanbanController } from "@account_accountant/components/bank_reconciliation/kanban";
patch(BankRecKanbanController.prototype, {

    notebookPOSInvoiceListViewProps(){
        return {
            type: "list",
            noBreadcrumbs: true,
            resModel: "associate.pos.invoice.to.bank.statement",
            allowSelectors: false,
            searchViewId: false,
        };
    },


});