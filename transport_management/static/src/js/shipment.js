/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useService } from "@web/core/utils/hooks";
import { useDebounced } from "@web/core/utils/timing";
import { session } from "@web/session";
import { Domain } from "@web/core/domain";
import { sprintf } from "@web/core/utils/strings";

const { Component, useSubEnv, useState, onMounted, onWillStart, useRef } = owl;
import { loadJS, loadCSS } from "@web/core/assets"

class TransportDashboard extends Component {
    setup() {
//        this.rpc = useService("rpc");
        this.action = useService("action");
        this.orm = useService("orm");

        this.state = useState({
            transportStats: { 'all': 0, 'pack': 0, 'ship': 0, 'transit': 0, 'done': 0, 'cancel': 0 },
            ordersByMonth: { 'x-axis': [], 'y-axis': [] },
            shipmentTransporters: { 'x-axis': [], 'y-axis': [] },
        });

        this.ordersByMonth = useRef('order_by_months_graph');
        this.shipmentTransporters = useRef('shipment_transporter_graph');

        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });

        onWillStart(async () => {
            let transportManagementData = await this.orm.call('transport.shipment', 'get_shipment_stats', []);
            if (transportManagementData) {
                this.state.transportStats = transportManagementData;
                this.state.ordersByMonth = { 'x-axis': transportManagementData['orders_by_month'][0], 'y-axis': transportManagementData['orders_by_month'][1] }
                this.state.shipmentTransporters = { 'x-axis': transportManagementData['shipment_transporters'][0], 'y-axis': transportManagementData['shipment_transporters'][1] }
            }
        });
        onMounted(() => {
            this.renderOrdersByMonthGraph();
            this.renderShipmentTransporterGraph();
        })
    }

    viewShipmentStats(types) {
        let domain, context;
        let transportState = this.getShipmentState(types);
        if (types === 'all') {
            domain = []
        } else {
            domain = [['status', '=', types]]
        }
        context = { 'create': false }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: transportState,
            res_model: 'transport.shipment',
            view_mode: 'kanban',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'activity']],
            target: 'current',
            context: context,
            domain: domain,
        });
    }

    getShipmentState(types) {
        let transportState;
        if (types === 'all') {
            transportState = 'Shipments'
        } else if (types === 'draft') {
            transportState = 'Packing'
        } else if (types === 'ship') {
            transportState = 'Shipped'
        } else if (types === 'in_transit') {
            transportState = 'In Transit'
        } else if (types === 'done') {
            transportState = 'Delivered'
        } else if (types === 'cancel') {
            transportState = 'Cancelled'
        }
        return transportState;
    }

    renderGraph(el, options) {
        const graphData = new ApexCharts(el, options);
        graphData.render();
    }

    renderOrdersByMonthGraph() {
        const options = {
            series: [
                {
                    name: 'Amounts',
                    data: this.state.ordersByMonth['y-axis'],
                }
            ],
            chart: {
                height: 440,
                type: 'bar',
            },
            plotOptions: {
                bar: {
                    columnWidth: '40%',
                    distributed: true,
                }
            },
            dataLabels: {
                enabled: false
            },
            legend: {
                show: false
            },
            yaxis: {
                labels: {
                    formatter: function (val) {
                        if (typeof val === 'number') {
                            return val.toFixed(0);
                        } else {
                            return val;
                        }
                    }
                },
            },
            xaxis: {
                categories: this.state.ordersByMonth['x-axis'],
                labels: {
                    style: {
                        fontSize: '13px'
                    }
                }
            }
        };
        this.renderGraph(this.ordersByMonth.el, options);
    }

    renderShipmentTransporterGraph() {
        const options = {
            series: this.state.shipmentTransporters['y-axis'],
            chart: {
                height: 430,
                type: 'polarArea',
            },
            labels: this.state.shipmentTransporters['x-axis'],
            stroke: {
                colors: ['#fff']
            },
            fill: {
                opacity: 0.8
            },
            yaxis: {
                labels: {
                    formatter: function (val) {
                        if (typeof val === 'number') {
                            return val.toFixed(0);
                        } else {
                            return val;
                        }
                    }
                },
            },
            legend: {
                position: 'bottom'
            },
            responsive: [{
                breakpoint: 480,
                options: {
                    chart: {
                        width: 200
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }]
        };
        this.renderGraph(this.shipmentTransporters.el, options);
    }
}
TransportDashboard.template = "transport_management.transport_dashboard";
registry.category("actions").add("shipment_dashboard", TransportDashboard);