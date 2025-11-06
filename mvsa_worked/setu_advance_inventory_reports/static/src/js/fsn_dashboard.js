/** @odoo-module **/
import { loadJS } from "@web/core/assets";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

const { Component, onMounted, onWillStart, useState } = owl;
import { renderToFragment,renderToElement } from "@web/core/utils/render";

export class SetuFSNDashboard extends Component {
    setup() {
        this.actionService = useService("action");
        this.orm = useService("orm");
        this.context = session.user_context;

        this.fsn_stockData = null;
        this.initStartDate = null;
        this.initEndDate = null;
        var warehouseWiseFSNCountChart = null;
        var categoryWiseFSNChart = null;
        var warehouseWiseFSNChart = null;

        // Initialize state to hold category-wise, company-wise, warehouse-wise, and product-wise data
        this.state = useState({
            categories: [],
            fast_moving_count_by_category: [],
            slow_moving_count_by_category: [],
            non_moving_count_by_category: [],
            companies: [],
            fast_moving_count_by_company: [],
            slow_moving_count_by_company: [],
            non_moving_count_by_company: [],
            warehouses: [],
            fast_moving_count_by_warehouse: [],
            slow_moving_count_by_warehouse: [],
            non_moving_count_by_warehouse: [],
            products: [],
            fast_moving_count_by_product: [],
            slow_moving_count_by_product: [],
            non_moving_count_by_product: [],
            total_product_count: 0,
        });

        // Fetch the data when the component is mounted
        onWillStart(async () => {
            await loadJS("https://cdn.jsdelivr.net/npm/apexcharts@latest");
        });

        onMounted(() => {
            this.initializeDashboard();
        });
    }

    populateChartData(fsn_stockData) {
        // Category-wise data
        this.state.categories = Object.keys(fsn_stockData.categories);
        this.state.fast_moving_count_by_category = this.state.categories.map(category => fsn_stockData.categories[category].fast_moving_count || 0);
        this.state.slow_moving_count_by_category = this.state.categories.map(category => fsn_stockData.categories[category].slow_moving_count || 0);
        this.state.non_moving_count_by_category = this.state.categories.map(category => fsn_stockData.categories[category].non_moving_count || 0);

        // Company-wise data
        this.state.companies = Object.keys(fsn_stockData.companies);
        this.state.fast_moving_count_by_company = this.state.companies.map(company => fsn_stockData.companies[company].fast_moving_count || 0);
        this.state.slow_moving_count_by_company = this.state.companies.map(company => fsn_stockData.companies[company].slow_moving_count || 0);
        this.state.non_moving_count_by_company = this.state.companies.map(company => fsn_stockData.companies[company].non_moving_count || 0);

        // Warehouse-wise data
        this.state.warehouses = Object.keys(fsn_stockData.warehouses);
        this.state.fast_moving_count_by_warehouse = this.state.warehouses.map(warehouse => fsn_stockData.warehouses[warehouse].fast_moving_count || 0);
        this.state.slow_moving_count_by_warehouse = this.state.warehouses.map(warehouse => fsn_stockData.warehouses[warehouse].slow_moving_count || 0);
        this.state.non_moving_count_by_warehouse = this.state.warehouses.map(warehouse => fsn_stockData.warehouses[warehouse].non_moving_count || 0);
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
                loader.classList.remove('hidden');
            }

            try {
                const today = new Date();
                const past90Days = new Date();
                past90Days.setDate(today.getDate() - 90);

                this.initStartDate = past90Days.toLocaleDateString('en-CA');
                this.initEndDate = today.toLocaleDateString('en-CA');
                const fsn_stockData = await this.orm.call("setu.fsn.dashboard", "get_fsn_analysis_data", [this.initStartDate, this.initEndDate], { context: this.context });
                this.fsn_stockData = fsn_stockData;
                console.log(fsn_stockData);

                const totalProductCount = fsn_stockData.total_product_count || 0;

                // Update state with total product count
                this.state.totalProductCount = totalProductCount;

                this.populateChartData(fsn_stockData);
                this.evaluateData();
            } catch (error) {
                console.error("Error loading out-of-stock data:", error);
            } finally {
                if (loader) {
//                    loader.style.display = 'none';
                    document.querySelector(".loader_1").style.display = 'none';
                    document.querySelector(".loader_2").style.display = 'none';
                    document.querySelector(".loader_3").style.display = 'none';
                    document.querySelector(".loader_4").style.display = 'none';
                    document.querySelector(".loader_5").style.display = 'none';
                    document.querySelector(".loader_6").style.display = 'none';
                    document.querySelector(".loader_7").style.display = 'none';
                }
            }
        const defaultLi = document.getElementById('fsn_analysis');  // This will select the first li element
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

                this.fsn_stockData = await this.orm.call("setu.fsn.dashboard", "get_fsn_analysis_data", [new_start_Date, new_end_Date], { context });

                this.warehouseWiseFSNCountChart.destroy();
                this.categoryWiseFSNChart.destroy();
                this.warehouseWiseFSNChart.destroy();
                this.populateChartData(this.fsn_stockData);
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
    }

    evaluateData(){
        const fsn_stockData = this.fsn_stockData;
        let line_action = fsn_stockData.final_line_action || {};
        document.querySelector('.total_products').textContent = fsn_stockData.total_product_count;
        document.querySelector('.fast_moving_company').textContent = fsn_stockData.fast_moving_count;
        document.querySelector('.fast_moving_percentage').textContent = fsn_stockData.fast_moving_percentage;
        document.querySelector('.slow_moving_company').textContent = fsn_stockData.slow_moving_count;
        document.querySelector('.slow_moving_percentage').textContent = fsn_stockData.slow_moving_percentage;
        document.querySelector('.non_moving_company').textContent = fsn_stockData.non_moving_count;
        document.querySelector('.non_moving_percentage').textContent = fsn_stockData.non_moving_percentage;

        this.warehouseWiseFSN(line_action);
        this.warehouseWiseFSNCount(line_action);
        this.categoryWiseFSN(line_action);
        this.actions(line_action);
    }
    actions(line_action){

       document.querySelector('.warehouse_wiseFSN').addEventListener('click', () => {
            let data_action = line_action;
            if (data_action) {
                console.log(data_action);
                data_action.context = {'group_by': ['warehouse_id', 'stock_movement']};
                this.actionService.doAction(data_action);
            }
        });
        document.querySelector('.warehouse_FSNCount').addEventListener('click', () => {
            let data_action = line_action;
                if (data_action){
                    console.log(data_action);
                    data_action.context = {'group_by': ['warehouse_id', 'stock_movement']}
                    this.actionService.doAction(data_action);
                }
        });
        document.querySelector('.category_FSNCount').addEventListener('click', () => {
             let data_action = line_action;
                if (data_action){
                    console.log(data_action);
                    data_action.context = {'group_by': ['product_category_id', 'stock_movement']}
                    this.actionService.doAction(data_action);
                }
        });
    }
    warehouseWiseFSNCount(line_action){
        const dataset_label = ['Fast Moving', 'Slow Moving', 'Non Moving']
        const bgColor = this.generateColorPalette(dataset_label.length);

        let data_action = line_action;

        var options = {
            series: [
                {
                    name: dataset_label[0],
                    data: this.state.fast_moving_count_by_warehouse,
                },
                {
                    name: dataset_label[1],
                    data: this.state.slow_moving_count_by_warehouse,
                },
                {
                    name: dataset_label[2],
                    data: this.state.non_moving_count_by_warehouse,
                }
            ],
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
//                            data_action.context = {'group_by': ['warehouse_id', 'stock_movement']}
//                            this.actionService.doAction(data_action);
//                        }
//                    },
//                },
            },
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: '20%',
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
                    text: 'Warehouse'
                },
                categories: this.state.warehouses,
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

        this.warehouseWiseFSNCountChart = new ApexCharts(document.querySelector("#warehouseWiseFSNCount"), options);
        this.warehouseWiseFSNCountChart.render();
    };

    categoryWiseFSN(line_action){
        const dataset_label = ['Fast Moving', 'Slow Moving', 'Non Moving']
        const bgColor = this.generateColorPalette(dataset_label.length);

        let data_action = line_action;

        var options = {
            series: [
                {
                    name: dataset_label[0],
                    data: this.state.fast_moving_count_by_category,
                },
                {
                    name: dataset_label[1],
                    data: this.state.slow_moving_count_by_category,
                },
                {
                    name: dataset_label[2],
                    data: this.state.non_moving_count_by_category,
                }
            ],
            chart: {
                type: 'bar',
                width: '100%',
                height: '100%',
                toolbar: {
                    show: false,
                },
//                events: {
//                    click: (e) => {
//
//                        let data_action = line_action;
//                        if (data_action){
//                            console.log(data_action);
//                            data_action.context = {'group_by': ['product_category_id', 'stock_movement']}
//                            this.actionService.doAction(data_action);
//                        }
//                    },
//                },
            },
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: '30%',
                    borderRadius: 2,
                    borderRadiusApplication: 'end',
                    dataLabels: {
                        position: 'top', // top, center, bottom
                    },
                },
            },
            dataLabels: {
                enabled: true,
                offsetY: -5,
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
                    text: 'Category'
                },
                categories: this.state.categories,
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

        this.categoryWiseFSNChart = new ApexCharts(document.querySelector("#categoryWiseFSN"), options);
        this.categoryWiseFSNChart.render();
    };

    warehouseWiseFSN(line_action){
        const totalByWarehouse = [];
        const data = [];
        const labels = this.state.warehouses;
        const bgColor = this.generateColorPalette(labels.length);

        for (let i = 0; i < this.state.warehouses.length; i++) {
            const fastMovingData = this.state.fast_moving_count_by_warehouse;
            const slowMovingData = this.state.slow_moving_count_by_warehouse;
            const nonMovingData = this.state.non_moving_count_by_warehouse;

            const totalCount = fastMovingData[i] + slowMovingData[i] + nonMovingData[i];

            data.push(totalCount);

            totalByWarehouse.push({
                warehouse: this.state.warehouses[i],
                fastMoving: fastMovingData[i],
                slowMoving: slowMovingData[i],
                nonMoving: nonMovingData[i],
                total: totalCount,
            });
        };

        var options = {
            series: data,
            chart: {
                width: '100%',
                height: '100%',
                type: 'pie',
//                events: {
//                    click: (e) => {
//                        let data_action = line_action;
//                        if (data_action){
//                            console.log(data_action);
//                            data_action.context = {'group_by': ['warehouse_id', 'stock_movement']}
//                            this.actionService.doAction(data_action);
//                        }
//                    },
//                },
            },
            labels: this.state.warehouses,
            legend: {
                show: true,
                position: 'top',
            },
            dataLabels: {
                enabled: false,
            },
            tooltip: {
                enabled: true,
                shared: false,
                custom: function({ seriesIndex, dataPointIndex, w }) {
                    var seriesData = w.config.series[seriesIndex];
                    var label = w.config.labels[dataPointIndex];
                    const warehouseData = totalByWarehouse[seriesIndex];
                    const fastMovingPercentage = ((warehouseData.fastMoving / warehouseData.total) * 100).toFixed(2);
                    const slowMovingPercentage = ((warehouseData.slowMoving / warehouseData.total) * 100).toFixed(2);
                    const nonMovingPercentage = ((warehouseData.nonMoving / warehouseData.total) * 100).toFixed(2);
                    return '<div style="padding: 10px; background-color: ${bgColor[seriesIndex]}; border-radius: 5px; color: white;">' +
                           '<strong>' + warehouseData.warehouse + '</strong></br>' +
                           'Fast: ' + fastMovingPercentage +'%</br>' +
                           'Slow: ' + slowMovingPercentage +'%</br>' +
                           'Non: ' + nonMovingPercentage +'%</br>' +
                           '</div>';
                },
            },
        };

        this.warehouseWiseFSNChart = new ApexCharts(document.querySelector("#warehouseWiseFSN"), options);
        this.warehouseWiseFSNChart.render();
    };

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
}

SetuFSNDashboard.template = "SetuFSNDashboard";
registry.category("actions").add("setu_fsn_dashboard", SetuFSNDashboard);