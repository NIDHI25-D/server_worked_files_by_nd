/** @odoo-module **/

import { loadJS } from "@web/core/assets";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { Component, onMounted, onWillStart, useState } from "@odoo/owl";

export class SetuOutOfStockDashboard extends Component {
    setup() {
        this.actionService = useService("action");
        this.orm = useService("orm");
        this.context = session.user_context;
        this.outOfStockData = null;
        this.company_currency_symbol = null;
        this.line_action = null;
        this.final_action = null;
        this.out_of_stock_qty_by_warehouse = null;
        this.out_of_stock_qty_by_product_category = null;
        this.fsn_count = null;
        // Initialize the selected dates as null initially
        this.initStartDate = null;
        this.initEndDate = null;
        this.stockDays = null;

        let warehouse_wiseProdCount_chart = null
        let warehouseWiseProductValuation_chart = null

        let categoryByProductCount_chart = null
        let categoryByproductValuation_chart = null
        let outofstockByFSN_chart = null

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

    async initializeDashboard() {
        const loader = document.querySelector('.loader');
            if (loader) {
                loader.classList.remove('hidden'); // Show loader
                console.log('Loader should be visible now.');
            }

            try {
                // Fetch the out-of-stock data
                const today = new Date();
                const past90Days = new Date();
                past90Days.setDate(today.getDate() - 90);

                this.initStartDate = past90Days.toLocaleDateString('en-CA');
                this.initEndDate = today.toLocaleDateString('en-CA');
                this.stockDays = '30';

                this.outOfStockData = await this.orm.call("setu.out.of.stock.dashboard", "return_out_of_stock_analysis", [this.initStartDate, this.initEndDate, this.stockDays], { context: this.context });
                this.evaluateData();
            } catch (error) {
                console.error("Error loading out-of-stock data:", error);
            } finally {
                if (loader || document.querySelector(".loader_2")) {
                    document.querySelector(".loader_main").style.display = 'none';
                    document.querySelector(".loader_2").style.display = 'none';
                    document.querySelector(".loader_3").style.display = 'none';
                    document.querySelector(".loader_4").style.display = 'none';
                    //document.querySelector(".loader_5").style.display = 'none';
                    document.querySelector(".loader_6").style.display = 'none';
                    document.querySelector(".loader_7").style.display = 'none';
                    document.querySelector(".loader_8").style.display = 'none';
                    document.querySelector(".loader_9").style.display = 'none';
                }
            }
        const defaultLi = document.getElementById('out_of_stock_analysis');  // This will select the first li element
        if (defaultLi) {
            defaultLi.classList.add('active');
        }

        document.querySelector('.start-date').value = this.initStartDate || '';
        document.querySelector('.end-date').value = this.initEndDate || '';
        document.querySelector('.stock-days').value = this.stockDays || '';

        document.querySelectorAll('.filter-button').forEach(button => {
            button.addEventListener('click', async (event) => {
                const new_start_Date = document.querySelector('.start-date').value;
                const new_end_Date = document.querySelector('.end-date').value;
                const new_stock_days = document.querySelector('.stock-days').value;

                this.validateDates(new_start_Date, new_end_Date);

                const context = { ...session.user_context, startDate: new_start_Date, endDate:new_end_Date, stockDays:new_stock_days };
                console.log("Start Date:", new_start_Date);
                console.log("End Date:", new_end_Date);

                this.outOfStockData = await this.orm.call("setu.out.of.stock.dashboard", "return_out_of_stock_analysis", [new_start_Date, new_end_Date, new_stock_days], { context });
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
                        params: { timestamp: new Date().getTime() }
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

    }

    evaluateData(){
        const outOfStockData = this.outOfStockData;
        this.company_currency_symbol = outOfStockData.company_currency_symbol;

        this.line_action = outOfStockData.final_line_action || 0
        this.final_action = outOfStockData.final_action || 0
        this.out_of_stock_qty_by_warehouse = outOfStockData.out_of_stock_qty_by_warehouse;
        this.out_of_stock_qty_by_product_category = outOfStockData.out_of_stock_qty_by_product_category;
        this.fsn_count = outOfStockData.out_of_stock_qty_by_stock_movement;

        document.querySelector('.company_currency_symbol').textContent = outOfStockData.company_currency_symbol || '';
        document.querySelector('.total_prod').textContent = outOfStockData.total_prod || 0;
        document.querySelector('.overall_stock_valuation').textContent = this.abbreviateNumber(outOfStockData.overall_stock_valuation || 0);
        document.querySelector('.out_of_stock_product_count').textContent = outOfStockData.out_of_stock_product_count || 0;
        document.querySelector('.fast_moving_count').textContent = outOfStockData.out_of_stock_qty_by_stock_movement['Fast Moving'] || 0;
        document.querySelector('.slow_moving_count').textContent = outOfStockData.out_of_stock_qty_by_stock_movement['Slow Moving'] || 0;
        document.querySelector('.non_moving_count').textContent = outOfStockData.out_of_stock_qty_by_stock_movement['Non Moving'] || 0;

        this.warehouse_wiseProdCount();
        this.warehouseWiseProductValuation();
        this.categoryByProductCount();
        this.categoryByproductValuation();
        //this.outofstockByFSN()
        var action_1 = outOfStockData.final_line_action || 0
        var action_2 = outOfStockData.final_action || 0
        this.actions(action_1,action_2);
    }
    actions(action_1,action_2){
        document.querySelector('.stock_count_wh').addEventListener('click', () => {
             let data_action = action_1;
                if (data_action){
                    console.log(data_action);
                    data_action.context = {group_by: ["warehouse_id"]}
                    this.actionService.doAction(data_action);
                }
        });
        document.querySelector('.stock_count_cg').addEventListener('click', () => {
             let data_action = action_1;
                if (data_action){
                    console.log(data_action);
                    data_action.context = {group_by: ["product_category_id"]}
                    this.actionService.doAction(data_action);
                }
        });
        document.querySelector('.stock_value_cg').addEventListener('click', () => {
             let data_action = action_1;
                if (data_action){
                    console.log(data_action);
                    data_action.context = {group_by: ["product_category_id"]}
                    this.actionService.doAction(data_action);
                }
        });
        document.querySelector('.stock_value_wh').addEventListener('click', () => {
             let data_action = action_1;
                if (data_action){
                    console.log(data_action);
                    data_action.context = {group_by: ["warehouse_id"]}
                    this.actionService.doAction(data_action);
                }
        });
//        document.querySelector('.stock_fsn').addEventListener('click', () => {
//             let data_action = action_2;
//                if (data_action){
//                    console.log(data_action);
//                    data_action.context = {group_by: ["stock_movement"]}
//                    this.actionService.doAction(data_action);
//                }
//        });
    }
    warehouse_wiseProdCount() {
    if (this.warehouse_wiseProdCount_chart){
        this.warehouse_wiseProdCount_chart.destroy();
    }

    const out_of_stock = this.out_of_stock_qty_by_warehouse;

    const labels = Object.keys(out_of_stock);
    const dataset_label = ['Out of Stock product count'];
    const prod_count = Object.values(out_of_stock).map(list => list[0]);
    const barBGColor = this.generateColorPalette(dataset_label.length);

    var options = {
        series: [{
            name: dataset_label[0], // Use the dataset label for the series name
            data: prod_count
        }],
        chart: {
            height: '100%',
            width: '100%',
            type: 'bar',
//            events: {
//                click: (e) => {
//                    this.actionService.doAction({
//                            ...this.line_action,
//                            context: { ...this.line_action.context, group_by: ["warehouse_id"]},
//                        });
//                }
//            },
            toolbar: {
                show: false
            }
        },
        plotOptions: {
            bar: {
                borderRadius: 10,
                columnWidth: '10%',
                dataLabels: {
                    position: 'top', // top, center, bottom
                },
            }
        },
        dataLabels: {
            enabled: true,
            offsetY: -20,
            style: {
                fontSize: '12px',
                colors: ["#304758"]
            }
        },
        xaxis: {
            categories: labels,
            position: 'bottom',
            axisBorder: {
                show: false
            },
            axisTicks: {
                show: false
            },
            crosshairs: {
                fill: {
                    type: 'gradient',
                    gradient: {
                        colorFrom: '#D8E3F0',
                        colorTo: '#BED1E6',
                        stops: [0, 100],
                        opacityFrom: 0.4,
                        opacityTo: 0.5,
                    }
                }
            },
            tooltip: {
                enabled: true
            },
            title: {
                text: 'Warehouse'
            }
        },
        yaxis: {
            axisBorder: {
                show: true
            },
            axisTicks: {
                show: true
            },
            labels: {
                show: true
            },
            title: {
                text: 'Count'
            }
        },
    };

    this.warehouse_wiseProdCount_chart = new ApexCharts(document.querySelector("#inventoryBarChartByWarehouseProdCount"), options);
    this.warehouse_wiseProdCount_chart.render();
}

    warehouseWiseProductValuation(){
        if (this.warehouseWiseProductValuation_chart){
            this.warehouseWiseProductValuation_chart.destroy();
        }
        const fsn_count = this.fsn_count;
        const labels = Object.keys(fsn_count);
        const fsn = Object.values(fsn_count);
        var options = {
          series: fsn,
          chart: {
          type: 'polarArea',
          width: '100%',
          height:'100%',
//          events: {
//                dataPointSelection: (event, chartContext, config) => {
//                    this.actionService.doAction({
//                        ...this.line_action,
//                        context: { ...this.line_action.context, group_by: ["product_category_id"] },
//                    });
//                }
//            }
        },
        stroke: {
          colors: ['#fff']
        },
        fill: {
          opacity: 0.8
        },
        legend: {
            position: 'top',
            horizontalAlign: 'center'
        },
        responsive: [{
          breakpoint: 480,
          options: {
            chart: {
              width: '100%',
              height:'100%',
            },
            legend: {
              position: 'top'
//              horizontalAlign: 'center',
            }
          }
        }],
        labels: labels,
        };

        this.warehouseWiseProductValuation_chart = new ApexCharts(document.querySelector("#inventoryBarChartByWarehouseProdValuation"), options);
        this.warehouseWiseProductValuation_chart.render();
    }

    categoryByProductCount() {
    if (this.categoryByProductCount_chart){
        this.categoryByProductCount_chart.destroy();
    }
    const out_of_stock = this.out_of_stock_qty_by_product_category;

    const labels = Object.keys(out_of_stock);
    const prod_count = Object.values(out_of_stock).map(list => list[0]);
    const barBGColor = this.generateColorPalette(labels.length);

    var options = {
        series: prod_count,
        chart: {
            type: 'polarArea',
            width: '100%',
            height: '100%',
//            events: {
//                dataPointSelection: (event, chartContext, config) => {
//                    this.actionService.doAction({
//                        ...this.line_action,
//                        context: { ...this.line_action.context, group_by: ["product_category_id"] },
//                    });
//                }
//            }
        },
        stroke: {
            colors: ['#fff']
        },
        fill: {
            opacity: 0.8
        },
        legend: {
            position: 'top',
            horizontalAlign: 'center'
        },
        responsive: [{
            breakpoint: 480,
            options: {
                chart: {
                    width: '100%',
                    height: '100%',
                },
                legend: {
                    position: 'top'
                }
            }
        }],
        labels: labels,
    };

    this.categoryByProductCount_chart = new ApexCharts(document.querySelector("#inventoryPolarChartByCategoryProdCount"), options);
    this.categoryByProductCount_chart.render();
}

    categoryByproductValuation(){
        if(this.categoryByproductValuation_chart){
            this.categoryByproductValuation_chart.destroy();
        }
        const out_of_stock = this.out_of_stock_qty_by_product_category;
        const labels = Object.keys(out_of_stock);
        const prod_valuation = Object.values(out_of_stock).map(list => list[1]);
        const bgColor = this.generateColorPalette(labels.length);
        var options = {
          series: prod_valuation,
          chart: {
          type: 'polarArea',
          width: '100%',
          height:'100%',
//          events: {
//                dataPointSelection: (event, chartContext, config) => {
//                    this.actionService.doAction({
//                        ...this.line_action,
//                        context: { ...this.line_action.context, group_by: ["product_category_id"] },
//                    });
//                }
//            }
        },
        stroke: {
          colors: ['#fff']
        },
        fill: {
          opacity: 0.8
        },
        legend: {
            position: 'top',
            horizontalAlign: 'center'
        },
        responsive: [{
          breakpoint: 480,
          options: {
            chart: {
              width: '100%',
              height:'100%',
            },
            legend: {
              position: 'top'
//              horizontalAlign: 'center',
            }
          }
        }],
        labels: labels,
        };

        this.categoryByproductValuation_chart = new ApexCharts(document.querySelector("#inventoryPieChartByCategoryProdValuation"), options);
        this.categoryByproductValuation_chart.render();
    }

//    outofstockByFSN(){
//        if(this.outofstockByFSN_chart){
//            this.outofstockByFSN_chart.destroy();
//        }
//        const fsn_count = this.fsn_count;
//        const labels = Object.keys(fsn_count);
//        const fsn = Object.values(fsn_count);
//        var options = {
//          series: fsn,
//          chart: {
//          type: 'polarArea',
//          width: '100%',
//          height:'100%',
////          events: {
////                dataPointSelection: (event, chartContext, config) => {
////                    this.actionService.doAction({
////                        ...this.line_action,
////                        context: { ...this.line_action.context, group_by: ["product_category_id"] },
////                    });
////                }
////            }
//        },
//        stroke: {
//          colors: ['#fff']
//        },
//        fill: {
//          opacity: 0.8
//        },
//        legend: {
//            position: 'top',
//            horizontalAlign: 'center'
//        },
//        responsive: [{
//          breakpoint: 480,
//          options: {
//            chart: {
//              width: '100%',
//              height:'100%',
//            },
//            legend: {
//              position: 'top'
////              horizontalAlign: 'center',
//            }
//          }
//        }],
//        labels: labels,
//        };
//
//        this.outofstockByFSN_chart = new ApexCharts(document.querySelector("#inventoryBarChartByFSNCount"), options);
//        this.outofstockByFSN_chart.render();
//    }

    generateColorPalette(numColors){
        const colors = [];
        const baseColors = [
            'rgba(16, 177, 142, 1)',   // Persian Green
            'rgba(17, 136, 248, 1)',   // Dodger Blue
            'rgba(254, 204, 2, 1)',    // Philippine Yellow
            'rgba(133, 133, 255, 1)',  // Violets Are Blue
            'rgba(3, 74, 131, 1)',     // Dark Cerulean
            'rgba(243, 114, 119, 1)',  // Begonia
            'rgba(71, 198, 207, 1)',   // Sea Serpent
            'rgba(76, 74, 75, 1)',     // Quartz
            'rgba(255, 102, 51, 1)',   // Smashed Pumpkin
            'rgba(250, 60, 72, 1)',    // Red Salsa
            'rgba(232, 189, 137, 1)',  // Gold (Crayola)
            'rgba(0, 123, 151, 1)',    // CG Blue
            'rgba(128, 0, 128, 1)',    // Dark Purple
            'rgba(255, 165, 0, 0.9)',  // Bright Orange
            'rgba(244, 67, 54, 1)',    // Deep Red
            'rgba(0, 128, 128, 1)',    // Dark Teal
            'rgba(128, 100, 200, 1)',  // Lavender
            'rgba(63, 81, 181, 1)',    // Indigo
            'rgba(0, 188, 212, 1)',    // Aqua
            'rgba(102, 187, 106, 1)',  // Green
            'rgba(255, 235, 59, 1)',   // Bright Yellow
            'rgba(142, 36, 170, 0.9)', // Purple
            'rgba(96, 125, 139, 1)',   // Blue Grey
            'rgba(0, 255, 127, 1)',    // Spring Green
            'rgba(3, 169, 244, 1)',    // Light Blue
            'rgba(238, 130, 238, 1)',  // Violet
            'rgba(70, 130, 180, 1)',   // Steel Blue
            'rgba(169, 169, 169, 1)',  // Dark Grey
            'rgba(121, 85, 72, 1)',    // Brown
            'rgba(0, 255, 255, 1)',    // Cyan
            'rgba(103, 58, 183, 1)',   // Deep Purple
        ];

        for (let i = 0; i < numColors; i++) {
            colors.push(baseColors[i % baseColors.length]);
        }

        return colors;
    };

    getBarThickness() {
    const viewportWidth = window.innerWidth;

    // Adjust the bar thickness based on the viewport size
    // You can tweak these values to fit your design
    if (viewportWidth <= 600) {
        return 7; // Smaller bar thickness for small screens
    } else if (viewportWidth <= 1200) {
        return 13; // Medium bar thickness for medium screens
    } else {
        return 25; // Larger bar thickness for large screens
    }
}

    abbreviateNumber(num) {
        const currency = this.company_currency_symbol;

        // Check if the number is less than 1000 (no abbreviation needed)
        if (num < 1000) return num;
        if (currency === '₹') {
            // Define the suffixes for the Indian numbering system (K for thousands, L for Lakh, Cr for Crore, etc.)
            const suffixes = ['K','L','Cr','Arb','Kh'];

            // If the number is between 1000 and less than 1 Lakh, we use K
            if (num < 100000) {
                return (num / 1000).toFixed(2) + ' ' + suffixes[0];
            }
            else if (num < 10000000) {
                return (num / 100000).toFixed(2) + ' ' + suffixes[1];
            }
            else if (num < 1000000000) {
                return (num / 10000000).toFixed(2) + ' ' + suffixes[2];
            }
            else if (num < 100000000000) {
                return (num / 1000000000).toFixed(2) + ' ' + suffixes[3];
            }
        }
        else if (currency === '$') {
            if (num > 1000000000 || num === 1000000000) {
                return (num / 1e9).toFixed(1) + 'B'; // For billions
            }
            if (num > 1000000 || num === 1000000) {
                return (num / 1e6).toFixed(1) + 'M'; // For millions
            }
            if (num > 1000 || num === 1000) {
                return (num / 1e3).toFixed(1) + 'K'; // For thousands
            }
            return num;
        }
    }
}

SetuOutOfStockDashboard.template = "SetuOutOfStockDashboard";
const checkStuff =  registry.category("actions").add("setu_outofstock_dashboard", SetuOutOfStockDashboard);