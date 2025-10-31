/** @odoo-module **/
import { loadJS } from "@web/core/assets";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

const { Component, onMounted, onWillStart, useState } = owl;

export class SetuAgeBreakdownInventoryDashboard extends Component {
    setup() {
        this.actionService = useService("action");
        this.orm = useService("orm");
        this.context = session.user_context;

        this.ageBreakdownData = null
        this.company_currency = null
        this.category_names = null
        this.age_line_action= null;
        this.age_breakdown_line_action= null;

        onWillStart(async () => {
            await loadJS("https://cdn.jsdelivr.net/npm/apexcharts");
        });

        onMounted(() => {
            this.initializeDashboard();
        });
    };

    formatValue(value) {
        if (typeof value !== 'number') return value;

        const thresholds = [
            { limit: 1e7, suffix: ' Cr' },
            { limit: 1e5, suffix: ' L' },
            { limit: 1e3, suffix: ' K' },
        ];

        for (const { limit, suffix } of thresholds) {
            if (value >= limit) {
                return (value / limit).toFixed(1) + suffix;
            }
        }
        return value.toLocaleString();
    };

    async initializeDashboard() {
        const loader = document.querySelector('.loader');
            if (loader) {
                loader.classList.remove('hidden');
            }

            try {
                this.ageBreakdownData = await this.orm.call("setu.age.breakdown.inventory.dashboard", "get_inventory_data");
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
                    document.querySelector(".loader_7").style.display = 'none';
                }
            }
        const defaultLi = document.getElementById('age_breakdown_analysis');
        if (defaultLi) {
            defaultLi.classList.add('active');
        }

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

        const ageBreakdownData = this.ageBreakdownData;

        this.company_currency = ageBreakdownData.company_currency_symbol;
        this.age_line_action = ageBreakdownData.final_age_action || {};
        this.age_breakdown_line_action = ageBreakdownData.final_breakdown_action || {};

        document.querySelector(".total_products").textContent = ageBreakdownData.total_product_count;
        document.querySelector(".total_current_stock").textContent = ageBreakdownData.total_current_stock;
        document.querySelector(".total_current_stock_value").textContent = `${this.company_currency} ${this.formatValue(ageBreakdownData.total_current_stock_value)}`;
        document.querySelector(".total_oldest_stock_qty").textContent = ageBreakdownData.total_oldest_stock_qty;
        document.querySelector(".total_oldest_stock_value").textContent = `${this.company_currency} ${this.formatValue(ageBreakdownData.total_oldest_stock_value)}`;

        const oldest_stock_qty_by_category = Object.values(ageBreakdownData.categories).map(c => c.total_stock_qty);
        const oldest_stock_value_by_category = Object.values(ageBreakdownData.categories).map(c => c.total_stock_value);
        const total_stock_breakdown =   ageBreakdownData.category_summary.map(cat => [
                                                                                        cat.total_breakdown1_qty,
                                                                                        cat.total_breakdown2_qty,
                                                                                        cat.total_breakdown3_qty,
                                                                                        cat.total_breakdown4_qty,
                                                                                        cat.total_breakdown5_qty,
                                                                                        cat.total_breakdown6_qty,
                                                                                        cat.total_breakdown7_qty,
                                                                                    ]);
        this.category_names = Object.values(ageBreakdownData.categories).map(c => c.category_name);
        const top_20_product_names = ageBreakdownData.top_20_products.map(product => product.product_name);
        const top_20_product_breakdowns = ageBreakdownData.top_20_products.map(product => product.total_breakdown_qty);
        this.productCategoryVsStockQty(oldest_stock_qty_by_category);
        this.stockValuebyProductCategory(oldest_stock_value_by_category);
        this.breakdownData(total_stock_breakdown);
        this.top_20products(top_20_product_names, top_20_product_breakdowns);

        var action_1 = ageBreakdownData.final_age_action || {};
        var action_2 = ageBreakdownData.final_breakdown_action || {};
        this.actions(action_1,action_2)
    };

    actions(action_1,action_2){
        document.querySelector('.category_skValue').addEventListener('click', () => {
             let data_action = action_1;
                if (data_action){
                    console.log(data_action);
                    data_action.context = {'group_by': ['product_category_id']}
                    this.actionService.doAction(data_action);
                }
        });
        document.querySelector('.category_skQty').addEventListener('click', () => {
             let data_action = action_1;
                if (data_action){
                    console.log(data_action);
                    data_action.context = {'group_by': ['product_category_id']}
                    this.actionService.doAction(data_action);
                }
        });
        document.querySelector('.skTop20').addEventListener('click', () => {
             let data_action = action_2;
                if (data_action){
                    console.log(data_action);
                    data_action.context = {'group_by': ['product_category_id']}
                    this.actionService.doAction(data_action);
                }
        });
        document.querySelector('.cgBreakdown').addEventListener('click', () => {
             let data_action = action_2;
                if (data_action){
                    console.log(data_action);
                    data_action.context = {'group_by': ['product_category_id']}
                    this.actionService.doAction(data_action);
                }
        });
    }

    productCategoryVsStockQty(oldest_stock_qty_by_category) {

        // Define chartData correctly
        const chartData = {
            labels: this.category_names,
            datasets: [{
                label: 'Products',
                data: oldest_stock_qty_by_category,
                backgroundColor: 'rgba(70, 130, 180, 1)',
                borderColor: 'rgba(70, 130, 180, 1)',
                borderWidth: 1,
            }],
        };

        // Reference chartData.datasets[0].data for series data
        var options = {
            series: [{
                name: 'Products',
                data: chartData.datasets[0].data
            }],
            chart: {
                height: '95%',
                width: '100%',
                type: 'bar',
                toolbar: {
                    show: false,
                },
//                 events: {
//                    dataPointSelection: (event, chartContext, config) => {
//                        this.age_line_action.context = { 'group_by': ['product_category_id'] };
//                        this.actionService.doAction(this.age_line_action);
//                    }
//                }
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
                categories: chartData.labels,
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
                    enabled: true,
                },
                title: {
                    text: 'Category'
                }
            },
            yaxis: {
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false,
                },
                labels: {
                    show: true,
                },
                title: {
                    text: 'Count'
                }
            },
        };

        var chart = new ApexCharts(document.querySelector("#oldestStockQtyBarChart"), options);
        chart.render();
    }

    stockValuebyProductCategory(oldest_stock_value_by_category) {
        const barBgColor = this.generateColorPalette(this.category_names.length);
        var options = {
            series: oldest_stock_value_by_category,
            chart: {
                type: 'polarArea',
                width: '100%',
                height: '90%',
//                events: {
//                    dataPointSelection: (event, chartContext, config) => {
//                        this.age_line_action.context = { 'group_by': ['product_category_id'] };
//                        this.actionService.doAction(this.age_line_action);
//                    }
//                }
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
            labels: this.category_names,
        };

        var chart = new ApexCharts(document.querySelector("#oldestStockValuePieChart"), options);
        chart.render();
    }

    breakdownData(total_stock_breakdown) {
    const datasets = this.category_names.map((categoryName, index) => ({
        name: categoryName,
        data: total_stock_breakdown[index],
        borderWidth: 1,
    }));

    var options = {
        series: datasets.map(dataset => ({
            name: dataset.name,
            data: dataset.data,

        })),
        chart: {
            type: 'bar',
            height: '100%',
            stacked: true,
            toolbar: {
                show: false
            },
//            events: {
//                dataPointSelection: (event, chartContext, config) => {
//                    this.age_breakdown_line_action.context = {'group_by': ['product_category_id']}
//                    this.actionService.doAction(this.age_breakdown_line_action);
//                }
//            },
            zoom: {
                enabled: true
            }
        },
        responsive: [{
            breakpoint: 480,
            options: {
                legend: {
                    position: 'bottom',
                    offsetX: -10,
                    offsetY: 0
                }
            }
        }],
        plotOptions: {
            bar: {
                horizontal: false,
                borderRadius: 10,
                borderRadiusApplication: 'end', // 'around', 'end'
                borderRadiusWhenStacked: 'last', // 'all', 'last'
                dataLabels: {
                        enabled: false,
                }
            },
        },
        xaxis: {
            type: 'category',  // Use 'category' as it's not a datetime series
            categories: ["1-30", "31-60", "61-90", "91-120", "121-150", "151-180", "181+"],
            title: {
                text: 'Days'
            }
        },
        yaxis: {
            title: {
                text: 'Count'
            }
        },
        legend: {
            position: 'top',
            offsetY: 20
        },
        fill: {
            opacity: 1
        }
    };

    var chart = new ApexCharts(document.querySelector("#breakdownDataByStackChart"), options);
    chart.render();
}

    top_20products(top_20_product_names, top_20_product_breakdowns) {
    // Ensure top_20_product_names and top_20_product_breakdowns are defined
    const chartData = {
        labels: top_20_product_names,  // List of product names
        datasets: [{
            label: "Products",
            data: top_20_product_breakdowns,  // List of product data
            backgroundColor: 'rgba(0, 128, 128, 1)',
            borderColor: 'rgba(0, 128, 128, 1)',
            borderWidth: 1,
        }],
    };

    var options = {
        series: [{
            name: 'Products',
            data: chartData.datasets[0].data
        }],
        chart: {
            height: '100%',
            width: '100%',
            type: 'bar',
            toolbar: {
                show: false,
            },
//            events: {
//                dataPointSelection: (event, chartContext, config) => {
//                    this.age_breakdown_line_action.context = {'group_by': ['product_category_id']}
//                    this.actionService.doAction(this.age_breakdown_line_action);
//                }
//            }
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
            categories: chartData.labels,  // Use chartData.labels for categories
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
                enabled: true,
            },
            title: {
                text: 'Products'
            }
        },
        yaxis: {
            axisBorder: {
                show: false
            },
            axisTicks: {
                show: false,
            },
            labels: {
                show: false,
                formatter: function (val) {
                    return val + "%";
                }
            },
            title: {
                text: 'Count'
            }
        },
    };

    var chart = new ApexCharts(document.querySelector("#top20ProductStackChart"), options);
    chart.render();
}

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

SetuAgeBreakdownInventoryDashboard.template = "SetuAgeBreakdownInventoryDashboard";
registry.category("actions").add("setu_age_breakdown_analysis_dashboard", SetuAgeBreakdownInventoryDashboard);