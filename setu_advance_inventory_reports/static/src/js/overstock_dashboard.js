/** @odoo-module **/
import { loadJS } from "@web/core/assets";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
//import { Component, onMounted, onWillStart, useState } from "@odoo/owl";

const { Component, onMounted, onWillStart, useState } = owl;

export class SetuOverstockDashboard extends Component {
    setup() {
        this.actionService = useService("action");
        this.orm = useService("orm");
        this.context = session.user_context;

        this.overstock_data = null;
        this.company_currency = null;
        this.initStartDate = null;
        this.initEndDate = null;
        this.stockDays = null;

        this.state = useState({
            overstock_qty_by_product: null,
        });

        this.line_action = null;
        let category_wiseProdsCount = null
        let inventoryChartWarehouseProd = null
        let inventorypolarcategory = null
        let inventoryPieChart = null


        onWillStart(async () => {
            await loadJS("https://cdn.jsdelivr.net/npm/apexcharts");
        });

        onMounted(() => {
            this.initializeDashboard();
        });
    }

    populateData(){
        const data = this.overstock_data;
        this.company_currency = data.company_currency_symbol;
        this.state.overstock_qty_by_product_category = data.overstock_qty_by_product_category;
        this.state.overall_stock_valuation = data.overall_stock_valuation;
        this.state.overstock_product_count = data.overstock_product_count;
        this.state.total_prod = data.total_prod;
        this.state.overstock_qty_by_warehouse = data.overstock_qty_by_warehouse;
        this.state.overstock_valuation = data.overstock_valuation;
        this.state.company_currency_symbol = data.company_currency_symbol;

        this.line_action = data.final_line_action || {};
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
                const today = new Date();
                const past90Days = new Date();
                past90Days.setDate(today.getDate() - 90);

                this.initStartDate = past90Days.toLocaleDateString('en-CA');
                this.initEndDate = today.toLocaleDateString('en-CA');
                this.stockDays = '30';
                const data = await this.orm.call("setu.overstock.dashboard", "return_overstock_analysis", [this.initStartDate, this.initEndDate, this.stockDays], { context: this.context });
                this.overstock_data = data;
                this.populateData();
                this.evaluateData();
            } catch (error) {
                console.error("Error loading out-of-stock data:", error);
            } finally {
                if (loader || document.querySelector(".loader_2")) {
                    document.querySelector(".loader_main").style.display = 'none';
                    document.querySelector(".loader_2").style.display = 'none';
                    document.querySelector(".loader_3").style.display = 'none';
                    document.querySelector(".loader_4").style.display = 'none';
                    document.querySelector(".loader_5").style.display = 'none';
                    document.querySelector(".loader_6").style.display = 'none';
                    document.querySelector(".loader_7").style.display = 'none';
                    document.querySelector(".loader_8").style.display = 'none';
                }
            }
        const defaultLi = document.getElementById('overstock_analysis');  // This will select the first li element
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

                this.overstock_data = await this.orm.call("setu.overstock.dashboard", "return_overstock_analysis", [new_start_Date, new_end_Date, new_stock_days], { context });
                this.populateData();
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

        var action = this.overstock_data.final_line_action || {};
        this.actions(action);
    }

    abbreviateNumber(num) {
        const currency = this.company_currency;

        // Check if the number is less than 1000 (no abbreviation needed)
        if (num < 1000) return num;

        var thresholds = 0
        if (currency === '₹') {
            thresholds = [
                { limit: 1e11, suffix: ' Kh' },
                { limit: 1e9, suffix: ' Arb' },
                { limit: 1e7, suffix: ' Cr' },
                { limit: 1e5, suffix: ' L' },
                { limit: 1e3, suffix: ' K' },
            ];
        }
        else if (currency === '$') {
            thresholds = [
                { limit: 1e12, suffix: ' T' },
                { limit: 1e9, suffix: ' B' },
                { limit: 1e6, suffix: ' M' },
                { limit: 1e3, suffix: ' K' },
            ];
        }

        if (thresholds) {

            for (const { limit, suffix } of thresholds) {
                if (num >= limit) {
                    return (num / limit).toFixed(2) + suffix;
                }
            }
        }

        return num.toLocaleString();
    }

    evaluateData(){
        this.overstock_by_warehouse();
        this.overstock_product_count_byWarehouse();
        this.category_wiseProductCount();
        this.category_wiseproductValuation();


        const overall_stock_valuation = this.state.overall_stock_valuation;
        document.querySelector('.overall_stock_valuation').textContent = this.abbreviateNumber(overall_stock_valuation || 0);

        const overstock_product_count_data = this.state.overstock_product_count;
        document.querySelector('.overstock_product_count_data').textContent = overstock_product_count_data;

        const total_prod = this.state.total_prod;
        document.querySelector('.total_prod').textContent = total_prod;

        const overstock_valuation = this.state.overstock_valuation;
        document.querySelector('.overstock_valuation').textContent = this.abbreviateNumber(overstock_valuation || 0);

        const company_currency_symbol = this.state.company_currency_symbol;
        document.querySelector('.company_currency_symbol1').textContent = company_currency_symbol;
        document.querySelector('.company_currency_symbol2').textContent = company_currency_symbol;

    }
    actions(action){
        document.querySelector('.stock_count_wh').addEventListener('click', () => {
             let data_action = action;
                if (data_action){
                    console.log(data_action);
                    data_action.context = {group_by: ["warehouse_id"]}
                    this.actionService.doAction(data_action);
                }
        });

        document.querySelector('.stock_val_wh').addEventListener('click', () => {
             let data_action = action;
                if (data_action){
                    console.log(data_action);
                    data_action.context = {group_by: ["warehouse_id"]}
                    this.actionService.doAction(data_action);
                }
        });
        document.querySelector('.stock_countCategory').addEventListener('click', () => {
             let data_action = action;
                if (data_action){
                    console.log(data_action);
                    data_action.context = {group_by: ["product_category_id"]}
                    this.actionService.doAction(data_action);
                }
        });
        document.querySelector('.stock_valueCategory').addEventListener('click', () => {
             let data_action = action;
                if (data_action){
                    console.log(data_action);
                    data_action.context = {group_by: ["product_category_id"]}
                    this.actionService.doAction(data_action);
                }
        });
    }
    category_wiseProductCount(){
        if (this.inventorypolarcategory) {
        this.inventorypolarcategory.destroy();
     }
        const overstockData = this.state.overstock_qty_by_product_category;

        const labels = Object.keys(overstockData);
        const bgColor = this.generateColorPalette(labels.length);
        const prod_count = Object.values(overstockData).map(list => list[0]);
        const data = {
          labels: labels,
          datasets: [
              {
                    label: 'Overstock product count',
                    data: prod_count,
                    backgroundColor: bgColor,
              }
          ]
        };
        var options = {
          series: prod_count,
          chart: {
          type: 'polarArea',
          width: '100%',
          height:'100%',
//          events: {
//                    click: (e) => {
//                        this.actionService.doAction({
//                            ...this.line_action,
//                            context: { ...this.line_action.context, group_by: ["product_category_id"]},
//                        });
//                    }
//                },
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
            }
          }
        }],
        labels: labels,
        };

        this.inventorypolarcategory = new ApexCharts(document.querySelector("#inventoryPolarChartByCategoryProdCount"), options);
        this.inventorypolarcategory.render();
    }

    category_wiseproductValuation(){

        if (this.inventoryPieChart) {
        this.inventoryPieChart.destroy();
     }
        const overstockData = this.state.overstock_qty_by_product_category;

        const labels = Object.keys(overstockData);
        const bgColor = this.generateColorPalette(labels.length);
        const prod_valuation = Object.values(overstockData).map(list => list[1]);
        var options = {
          series: prod_valuation,
          chart: {
          type: 'polarArea',
          width: '100%',
          height:'100%',
//          events: {
//                    click: (e) => {
//                        this.actionService.doAction({
//                            ...this.line_action,
//                            context: { ...this.line_action.context, group_by: ["product_category_id"]},
//                        });
//                    }
//                },
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
            }
          }
        }],
        labels: labels,
        };

        this.inventoryPieChart = new ApexCharts(document.querySelector("#inventoryPieChartByCategoryProdValuation"), options);
        this.inventoryPieChart.render();

    }

    overstock_by_warehouse(){
        if (this.category_wiseProdsCount) {
        this.category_wiseProdsCount.destroy();
     }

        const overstockData = this.state.overstock_qty_by_warehouse;
        const dataset_label = ['Overstock product count'];
        const bgColor = this.generateColorPalette(dataset_label.length);
        const labels = Object.keys(overstockData);
        const prod_count = Object.values(overstockData).map(list => list[0]);
        var options = {
          series: [{
          name: dataset_label,
          data: prod_count
        }],
          chart: {
          height: '100%',
          width:'100%',
//          events: {
//                    click: (e) => {
//                          this.actionService.doAction({
//                            ...this.line_action,
//                            context: { ...this.line_action.context, group_by: ["warehouse_id"]},
//                        });
//                    }
//                },
          type: 'bar',
          toolbar:{
            show:false,
          }
        },
        plotOptions: {
          bar: {
            columnWidth:'10%',
            borderRadius: 10,
            dataLabels: {
              position: 'top',
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
            enabled: true,
          },
          title: {
            text: 'Warehouse'
          }
        },
        yaxis: {
          title: {
            text: 'Count'
          }
        },
        };

        this.category_wiseProdsCount = new ApexCharts(document.querySelector("#inventoryBarChartByWarehouseProdCount"), options);
        this.category_wiseProdsCount.render();

        }

    overstock_product_count_byWarehouse(){
         if (this.inventoryChartWarehouseProd) {
        this.inventoryChartWarehouseProd.destroy();
     }
        const overstockData = this.state.overstock_qty_by_warehouse;
        const dataset_label = ['Overstock product valuation'];
        const bgColor = this.generateColorPalette(dataset_label.length);
        const labels = Object.keys(overstockData);
        const prod_valuation = Object.values(overstockData).map(list => list[1]);
        var options = {
          series: [{
          name: dataset_label,
          data: prod_valuation
        }],
        chart: {
          height: '100%',
          width:'100%',
          type: 'bar',
//          events: {
//                    click: (e) => {
//                          this.actionService.doAction({
//                            ...this.line_action,
//                            context: { ...this.line_action.context, group_by: ["warehouse_id"]},
//                        });
//                    }
//                },
          toolbar:{
            show:false,
          }
        },
        plotOptions: {
          bar: {
            borderRadius: 10,
            columnWidth: '15%',
          }
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          width: 0
        },
        grid: {
          row: {
            colors: ['#fff', '#f2f2f2']
          }
        },
        xaxis: {
          labels: {
            rotate: -45
          },
          categories: labels,
          tickPlacement: 'on',
          title: {
            text: 'Warehouse'
          }
        },
        yaxis: {
          title: {
            text: 'Value',
          },
        },
        fill: {
          type: 'gradient',
          gradient: {
            shade: 'light',
            type: "horizontal",
            shadeIntensity: 0.25,
            gradientToColors: undefined,
            inverseColors: true,
            opacityFrom: 0.85,
            opacityTo: 0.85,
            stops: [50, 0, 100]
          },
        }
        };

        this.inventoryChartWarehouseProd = new ApexCharts(document.querySelector("#inventoryBarChartByWarehouseProdValuation"), options);
        this.inventoryChartWarehouseProd.render();
    }

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

SetuOverstockDashboard.template = "SetuOverstockDashboard";
registry.category("actions").add("setu_overstock_dashboard", SetuOverstockDashboard);
