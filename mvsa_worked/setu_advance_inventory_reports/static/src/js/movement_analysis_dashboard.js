/** @odoo-module **/

import { loadJS } from "@web/core/assets";
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
import { session } from '@web/session';
import { Component, onMounted, useState, onWillStart} from "@odoo/owl";

export class SetuStockMovementDashboard extends Component {
    setup() {
        this.actionService = useService("action");
        this.orm = useService('orm');
        const context = session.user_context;

        this.stock_movement_data = null
        this.total_category_name = null
        this.warehouse_stock_movement_data = null
        this.categorized_stock_movement_data = null

        // Initialize the selected dates as null initially
        this.initStartDate = null;
        this.initEndDate = null;

        var barChart = null;
        var stackChart = null;

        onWillStart(async () => {
            await loadJS("https://cdn.jsdelivr.net/npm/apexcharts");
        });

        onMounted(() => {
            this.initializeDashboard();
        });
    }

    validateDates(new_start_Date, new_end_Date) {
        const startDate = new_start_Date;
        const endDate = new_end_Date;

        if (startDate && endDate) {
            // If end date is less than start date, show an alert
            if (endDate < startDate) {
                document.querySelector('.end-date').value = startDate || '';
            }
        }
    };

    async initializeDashboard(){
        const loader = document.querySelector('.loader');
            if (loader) {
                loader.classList.remove('hidden');
                console.log('Loader should be visible now.');
            }

            try {
                const context = session.user_context;
                const today = new Date();
                const past90Days = new Date();
                past90Days.setDate(today.getDate() - 90);

                this.initStartDate = past90Days.toLocaleDateString('en-CA');
                this.initEndDate = today.toLocaleDateString('en-CA');

                this.stock_movement_data = await this.orm.call('setu.stock.movement.inventory.dashboard', 'get_stock_movement_analysis_data', [this.initStartDate, this.initEndDate], { context });
                this.evaluateData();
            } catch (error) {
                console.error("Error loading out-of-stock data:", error);
            } finally {
                if (loader) {
                    document.querySelector(".loader_main").style.display = 'none';
                    document.querySelector(".loader_2").style.display = 'none';
                    document.querySelector(".loader_3").style.display = 'none';
                    document.querySelector(".loader_4").style.display = 'none';
                    document.querySelector(".loader_5").style.display = 'none';
                    document.querySelector(".loader_6").style.display = 'none';
                }
            }
        const defaultLi = document.getElementById('movement_analysis');  // This will select the first li element
        if (defaultLi) {
            defaultLi.classList.add('active');
        }

        document.querySelector('.start-date').value = this.initStartDate || '';
        document.querySelector('.end-date').value = this.initEndDate || '';

        document.querySelectorAll('.filter-button').forEach(button => {
            button.addEventListener('click', async (event) => {
                const new_start_Date = document.querySelector('.start-date').value;
                const new_end_Date = document.querySelector('.end-date').value;

                this.validateDates(new_start_Date, new_end_Date);

                const context = { ...session.user_context, startDate: new_start_Date, endDate:new_end_Date };
                    console.log("Start Date:", new_start_Date);
                    console.log("End Date:", new_end_Date);

                    this.stock_movement_data = await this.orm.call('setu.stock.movement.inventory.dashboard', 'get_stock_movement_analysis_data', [new_start_Date, new_end_Date], { context });


                    this.evaluateData();
            });
        });

        document.querySelectorAll('.context-button').forEach(button => {
            button.addEventListener('click', async (event) => {
                const selectedOption = event.target.getAttribute('data-option');
                console.log(selectedOption);

                // Map options to their respective actions
                const actions = {
                    "fsn_dashboard": ["setu_fsn_dashboard", "FSN Dashboard"],
                    "xyz_dashboard": ["setu_xyz_dashboard", "XYZ Dashboard"],
                    "fsn_xyz_dashboard": ["setu_fsn_xyz_dashboard", "FSN-XYZ Dashboard"],
                    "overstock_dashboard": ["setu_overstock_dashboard", "OverStock Dashboard"],
                    "outofstock_dashboard": ["setu_outofstock_dashboard", "OutOfStock Dashboard"],
                    "movement_dashboard": ["setu_stock_movement_dashboard", "Movement Dashboard"],
                    "age_breakdown_dashboard": ["setu_age_breakdown_analysis_dashboard", "Age Breakdown Dashboard"],
                };

                // Check if the selected option has a corresponding action
                if (actions[selectedOption]) {
                    const actionRequest = {
                        type: "ir.actions.client",
                        tag: actions[selectedOption][0],
                        name: actions[selectedOption][1],
                    };
                    const options = { stackPosition: "replaceCurrentAction" }; // Re-add options if needed

                    try {
                        await this.actionService.doAction(actionRequest, options);
                    } catch (error) {
                        console.error("Error performing action:", error);
                    }
                } else {
                    console.warn("Unknown dashboard option selected:", selectedOption);
                }
            });
        });
    };

    evaluateData(){
        // Dashboard Data
        const stock_movement_data = this.stock_movement_data;
        const custom_click_action = stock_movement_data.final_action_click || ''

        // Evaluate the data for the charts
        this.total_category_name = stock_movement_data.total_category_name || []
        this.warehouse_stock_movement_data = stock_movement_data.warehouse_stock_movement_data || {}
        this.categorized_stock_movement_data = stock_movement_data.categorized_stock_movement_data || {}

        document.querySelector('.total_product_count').textContent = stock_movement_data.total_product_count || 0
        document.querySelector('.class_sale_stock').textContent = stock_movement_data.total_sale_stock || 0
        document.querySelector('.class_sale_return_stock').textContent = stock_movement_data.total_sale_return_stock || 0
        document.querySelector('.class_purchase_stock').textContent = stock_movement_data.total_purchase_stock || 0
        document.querySelector('.class_purchase_return_stock').textContent = stock_movement_data.total_purchase_return_stock || 0
        document.querySelector('.class_adjustment_in_stock').textContent = stock_movement_data.total_adjustment_in_stock || 0
        document.querySelector('.class_adjustment_out_stock').textContent = stock_movement_data.total_adjustment_out_stock || 0

        this.stockMovementByWarehouse(custom_click_action);
        this.stockMovementByProductCategory(custom_click_action);

        this.actions(custom_click_action)
    }
    actions(custom_click_action){
        document.querySelector('.stock_mv_wh').addEventListener('click', () => {
             let data_action = custom_click_action;
                if (data_action){
                    console.log(data_action);
                    data_action.context = {group_by: ["warehouse_id"]}
                    this.actionService.doAction(data_action);
                }
        });
        document.querySelector('.stock_mv_cg').addEventListener('click', () => {
             let data_action = custom_click_action;
                if (data_action){
                    console.log(data_action);
                    data_action.context = {group_by: ["product_category_id"]}
                    this.actionService.doAction(data_action);
                }
        });
    }
    stockMovementByWarehouse(line_action){
        const warehouses_data = this.warehouse_stock_movement_data;
        const warehouses_name = Object.keys(warehouses_data);
        const warehouses_data_values = Object.values(warehouses_data);
        const label_movement = Object.keys(warehouses_data_values[0]);
        const barBackgroundColor = this.generateColorPalette(warehouses_name.length)


        var my_series = [];
        Object.keys(warehouses_data).forEach(location => {
            my_series.push({
                name: location,
                data: Object.values(warehouses_data[location])
            });
        });

        var options = {
            series: my_series,
            colors: barBackgroundColor,
            chart: {
                type: 'bar',
                width: '100%',
                height: '100%',
                toolbar: {
                    show: false,
                },
//                events: {
//                    click: (e) => {
//                        let data_action = line_action;
//                        if (data_action){
//                            console.log(data_action);
//                            data_action.context = {'group_by': ['warehouse_id']}
//                            this.actionService.doAction(data_action);
//                        }
//                    },
//                },
            },
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: '60%',
                    borderRadius: 2,
                    borderRadiusApplication: 'end',
                    dataLabels: {
                        position: 'top', // top, center, bottom
                    },
                },
            },
            dataLabels: {
                enabled: true,
                offsetY: -10,
                formatter: function (val) {
                    if (val == 0){val = '';};
                    return val;
                },
                style: {
                    fontSize: '0.7vw',
                    colors: ["#304758"]
                }
            },
            legend: {
                show: true,
                showForSingleSeries: true,
                horizontalAlign: 'right',
                position: 'top',
            },
            stroke: {
                show: true,
                width: 2,
                colors: ['transparent']
            },
            xaxis: {
                title: {
                    text: 'Stock Movement'
                },
                categories: label_movement,
                grid: {
                    xaxis: {
                        lines: {
                            show: true, // Show the grid lines under the x-axis
                        }
                    },
                },
            },
            yaxis: {
                title: {
                    text: 'Count',
                },
            },
            fill: {
                opacity: 1
            },
        };

        if (this.barChart){
            this.barChart.destroy();
        }

        this.barChart = new ApexCharts(document.querySelector("#stockMovementByWarehouse"), options);
        this.barChart.render();
    };

    stockMovementByProductCategory(line_action){
        const categorized_data = this.categorized_stock_movement_data;
        const category_name = Object.keys(categorized_data);
        const first_category_data = Object.values(categorized_data)[0];
        const categories_data_keys = Object.keys(first_category_data);
        const categories_data_values = Object.values(categorized_data);
        const stackBackgroundColor = this.generateColorPalette(categories_data_keys.length)

        var data_series = [];

        // Iterate over the keys of the first object in the data array
        Object.keys(categories_data_values[0]).forEach(key => {
            let dataForKey = {
                name: key,
                data: categories_data_values.map(entry => entry[key])
            };
            data_series.push(dataForKey);
        });

        console.log(data_series);

        var options = {
            series: data_series,
            colors: stackBackgroundColor,
            chart: {
                type: 'bar',
                width: '100%',
                height: '100%',
                stacked: true,
                toolbar: {
                    show: false,
                },
                zoom: {
                    enabled: true,
                },
                events: {
//                    click: (e) => {
//                        let data_action = line_action;
//                        if (data_action){
//                            console.log(data_action);
//                            data_action.context = {'group_by': ['product_category_id']}
//                            this.actionService.doAction(data_action);
//                        }
//                    },
                },
            },
            dataLabels: {
                enabled: true,
                offsetY: -10,
                formatter: function (val) {
                    if (val == 0){val = '';};
                    return val;
                },
                style: {
                    fontSize: '0.7vw',
                    colors: ["#ffffff"]
                }
            },
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: '30%',
                    borderRadius: 10,
                    borderRadiusApplication: 'end', // 'around', 'end'
                    borderRadiusWhenStacked: 'last', // 'all', 'last'
                },
            },
            xaxis: {
                categories: category_name,
                title: {
                    text: 'Category',
                },
            },
            yaxis: {
                title: {
                    text: 'Count',
                },
            },
            legend: {
                position: 'top',
            },
            fill: {
                opacity: 1
            }
        };

        if (this.stackChart){
            this.stackChart.destroy();
        }

        this.stackChart = new ApexCharts(document.querySelector("#stockMovementByProductCategory"), options);
        this.stackChart.render();
    };

    generateColorPalette(numColors){
        const colors = [];
        const baseColors = [
            'rgba(16, 177, 142, 1)',   // Persian Green
            'rgba(17, 136, 248, 1)',   // Dodger Blue

            'rgba(0, 123, 151, 1)',    // CG Blue
            'rgba(142, 36, 170, 0.9)', // Purple
            'rgba(255, 165, 0, 0.9)',  // Bright Orange
            'rgba(254, 204, 2, 1)',    // Philippine Yellow
            'rgba(244, 67, 54, 1)',    // Deep Red
            'rgba(3, 74, 131, 1)',     // Dark Cerulean
            'rgba(243, 114, 119, 1)',  // Begonia
            'rgba(71, 198, 207, 1)',   // Sea Serpent
            'rgba(255, 102, 51, 1)',   // Smashed Pumpkin
            'rgba(250, 60, 72, 1)',    // Red Salsa
            'rgba(0, 128, 128, 1)',    // Dark Teal
            'rgba(128, 100, 200, 1)',  // Lavender
            'rgba(63, 81, 181, 1)',    // Indigo
            'rgba(0, 188, 212, 1)',    // Aqua
            'rgba(232, 189, 137, 1)',  // Gold (Crayola)
            'rgba(102, 187, 106, 1)',  // Green
            'rgba(255, 235, 59, 1)',   // Bright Yellow
            'rgba(96, 125, 139, 1)',   // Blue Grey
            'rgba(128, 0, 128, 1)',    // Dark Purple
            'rgba(0, 255, 127, 1)',    // Spring Green
            'rgba(3, 169, 244, 1)',    // Light Blue
            'rgba(238, 130, 238, 1)',  // Violet
            'rgba(70, 130, 180, 1)',   // Steel Blue
            'rgba(169, 169, 169, 1)',  // Dark Grey
            'rgba(133, 133, 255, 1)',  // Violets Are Blue
            'rgba(121, 85, 72, 1)',    // Brown
            'rgba(76, 74, 75, 1)',     // Quartz
            'rgba(0, 255, 255, 1)',    // Cyan
            'rgba(103, 58, 183, 1)',   // Deep Purple
        ];

        for (let i = 0; i < numColors; i++) {
            colors.push(baseColors[i % baseColors.length]);
        }

        return colors;
    };
}
SetuStockMovementDashboard.template = 'SetuStockMovementDashboard';
registry.category('actions').add('setu_stock_movement_dashboard', SetuStockMovementDashboard);
