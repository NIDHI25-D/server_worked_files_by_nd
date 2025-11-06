import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { useState, onWillStart } from "@odoo/owl";


patch(ControlButtons.prototype, {
    setup() {
        super.setup();
        this.state = useState({
            currentSalesTeam: _t("Sales Team")
        });
        this.pos = usePos();
        onWillStart(async () => {
            this.SalesTeamList = await rpc("/setu_pos_extended/get_sales_teams") || [];
            debugger
            const selectedSalesTeam = this.SalesTeamList.filter((x) => this.pos.get_order().sales_team_id && this.pos.get_order().sales_team_id.id === x.item);
            this.state.currentSalesTeam = selectedSalesTeam.length > 0 ? selectedSalesTeam[0].label : _t("Sales Team");
        });
    },

    async selectSalesTeam() {
        const SelectedOrder = this.pos.get_order();
        const currentsale_team = this.SalesTeamList.filter((x) => SelectedOrder.sales_team_id && SelectedOrder.sales_team_id.id === x.item);
        const sales_teamList = [
                {
                    id: -1,
                    label: _t('None'),
                    isSelected: !currentsale_team.length,
                },
            ];
            for (let saleTeam of this.SalesTeamList) {
                sales_teamList.push({
                    id: saleTeam.id,
                    label: saleTeam.label,
                    isSelected: currentsale_team
                        ? SelectedOrder.sales_team_id && saleTeam.item === SelectedOrder.sales_team_id.id
                        : false,
                    item: saleTeam.id,
                });
            }

        const payload = await makeAwaitable(this.dialog, SelectionPopup, {
            title: _t("Select Sales Team"),
            list: sales_teamList,
        });

        SelectedOrder.update({ sales_team_id: payload });
        const selectedSalesTeam = this.SalesTeamList.filter((x) => SelectedOrder.sales_team_id && SelectedOrder.sales_team_id.id === x.item)
        this.state.currentSalesTeam = selectedSalesTeam.length ? selectedSalesTeam[0].label : _t("Sales Team");
    },
});
