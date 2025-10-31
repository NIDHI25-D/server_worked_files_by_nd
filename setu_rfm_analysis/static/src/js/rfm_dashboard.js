/** @odoo-module **/
import { loadJS } from "@web/core/assets";
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
import { ControlPanel } from "@web/search/control_panel/control_panel";
const { format } = require('web.field_utils');
var session = require('web.session');
import { getLangDateFormat } from 'web.time';
const { Component,onMounted, onWillStart, useState, useEffect,useRef } = owl;
var core = require('web.core');
var COLORS = ["#1f77b4", "#aec7e8"];
var QWeb = core.qweb;
var FORMAT_OPTIONS = {
    // allow to decide if utils.human_number should be used
    humanReadable: function (value) {
        return Math.abs(value) >= 1000;
    },
    // with the choices below, 1236 is represented by 1.24k
    minDigits: 1,
    decimals: 2,
    // avoid comma separators for thousands in numbers when human_number is used
    formatterCallback: function (str) {
        return str;
    },
};
export class RfmDashboardAction extends Component{
    setup() {
        super.setup();
         this.controlPanelDisplay = {
            "top-left": true,
            "top-right": true,
            "bottom-left": false,
            "bottom-right": false,
        };
        this.rpc = useService("rpc");
        this.DATE_FORMAT = getLangDateFormat();
        this.date_range = 'week';  // possible values : 'week', 'month', year'
        this.date_from = moment.utc();//.subtract(1, 'week')
        this.date_to = moment.utc();

        this.graphs = [];
        this.chartIds = {};
        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            var self = this;
            return self.fetch_data();
        })
         onMounted(()=> {
//                this._computeControlPanelProps();
              this.render_graphs(this.chart_values);
            });

      }
      async fetch_data() {
        var self = this;
        debugger
        const result = await this.rpc(  '/setu_rfm_analysis/fetch_dashboard_data', {
                date_from: this.date_from.year()+'-'+(this.date_from.month()+1)+'-'+this.date_from.date(),
                date_to: this.date_to.year()+'-'+(this.date_to.month()+1)+'-'+this.date_to.date(),
                company_id: session.user_context.allowed_company_ids
        });
        self.chart_values = result
        return result;
    }
    formatValue(value) {
        var formatter = format.float;
        var formatedValue = formatter(value, undefined, FORMAT_OPTIONS);
        return formatedValue;
    }
    render_graphs(chart_values) {
        var self = this;
        $.each(self.chart_values, function(index, chartvalue){
            var $canvasContainer = $('<div/>', {class: 'o_graph_canvas_container'});
            self.$canvas = $('<canvas/>');
            $canvasContainer.append(self.$canvas);
            $('#'+chartvalue.chart_name).append($canvasContainer);
            var ctx = self.$canvas[0];
            ctx.height = 106

            if (chartvalue.chart_name == 'customer_rating'){
                var labels = chartvalue.integration_labels
            }
            else{
                var labels = chartvalue.chart_values[0].values.map(function (value) {
                return value.name
            });
            }
            /*if(chartvalue.chart_name == 'customer_rating'){
            	var labels_1 = chartvalue.chart_values.map(function (group, index) {
            	return group.values.map(function (value) {
                        return value.name;
                    })
            	});
                var labels_1 = [].concat.apply([], labels_1);
                var labels = _.union(labels,labels_1);
		}*/

            if (chartvalue.chart_name == 'customer_rating'){
                 var datasets = chartvalue.chart_values
            }
            else {
                var datasets = chartvalue.chart_values.map(function (group, index) {
                    return {
                        label: group.key,
                        data: group.values.map(function (value) {
                            return value.count;
                        }),
                        labels: group.values.map(function (value) {
                            return value.name;
                        }),
                        backgroundColor: chartvalue.chart_type == 'bar'? self.getRandomRgb() : group.values.map(function (value) {
                            return self.getRandomRgb()
                        }),
                        borderWidth: 1
                    };
                });
            }

            const data = {
              labels: labels,
              datasets: datasets
            };
            const options = {
                    title: {
                        display: true,
                        text: chartvalue.chart_title,
                        position: 'bottom',
                    }
                }
            if(chartvalue.chart_type == 'bar'){
                options.scales = {
                            yAxes: [{
                                ticks: {
                                    beginAtZero: true
                                }
                            }]
                        }
            }
            self.chart = new Chart(ctx, {
                type: chartvalue.chart_type,
                data: data,
                 options: options
            });
        });
    }
    getRandomRgb() {
      var num = Math.round(0xffffff * Math.random());
      var r = num >> 16;
      var g = num >> 8 & 255;
      var b = num & 255;
      return 'rgb(' + r + ', ' + g + ', ' + b + ', 0.7)';
    }
     _computeControlPanelProps() {

        const $searchview = $(QWeb.render("setu_rfm_analysis.DateRangeButtons", {
            content: this,
        }));
        $searchview.find('button.js_date_range').click((ev) => {
            $searchview.find('button.js_date_range.active').removeClass('active');
            $(ev.target).addClass('active');
            this.on_date_range_button($(ev.target).data('date'));
        });
        $('#setu_rfm_analysis_panel').html($searchview)
    }
    on_date_range_button(date_range) {
        if (date_range === 'week') {
            this.date_range = 'week';
            this.date_from = moment.utc().subtract(1, 'weeks');
        } else if (date_range === 'month') {
            this.date_range = 'month';
            this.date_from = moment.utc().subtract(1, 'months');
        } else if (date_range === 'year') {
            this.date_range = 'year';
            this.date_from = moment.utc().subtract(1, 'years');
        } else {
            console.log('Unknown date range. Choose between [week, month, year]');
            return;
        }

        var self = this;
        Promise.resolve(this.fetch_data()).then(function () {
            $('.o_rfm_dashboard').empty();
            self.render_dashboards();
            self.render_graphs();
        });

    }
     render_dashboards() {
        var self = this;
        $('.o_rfm_dashboard').append(QWeb.render('setu_rfm_analysis.dashboard_content_qweb', {content: self}));
    }
}
ControlPanel.defaultProps = {
        withBreadcrumbs: true,
        withSearchBar: true,
    };
RfmDashboardAction.components = {
    ControlPanel,
};



RfmDashboardAction.template = 'setu_rfm_analysis.RfmDashboardMain';

registry.category('actions').add('rfm_dashboard_client_action', RfmDashboardAction);
