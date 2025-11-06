/** @odoo-module **/
import { rpc } from "@web/core/network/rpc";

    $(document).ready(async function() {
    if (document.location.pathname == '/en_US/my/statistics' || document.location.pathname == '/my/statistics'){
    debugger
        try {
        debugger
        var result = await rpc('/my/charts/purchase_history')
//          var result = await $.ajax({
//            type: 'POST',
//            dataType: 'json',
//            url: '/my/charts/purchase_history',
//            contentType: 'application/json',
//            data: JSON.stringify({'jsonrpc': "2.0", 'method': "call"}),
//            });
          if ($('html').attr('lang')== "es-MX"){
            var main_title = "Historial de Compras"
            var amount_label = "Dinero"
            var unit_label = "Unidades"
            var period_label = "Periodo"
          }
          else{
            var main_title = "Purchase History"
            var amount_label = "Money"
            var unit_label = "Units"
            var period_label = "Period"
          }
          var optionshistory = {
          series: [{
          name: amount_label,
          type: 'column',
          data: result.price_data
        }, {
          name: unit_label,
          type: 'line',
          data: result.unit_data
        }],
          chart: {
          height: 400,
          type: 'line',
          background: '#1E1F2F', //Added
          foreColor: '#f2f2f2', //Added
          zoom: {
            enabled: false
          }
        },
        colors: ['#FFAA00', '#66CCFF'],
        title: {
          text: main_title,
          style: { color: '#ffffff',fontWeight: 'bold' }
        },
        dataLabels: {
          enabled: true,
          style: { colors: ['#1a1010'] }, //added
          formatter: function (val) {
            return val.toLocaleString(); // Format amount data labels with commas
            },
        },
        stroke: {
            curve: 'smooth',
            width: [0, 3]
        },
        fill: {
            type:'solid',
            opacity: 1
          },
        xaxis: {
          categories: result.year_data,
            title: {
                text: period_label,
                style: { color: '#f2f2f2'}
            },
            labels: { style: { colors: '#f2f2f2' } }
        },
        yaxis: [{
          title: {
            text: amount_label,
            style: { color: '#ffffff'}
          },
          labels: {
        formatter: function (value) {
          return new Intl.NumberFormat().format(value); // Format number with commas
            },
        },

        }, {
          opposite: true,
          title: {
            text: unit_label,
            style: { color: '#ffffff'}
          },
          labels: {
        formatter: function (value) {
          return new Intl.NumberFormat().format(value); // Format number with commas
            }
        },
        }]
        };

        var chart = new ApexCharts(document.querySelector("#purchase_history_chart"), optionshistory);
        chart.render();
        } catch (error) {
            console.error("Error:", error);
        }

        // Product Category : Current Month Data
        try {
            debugger
            var result = await rpc('/my/charts/product_category/current_month')
            if ($('html').attr('lang')== "es-MX"){
                var main_title = "Este Mes"
            }
            else{
                var main_title = "This Month"
            }
            if (result.unit_data.length > 0 ){
                var options = {
                      series: result.unit_data,
                      chart: {
                      width: 500,
                      type: 'pie',
                    },
                    title: {
                        text: main_title,
                        style:{ color: '#ffffff', fontWeight: 'bold' }
                    },
                    labels: result.categ_data,
                    dataLabels: {
                    enabled: true,
                    style: {
                        fontSize: '14px',
                        fontFamily: 'Arial, sans-serif',
                        fontWeight: 'bold',
                        colors: ['#ffffff'] // Makes labels white
                            }
                        },
                    legend: {
                        labels: {
                            colors: '#ffffff', // Labels outside the pie chart (legend) in white
                            fontSize: '14px', // Increase size of legend labels
                            }
                        },
                    responsive: [{
                      options: {
                        legend: {
                           fontSize: '20px',
                           labels: { colors: '#ffffff' },
                           position: 'bottom'
                        }
                      }
                    }]
                    };
            var chart = new ApexCharts(document.querySelector("#categ_this_month_chart"), options);
            chart.render()
            }
//             else{
//        $("#categ_this_month_chart_main").remove();
//    }
        } catch (error) {
            console.error("Error:", error);
        }

        // Product Category Last Month Data
        try {
            debugger
            var result_for_last_month = await rpc('/my/charts/product_category/last_month')
            if ($('html').attr('lang')== "es-MX"){
                var main_title = "Mes Anterior"
            }
            else{
                var main_title = "Last Month"
            }
            if (result_for_last_month.unit_data.length > 0 ){
                var options = {
                      series: result_for_last_month.unit_data,
                      chart: {
                      width: 500,
                      type: 'pie',
                    },
                    title: {
                        text: main_title,
                        style: { color: '#ffffff'}
                    },
                    labels: result_for_last_month.categ_data,
                    dataLabels: {
                    enabled: true,
                    style: {
                        fontSize: '14px',
                        fontFamily: 'Arial, sans-serif',
                        fontWeight: 'bold',
                        colors: ['#ffffff'] // Makes labels white
                            }
                        },
                    legend: {
                        labels: {
                            colors: '#ffffff', //Labels outside the pie chart (legend) in white
                            fontSize: '14px', // Increase size of legend labels
                            }
                        },
                    responsive: [{
                      options: {
                        legend: {
                          position: 'bottom'
                        }
                      }
                    }]
                    };
                var chart = new ApexCharts(document.querySelector("#categ_last_month_chart"), options);
                chart.render()
            } else {
                $("#categ_last_month_chart_main").remove();
            }
        } catch (error) {
            console.error("Error:", error);
        }

        // Product Category last Quater  Data
        try {
            var result = await rpc('/my/charts/product_category/last_quater')
            if ($('html').attr('lang')== "es-MX"){
                var main_title = "Trimestre Anterior"
            }
            else{
                var main_title = "Last Quarter"
            }
            if (result.unit_data.length > 0 ){
                var options = {
                              series: result.unit_data,
                              chart: {
                              width: 500,
                              type: 'pie',
                            },
                            title: {
                                text: main_title,
                                style: { color: '#ffffff'}
                            },
                            labels: result.categ_data,
                            dataLabels: {
                                    enabled: true,
                                    style: {
                                        fontSize: '14px',
                                        fontFamily: 'Arial, sans-serif',
                                        fontWeight: 'bold',
                                        colors: ['#ffffff'] // Makes labels white
                                    }
                            },
                    legend: {
                        labels: {
                                colors: '#ffffff', //Labels outside the pie chart (legend) in white
                                fontSize: '14px', //Increase size of legend labels
                            }
                        },
                            responsive: [{
                              options: {
                                legend: {
                                  position: 'bottom'
                                }
                              }
                            }]
                            };
                    var chart = new ApexCharts(document.querySelector("#categ_last_quater_chart"), options);
                    chart.render()
            } else {
                    $("#categ_last_quater_chart_main").remove();
                    }

        } catch (error) {
            // Handle errors if any
            console.error("Error:", error);
        }

//        Payments
        try {
            var result_for_last_month = await rpc('/my/charts/payments')
            if (result_for_last_month.paid_after_due_date){
                $('#invoice_after_due').text(result_for_last_month.paid_after_due_date + "%")
            }
            if (result_for_last_month.paid_on_time){
                $('#invoice_on_time').text(result_for_last_month.paid_on_time + "%")
            }
        } catch (error) {
            // Handle errors if any
            console.error("Error:", error);
        }

        // Internal Operation
        try {
            var result = await rpc('/my/charts/internal_operation')
            if ($('html').attr('lang')== "es-MX"){
                var one = "< 1 Dia"
                var one_three ="1 - 3 Dias"
                var three_six ="3 - 6 Dias"
                var six = ">6 Dias"
            }
            else{
                var one = "< 1 Day"
                var one_three ="1 - 3 Days"
                var three_six ="3 - 6 Days"
                var six =" > 6 Days"
            }
            if (result.months.length > 0 ){
            var options = {
              series: [{
              name: one,
              data: result.one
            }, {
          name: one_three,
          data: result.one_three
        }, {
          name: three_six,
          data: result.three_six
        }, {
          name: six,
          data: result.six
        }],
          chart: {
          type: 'bar',
          height: 350,
          stacked: true,
          toolbar: {
            show: true
          },
          zoom: {
            enabled: true
          },
          background: '#1E1F2F',
          foreColor: '#f2f2f2',//Added
        },
        responsive: [{
          breakpoint: 480,
          options: {
            legend: {
              position: 'bottom',
              offsetX: -10,
              offsetY: 0
            },
          }
        }],
        plotOptions: {
          bar: {
            horizontal: false,
            borderRadius: 10,
            borderRadiusApplication: 'end', // 'around', 'end'
            borderRadiusWhenStacked: 'last', // 'all', 'last'
            dataLabels: {
              total: {
                enabled: true,
                style: {
                  fontSize: '13px',
                  fontWeight: 900,
                  color: '#ffffff'
                }
              }
            }
          },
        },
        xaxis: {
          categories: result.months,
        },
        legend: {
          position: 'bottom',
        },
        fill: {
                opacity: 1
              }
        };
        var chart = new ApexCharts(document.querySelector("#internal_operation"), options);
        chart.render();
        }
        } catch (error) {
            // Handle errors if any
            console.error("Error:", error);
        }
        }
    });
