/** @odoo-module **/

import { loadJS } from "@web/core/assets";
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
import { session } from '@web/session';
import { Component, onMounted, useState, onWillStart} from "@odoo/owl";

export class SetuFSNXYZDashboard extends Component {
    setup() {
        this.actionService = useService("action");
        this.orm = useService('orm');
        const context = session.user_context;
        this.fsn_xyzAnalysisData = null
        this.fetch_action = null
        // Initialize the selected dates as null initially
        this.initStartDate = null;
        this.initEndDate = null;
        var chartX = null;
        var chartY = null;
        var chartZ = null;

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
                const today = new Date();
            const past90Days = new Date();
            past90Days.setDate(today.getDate() - 90);

            this.initStartDate = past90Days.toLocaleDateString('en-CA');
            this.initEndDate = today.toLocaleDateString('en-CA');

            this.fsn_xyzAnalysisData = await this.orm.call('setu.fsn.xyz.inventory.dashboard', 'get_fsn_xyz_analysis_data', [this.initStartDate, this.initEndDate], { context: this.context });
            this.evaluateData()
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
        const defaultLi = document.getElementById('fsn_xyz_analysis');  // This will select the first li element
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

                this.fsn_xyzAnalysisData = await this.orm.call('setu.fsn.xyz.inventory.dashboard', 'get_fsn_xyz_analysis_data', [new_start_Date, new_end_Date], { context });

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
        const fsn_xyzAnalysisData = this.fsn_xyzAnalysisData;
        this.fetch_action = fsn_xyzAnalysisData.final_action_click || 0
        var action_new = fsn_xyzAnalysisData.final_action_click || 0
        document.querySelector('.total_product_count').textContent = fsn_xyzAnalysisData.total_product_count || 0

        document.querySelector('.class_fx').textContent = (fsn_xyzAnalysisData.fsn_classification[0] + fsn_xyzAnalysisData.xyz_classification[0]) || ''
        document.querySelector('.class_fy').textContent = (fsn_xyzAnalysisData.fsn_classification[0] + fsn_xyzAnalysisData.xyz_classification[1]) || ''
        document.querySelector('.class_fz').textContent = (fsn_xyzAnalysisData.fsn_classification[0] + fsn_xyzAnalysisData.xyz_classification[2]) || ''
        document.querySelector('.class_sx').textContent = (fsn_xyzAnalysisData.fsn_classification[1] + fsn_xyzAnalysisData.xyz_classification[0]) || ''
        document.querySelector('.class_sy').textContent = (fsn_xyzAnalysisData.fsn_classification[1] + fsn_xyzAnalysisData.xyz_classification[1]) || ''
        document.querySelector('.class_sz').textContent = (fsn_xyzAnalysisData.fsn_classification[1] + fsn_xyzAnalysisData.xyz_classification[2]) || ''
        document.querySelector('.class_nx').textContent = (fsn_xyzAnalysisData.fsn_classification[2] + fsn_xyzAnalysisData.xyz_classification[0]) || ''
        document.querySelector('.class_ny').textContent = (fsn_xyzAnalysisData.fsn_classification[2] + fsn_xyzAnalysisData.xyz_classification[1]) || ''
        document.querySelector('.class_nz').textContent = (fsn_xyzAnalysisData.fsn_classification[2] + fsn_xyzAnalysisData.xyz_classification[2]) || ''

        const fx_count = fsn_xyzAnalysisData.fx_product_count || 0
        const fy_count = fsn_xyzAnalysisData.fy_product_count || 0
        const fz_count = fsn_xyzAnalysisData.fz_product_count || 0
        const sx_count = fsn_xyzAnalysisData.sx_product_count || 0
        const sy_count = fsn_xyzAnalysisData.sy_product_count || 0
        const sz_count = fsn_xyzAnalysisData.sz_product_count || 0
        const nx_count = fsn_xyzAnalysisData.nx_product_count || 0
        const ny_count = fsn_xyzAnalysisData.ny_product_count || 0
        const nz_count = fsn_xyzAnalysisData.nz_product_count || 0

        document.querySelector('.fx_product_count').textContent = fx_count
        document.querySelector('.fy_product_count').textContent = fy_count
        document.querySelector('.fz_product_count').textContent = fz_count
        document.querySelector('.sx_product_count').textContent = sx_count
        document.querySelector('.sy_product_count').textContent = sy_count
        document.querySelector('.sz_product_count').textContent = sz_count
        document.querySelector('.nx_product_count').textContent = nx_count
        document.querySelector('.ny_product_count').textContent = ny_count
        document.querySelector('.nz_product_count').textContent = nz_count

        const x_canvas = document.getElementById('classification_X_polarChart');
        const y_canvas = document.getElementById('classification_Y_polarChart');
        const z_canvas = document.getElementById('classification_Z_polarChart');

        const x_fsn_count = [fx_count, sx_count, nx_count]
        const y_fsn_count = [fy_count, sy_count, ny_count]
        const z_fsn_count = [fz_count, sz_count, nz_count]

        this.classificationXByMovement(x_canvas, x_fsn_count);
        this.classificationYByMovement(y_canvas, y_fsn_count);
        this.classificationZByMovement(z_canvas, z_fsn_count);
        this.actions(action_new)
    }
    actions(action_new){
        document.querySelector('.x_classification').addEventListener('click', () => {
             let data_action = action_new;
                if (data_action){
                    data_action.context = {'group_by': ['xyz_classification', 'fsn_classification']}
                    this.actionService.doAction(data_action);
                }
        });
        document.querySelector('.y').addEventListener('click', () => {
             let data_action = action_new;
                if (data_action){
                    data_action.context = {'group_by': ['xyz_classification', 'fsn_classification']}
                    this.actionService.doAction(data_action);
                }
        });
        document.querySelector('.z').addEventListener('click', () => {
             let data_action = action_new;
                if (data_action){
                    data_action.context = {'group_by': ['xyz_classification', 'fsn_classification']}
                    this.actionService.doAction(data_action);
                }
        });
    }
    classificationXByMovement(custom_canvas, data){
        const dataset_label = ['F', 'S', 'N'];
        const bgColor = this.generateColorPalette(dataset_label.length);

        var options = {
            series: data,
            chart: {
                width: '100%',
                height: '100%',
                type: 'pie',
//                events: {
//                    click: (e) => {
//                        if (this.fetch_action){
//                            this.fetch_action.context = {'group_by': ['xyz_classification', 'fsn_classification']}
//                            this.actionService.doAction(this.fetch_action);
//                        }
//                    },
//                },
            },
            labels: dataset_label,
            legend: {
                show: true,
                position: 'top',
            },
            dataLabels: {
                enabled: false,
            },
        };

        if (custom_canvas.chart) {
            custom_canvas.chart.destroy();
        }

        if(this.chartX){
            this.chartX.destroy();
        }

        this.chartX = new ApexCharts(custom_canvas, options);
        this.chartX.render();
    };

    classificationYByMovement(custom_canvas, data){
        const dataset_label = ['F', 'S', 'N'];
        const bgColor = this.generateColorPalette(dataset_label.length);

        var options = {
            series: data,
            chart: {
                width: '100%',
                height: '100%',
                type: 'pie',
//                events: {
//                    click: (e) => {
//                        if (this.fetch_action){
//                            this.fetch_action.context = {'group_by': ['xyz_classification', 'fsn_classification']}
//                            this.actionService.doAction(this.fetch_action);
//                        }
//                    },
//                },
            },
            labels: dataset_label,
            legend: {
                show: true,
                position: 'top',
            },
            dataLabels: {
                enabled: false,
            },
        };

        if (custom_canvas.chart) {
            custom_canvas.chart.destroy();
        }

        if(this.chartY){
            this.chartY.destroy();
        }

        this.chartY = new ApexCharts(custom_canvas, options);
        this.chartY.render();
    };

    classificationZByMovement(custom_canvas, data){
        const dataset_label = ['F', 'S', 'N'];
        const bgColor = this.generateColorPalette(dataset_label.length);

        var options = {
            series: data,
            chart: {
                width: '100%',
                height: '100%',
                type: 'pie',
//                events: {
//                    click: (e) => {
//                        if (this.fetch_action){
//                            this.fetch_action.context = {'group_by': ['xyz_classification', 'fsn_classification']}
//                            this.actionService.doAction(this.fetch_action);
//                        }
//                    },
//                },
            },
            labels: dataset_label,
            legend: {
                show: true,
                position: 'top',
            },
            dataLabels: {
                enabled: false,
            },
        };

        if (custom_canvas.chart) {
            custom_canvas.chart.destroy();
        }

        if(this.chartZ){
            this.chartZ.destroy();
        }

        this.chartZ = new ApexCharts(custom_canvas, options);
        this.chartZ.render();
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

SetuFSNXYZDashboard.template = 'SetuFSNXYZDashboard';
registry.category('actions').add('setu_fsn_xyz_dashboard', SetuFSNXYZDashboard);
