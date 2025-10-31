/** @odoo-module **/

import { loadJS } from "@web/core/assets";
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
import { session } from '@web/session';
import { Component, onMounted, useState, onWillStart} from "@odoo/owl";

export class SetuXYZDashboard extends Component {
    setup() {
        this.actionService = useService("action");
        this.orm = useService('orm');
        const context = session.user_context;
        this.xyzAnalysisData = null
        this.company_currency = null
        this.chart_action = null

        let company_wise_xyz_chart = null
        let xyz_byProductCategory_chart = null


        onWillStart(async () => {
            await loadJS("https://cdn.jsdelivr.net/npm/apexcharts");
        });

        onMounted(() => {
            this.initializeDashboard();
        });
    }

    async initializeDashboard(){
        const loader = document.querySelector('.loader');
            if (loader) {
                loader.classList.remove('hidden');
                console.log('Loader should be visible now.');
            }

            try {
                this.xyzAnalysisData = await this.orm.call('setu.xyz.inventory.dashboard', 'get_xyz_analysis_data');
                this.evaluate_data()
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
        const defaultLi = document.getElementById('xyz_analysis');
        if (defaultLi) {
            defaultLi.classList.add('active');
        }

        document.querySelectorAll('.context-button').forEach(button => {
            button.addEventListener('click', async (event) => {
                const selectedOption = event.target.getAttribute('data-option');
                console.log(selectedOption);

                const actions = {
                    "fsn_dashboard": ["setu_fsn_dashboard", "FSN Dashboard"],
                    "xyz_dashboard": ["setu_xyz_dashboard", "XYZ Dashboard"],
                    "fsn_xyz_dashboard": ["setu_fsn_xyz_dashboard", "FSN-XYZ Dashboard"],
                    "overstock_dashboard": ["setu_overstock_dashboard", "OverStock Dashboard"],
                    "outofstock_dashboard": ["setu_outofstock_dashboard", "OutOfStock Dashboard"],
                    "movement_dashboard": ["setu_stock_movement_dashboard", "Movement Dashboard"],
                    "age_breakdown_dashboard": ["setu_age_breakdown_analysis_dashboard", "Age Breakdown Dashboard"],
                };

                if (actions[selectedOption]) {
                    const actionRequest = {
                        type: "ir.actions.client",
                        tag: actions[selectedOption][0],
                        name: actions[selectedOption][1],
                    };
                    const options = { stackPosition: "replaceCurrentAction" };

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
    evaluate_data(){
        const xyzAnalysisData = this.xyzAnalysisData
        this.chart_action = xyzAnalysisData.line_action || {}
        var line_action_new = xyzAnalysisData.line_action || {}
        this.company_currency = xyzAnalysisData.currency_name || ''
        document.querySelector('.currency_name').textContent = xyzAnalysisData.currency_name || ''
        document.querySelector('.total_stock_value').textContent = xyzAnalysisData.total_stock_value || 0
        document.querySelector('.total_stock_value').textContent = this.abbreviateNumber(xyzAnalysisData.total_stock_value || 0)
        document.querySelector('.total_product_count').textContent = xyzAnalysisData.total_product_count || 0

        document.querySelector('.class_x').textContent = xyzAnalysisData.classification[0] || 0
        document.querySelector('.x_currency_name').textContent = xyzAnalysisData.currency_name || ''
        document.querySelector('.x_product_count').textContent = xyzAnalysisData.x_product_count || 0

        document.querySelector('.x_stock_value').textContent = this.abbreviateNumber(xyzAnalysisData.x_stock_value || 0)

        document.querySelector('.class_y').textContent = xyzAnalysisData.classification[1] || 0
        document.querySelector('.y_currency_name').textContent = xyzAnalysisData.currency_name || ''
        document.querySelector('.y_product_count').textContent = xyzAnalysisData.y_product_count || 0

        document.querySelector('.y_stock_value').textContent = this.abbreviateNumber(xyzAnalysisData.y_stock_value || 0)

        document.querySelector('.class_z').textContent = xyzAnalysisData.classification[2] || 0
        document.querySelector('.z_currency_name').textContent = xyzAnalysisData.currency_name || ''
        document.querySelector('.z_product_count').textContent = xyzAnalysisData.z_product_count || 0
        document.querySelector('.z_stock_value').textContent = this.abbreviateNumber(xyzAnalysisData.z_stock_value || 0)

        const category_name = xyzAnalysisData.category_name || []
        const company_name = xyzAnalysisData.company_name || []
        const classification = xyzAnalysisData.classification || []
        const current_stock = xyzAnalysisData.current_stock || []
        const stock_value = xyzAnalysisData.stock_value || []
        const product_count_by_category = xyzAnalysisData.product_count_by_category || []

        const stock_category_data = xyzAnalysisData.stock_category_data || []
        const stock_company_data = xyzAnalysisData.stock_company_data || []

        this.company_wise_xyz(company_name, classification, stock_company_data);
        this.xyz_byProductCategory(category_name, classification, stock_category_data, product_count_by_category)
        this.actions(line_action_new)
    }

    actions(line_action_new){
        document.querySelector('.stock_value_category').addEventListener('click', () => {
             let data_action = line_action_new;
                data_action.context = {'group_by': ['product_category_id', 'analysis_category']}
                this.actionService.doAction(line_action_new);

        });
        document.querySelector('.stock_value_company').addEventListener('click', () => {
             let data_action = line_action_new;
                data_action.context = {'group_by': ['company_id', 'analysis_category']};
                this.actionService.doAction(line_action_new);

        });
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
                    return (num / limit).toFixed(1) + suffix;
                }
            }
        }

        return num.toLocaleString();
    }


    company_wise_xyz(company, classification, stock_company_data) {
        const stock_data = {'x_stock_values': [], 'y_stock_values': [], 'z_stock_values': []};

        const bgColor = this.generateColorPalette(classification.length);

        Object.keys(stock_company_data).forEach(company => {
            const companyData = stock_company_data[company];
            stock_data['x_stock_values'].push(companyData.X ? companyData.X.stock_value : 0);
            stock_data['y_stock_values'].push(companyData.Y ? companyData.Y.stock_value : 0);
            stock_data['z_stock_values'].push(companyData.Z ? companyData.Z.stock_value : 0);
        });

        var options = {
            series: [
                {
                    name: classification[0],
                    data: stock_data['x_stock_values'],
                },
                {
                    name: classification[1],
                    data: stock_data['y_stock_values'],
                },
                {
                    name: classification[2],
                    data: stock_data['z_stock_values'],
                }
            ],
            chart: {
                height: '100%',
                width: '100%',
                type: 'line',
//                events: {
//                    click: (event, chartContext, config) => {
//                        this.chart_action.context = {'group_by': ['company_id', 'analysis_category']};
//                        this.actionService.doAction(this.chart_action);
//                    }
//                },
                dropShadow: {
                    enabled: true,
                    color: '#000',
                    top: 18,
                    left: 7,
                    blur: 10,
                    opacity: 0.5
                },
                zoom: {
                    enabled: false
                },
                toolbar: {
                    show: false
                }
            },
            colors: ['#77B6EA', '#FF5733', '#33FF57'],
            dataLabels: {
                enabled: true,
            },
            stroke: {
                curve: 'smooth'
            },
            grid: {
                borderColor: '#e7e7e7',
                row: {
                    colors: ['#f3f3f3', 'transparent'],
                    opacity: 0.5
                },
            },
            markers: {
                size: 1
            },
            xaxis: {
                categories: Object.keys(stock_company_data),
                title: {
                    text: 'Company'
                }
            },
            yaxis: {
                title: {
                    text: 'Count'
                },
            },
            legend: {
                position: 'top',
                horizontalAlign: 'right',
                floating: true,
                offsetY: -5,
                offsetX: -5
            }
        };

        this.company_wise_xyz_chart = new ApexCharts(document.querySelector("#companyLineChart"), options);
        this.company_wise_xyz_chart.render();
    }

    xyz_byProductCategory(category, classification, stock_category_data, product_count_of_category){
        const stock_data = {'x_stock_values': [], 'y_stock_values': [], 'z_stock_values': []}
        const category_product_count = product_count_of_category

        const bgColor = this.generateColorPalette(classification.length);

        Object.keys(stock_category_data).forEach(category => {
            const categoryData = stock_category_data[category];
            if (categoryData.X) {
                stock_data['x_stock_values'].push(categoryData.X.stock_value);
            }
            else {
                stock_data['x_stock_values'].push(0);
            }
            if (categoryData.Y) {
                 stock_data['y_stock_values'].push(categoryData.Y.stock_value);
            }
            else {
                 stock_data['y_stock_values'].push(0);
            }
            if (categoryData.Z) {
                 stock_data['z_stock_values'].push(categoryData.Z.stock_value);
            }
            else {
                 stock_data['z_stock_values'].push(0);
            }
        });

        var options = {
          series: [{
          name: classification[0],
          data: stock_data['x_stock_values'],
        }, {
          name: classification[1],
          data: stock_data['y_stock_values'],
        }, {
          name: classification[2],
          data: stock_data['z_stock_values'],
        }],
          chart: {
          type: 'bar',
          height: '100%',
          width:'100%',
          toolbar:{
              show:false,
          },
//          events: {
//                click: (e) => {
//                    this.chart_action.context = {'group_by': ['product_category_id', 'analysis_category']}
//                    this.actionService.doAction(this.chart_action);
//                }
//            },
        },
        plotOptions: {
            bar: {
                horizontal: false,
                columnWidth: '30%',
                borderRadius: 5,
                borderRadiusApplication: 'end',
                dataLabels: {
                    position: 'top',
                },
            },
        },
        dataLabels: {
    enabled: true,
    offsetY: -20,
    formatter: function (val) {
        if (val == 0) { val = ''; }
        return val;
    },
    style: {
        colors: ["#000000"],
        fontSize: '0.5vw',
    },
    rotate: 60, // This will rotate the labels by -45 degrees
},

        stroke: {
          show: true,
          width: 2,
          colors: ['transparent']
        },
        xaxis: {
          categories: category,
        },
        yaxis: {
          title: {
            text: 'Count'
          }
        },
        fill: {
          opacity: 1
        },
        tooltip: {
          y: {
          },

        },
        legend: {
            position: 'top',
            horizontalAlign: 'right',
            floating: true,
            offsetY: -5,
            offsetX: -5
        }
        };

        this.xyz_byProductCategory_chart = new ApexCharts(document.querySelector("#productCategoryBarChart"), options);
        this.xyz_byProductCategory_chart.render();
    }

    getBarThickness() {
    const viewportWidth = window.innerWidth;

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
SetuXYZDashboard.template = 'SetuXYZDashboard';
registry.category('actions').add('setu_xyz_dashboard', SetuXYZDashboard);
