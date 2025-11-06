odoo.define('ninebox_employee_performance.ninebox_report', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var framework = require('web.framework');
    var session = require('web.session');

    var _t = core._t;
    var QWeb = core.qweb;
    var Dialog = require('web.Dialog');

Dialog.validation_error = function (owner, message, options) {
var buttons = [{
    text: _t("Ok"),
    close: true,
    click: options && options.confirm_callback,
}];
return new Dialog(owner, _.extend({
    size: 'medium',
    buttons: buttons,
    $content: $('<main/>', {
        role: 'validation_error',
        text: message,
    }),
    title: _t("Validation Error"),
    onForceClose: options && (options.onForceClose || options.confirm_callback),
}, options)).open({shouldFocusButtons:true});
};

    
    var NineBox = AbstractAction.extend({
        hasControlPanel: true,
        events: {
            'click .employee_profile_box': 'onclick_employee_profile_box',
            'click .detailed_profile_arrow_back': 'onclick_profile_arrow_back',
            'click .emp_count_circle': 'onclick_performance_count',
            'click .employee_profile_box_panel': 'show_all_employee_profile_box',
            'change select#selected_assessment_period_id': '_onChangePeriod',
            'click .o_report_print': 'print_ninebox_report',
        },
        init: function (parent, action) {
            this._super.apply(this, arguments); 
            var self = this;
            var assessment_period = this._rpc({
                model: 'review.period.timeline',
                method: 'search',
                args: [[]]});
                if (!assessment_period){
                    Dialog.confirm(
                                   this,
                                   "There is no any records to review report.",
                                   {
                                       onForceClose: function(){
                                            self.onForceClose = false;
                                       },
                                       confirm_callback: function(){
                                           self.confirm_callback = false;
                                       },
                                       cancel_callback: function(){
                                           self.cancel_callback = false;
                                       }
                                   }
                                );
                }

        },
        willStart: function () {
            var self = this;
            var assessment_period = this._rpc({
                model: 'review.period.timeline',
                method: 'search_read',
                orderBy: [{ name: 'id', desc: true }],
            }).then(function (res) {
                self.assessment_period = res;
            });
            return Promise.all([assessment_period,this._super.apply(this, arguments)]);
        },
        start: function(){
            var self = this;
            this.$buttons = $(QWeb.render('ninebox_employee_performance.ControlButtons', {widget: self}));
            this.controlPanelProps.cp_content = {
                $buttons: this.$buttons,
            };
            this.$select_button = this.$buttons.find('.selected_assessment_period_id');
            
            var assessment_period = this.assessment_period;
            if (typeof assessment_period != "undefined" && assessment_period != null && assessment_period.length != null && assessment_period.length > 0) {
                var assessment_period_last = self.assessment_period.length-1;                
                var assessment_period = self.assessment_period[assessment_period_last].assessment_period;
                
                if (assessment_period.length != null && assessment_period.length > 0){                
                    this.$select_button.children("option[value="+ assessment_period +"]").prop('selected',true);
                }

                var employee_performance = self._rpc({
                    model: 'employee.performance.report',
                    method: 'search_read',
                    kwargs: {                   
                        domain: [['assessment_period', '=', assessment_period]],
                    }
                })
                .then(function (res) {
                    self.performance_data = res;
                })
                .then(function(){
                    self.count_perpormance_rate();
                    var $NineBoxReport = $(QWeb.render("NineBoxReport", {widget: self}));
                    $NineBoxReport.appendTo(self.$('.o_content'));                    
                });

                var emp_asses_ques_rev = self._rpc({
                    model: 'employee.assessment.questions.review',
                    method: 'search_read',
                    kwargs: {                   
                        domain: [['assessment_period', '=', assessment_period]],
                    }
                })
                .then(function (res) {                
                    self.emp_asses_ques_rev = res;                    
                })
                .then(function(){                    
                    self.show_all_employee_profile_box();
                });                
                }

            return Promise.all([
                this._super.apply(this, arguments),
                employee_performance, 
                emp_asses_ques_rev,            
            ]);
        },
        update_cp: function() {
            if (!this.$buttons) {
                this.renderButtons();
            }
            this.controlPanelProps.cp_content = { $buttons: this.$buttons };
            return this.updateControlPanel();
        },
        renderButtons: function() {
            var self = this;
            this.$buttons = $(QWeb.render("ninebox_employee_performance.ControlButtons", {widget: self}));
            return this.$buttons;      
        },
        render: function() {
            var self = this;
            self.count_perpormance_rate();
            self.$('.o_content').empty();
            var $NineBoxReport = $(QWeb.render("NineBoxReport", {widget: self}));
            $NineBoxReport.appendTo(self.$('.o_content'));
            self.show_all_employee_profile_box();
        },
        do_show: function() {
            this._super();
            this.update_cp();
        },
        _onChangePeriod: function(ev){
            var self = this; 
            var $input = $(ev.target).val();
           
            var emp_asses_ques_rev = self._rpc({
                model: 'employee.assessment.questions.review',
                method: 'search_read',
                kwargs: {
                    domain: [['assessment_period', '=', $input ]],
                }
            })
            .then(function (res) {   
                self.emp_asses_ques_rev = res;  
            })
            .then(function(){                
                self.render();
                if ($input.length != null && $input.length > 0){ 
                    self.$el.find('.selected_assessment_period_id').children('option[value='+ $input +']').prop('selected',true);
                }
            });

            var employee_performance = self._rpc({
                model: 'employee.performance.report',
                method: 'search_read',
                kwargs: {                   
                    domain: [['assessment_period', '=', $input]],
                }
            })
            .then(function (res) {
                self.performance_data = res;                
            })
            .then(function(){
                self.render();
                if ($input.length != null && $input.length > 0){
                    self.$el.find('.selected_assessment_period_id').children('option[value='+ $input +']').prop('selected',true);    
                }
            });
        },
        count_perpormance_rate: function(){
            var self = this;
            
            var count_1x1 = 0;
            var count_1x2 = 0;
            var count_1x3 = 0;

            var count_2x1 = 0;
            var count_2x2 = 0;
            var count_2x3 = 0;

            var count_3x1 = 0;
            var count_3x2 = 0;
            var count_3x3 = 0;

            var performance_data = this.performance_data;       
            if (typeof performance_data != "undefined" && performance_data != null && performance_data.length != null && performance_data.length > 0) {
                for (var i = 0; i < performance_data.length; i++ ) {     
                    //   1x1 - 1x5   //
                    if(performance_data[i].pot_per_rate === '1_1'){
                        count_1x1 += 1 ;
                    }
                    if(performance_data[i].pot_per_rate === '1_2'){
                        count_1x2 += 1 ;
                    }
                    if(performance_data[i].pot_per_rate === '1_3'){
                        count_1x3 += 1 ;
                    }

                    //   2x1 - 2x5   //
                    if(performance_data[i].pot_per_rate === '2_1'){
                        count_2x1 += 1 ;
                    }
                    if(performance_data[i].pot_per_rate === '2_2'){
                        count_2x2 += 1 ;
                    }
                    if(performance_data[i].pot_per_rate === '2_3'){
                        count_2x3 += 1 ;
                    }

                    //   3x1 - 3x5   //
                    if(performance_data[i].pot_per_rate === '3_1'){
                        count_3x1 += 1 ;
                    }
                    if(performance_data[i].pot_per_rate === '3_2'){
                        count_3x2 += 1 ;
                    }
                    if(performance_data[i].pot_per_rate === '3_3'){
                        count_3x3 += 1 ;
                    }
                    
                }
            }

            self.count_1x1 = (count_1x1 <10) ? '0' + count_1x1.toString() : count_1x1.toString() ;
            self.count_1x2 = (count_1x2 <10) ? '0' + count_1x2.toString() : count_1x2.toString() ;
            self.count_1x3 = (count_1x3 <10) ? '0' + count_1x3.toString() : count_1x3.toString() ;

                
            self.count_2x1 = (count_2x1 <10) ? '0' + count_2x1.toString() : count_2x1.toString() ;
            self.count_2x2 = (count_2x2 <10) ? '0' + count_2x2.toString() : count_2x2.toString() ;
            self.count_2x3 = (count_2x3 <10) ? '0' + count_2x3.toString() : count_2x3.toString() ;

                
            self.count_3x1 = (count_3x1 <10) ? '0' + count_3x1.toString() : count_3x1.toString() ;
            self.count_3x2 = (count_3x2 <10) ? '0' + count_3x2.toString() : count_3x2.toString() ;
            self.count_3x3 = (count_3x3 <10) ? '0' + count_3x3.toString() : count_3x3.toString() ;
        },
        get_x_y_rate: function(box_value){
            var rate = {
                'x' : '',
                'y' : '',
                'x_rating': '',
                'y_rating': '',
                'bgcolor':'#d9d9d9',
            };
            //   1x1 - 1x3   //
            if(box_value === '1_1'){
                var rate = {
                    'x' : 'Se puede considerar desvincularte de la empresa',
                    'y' : 'Presentas serias dificultades para alcanzar tus metas',
                    'x_rating': '1',
                    'y_rating': '1',
                    'bgcolor':'#e51c21',
                };
            }
            if(box_value === '1_2'){
                var rate = {
                    'x' : 'Necesitamos más de ti, tu desempeño no es suficiente',
                    'y' : 'Puedes crecer si te decides a mejorar en tus actividades',
                    'x_rating': '1',
                    'y_rating': '2',
                    'bgcolor':'#f7984e',
                };
            }
            if(box_value === '1_3'){
                var rate = {
                    'x' : 'Necesitas aprender más de tu área, tu desempeño se ve pobre',
                    'y' : 'Tu talento puede estar  mal ubicado',
                    'x_rating': '1',
                    'y_rating': '3',
                    'bgcolor':'#f2e60e',
                };
            }
            
            //   2x1 - 2x3   //
            if(box_value === '2_1'){
                var rate = {
                    'x' : 'Tu desempeño es sólido',
                    'y' : 'No se ve mucha convicción por tener crecimiento con nosotros',
                    'x_rating': '2',
                    'y_rating': '1',
                    'bgcolor':  '#f7984e',
                };
            }
            if(box_value === '2_2'){
                var rate = {
                    'x' : 'Contribuyes a los objetivos de tu departamento y el grupo',
                    'y' : 'Tienes el balance que necesitamos, llegaste a una estabilidad laboral.',
                    'x_rating': '2',
                    'y_rating': '2',
                    'bgcolor':  '#f2e60e',
                };
            }
            if(box_value === '2_3'){
                var rate = {
                    'x' : 'No pares el ritmo estas aprendiendo muy bien.',
                    'y' : 'Estas listo para nuevas oportunidades en el grupo.',
                    'x_rating': '2',
                    'y_rating': '3',
                    'bgcolor':  '#9ac05d',
                };
            }            
            
            //   3x1 - 3x3   //
            if(box_value === '3_1'){
                var rate = {
                    'x' : 'Cumples tus funciones de manera excepcional.',
                    'y' : 'Puedes estar topado en tus actividades, necesitas delegar para que puedas crecer.',
                    'x_rating': '3',
                    'y_rating': '1',
                    'bgcolor':  '#f2e60e',
                };
            }
            if(box_value === '3_2'){
                var rate = {
                    'x' : 'Cumples todas las expectativas, tu desempeño es sobresaliente.',
                    'y' : 'Tienes madera para llegar muy lejos dentro de la compañía.',
                    'x_rating': '3',
                    'y_rating': '2',
                    'bgcolor':  '#9ac05d',
                };
            }
            if(box_value === '3_3'){
                var rate = {
                    'x' : 'No conoces los  límites del aprendizaje, no te detengas.',
                    'y' : 'Eres el próximo en tener un cargo estrátegico',
                    'x_rating': '3',
                    'y_rating': '3',
                    'bgcolor':  '#0d8537',
                };
            }

            return rate
        },
        onclick_performance_count: function(ev){
            var self = this;   
            var performance_data = this.performance_data;        
            var box_value = ev.currentTarget.getAttribute('value');
            var html = '';
            self.$el.find('.emp_box_list_panel_area').empty();
            if (typeof performance_data != "undefined" && performance_data != null && performance_data.length != null && performance_data.length > 0) {      
                for (var i = 0; i < performance_data.length; i++ ) {
                    if(performance_data[i].pot_per_rate === box_value){
                        var emp_id = performance_data[i].employee_id[0];
                        
                        var rate = this.get_x_y_rate(box_value);
                                                
                        // Employee Profile Box List // 
                        html = '<div class="employee_profile_box">';
                        html += '<table width="100%" border="0" style="border-spacing: 2px; border-collapse: separate;" cellpadding="0" class="right_p_emp_box">';
                        html += '<tr>';
                        html += '<td width="100%" height="25" class="emp_name">'+ performance_data[i].employee_name +'</td>';                        
                        html += '</tr>';
                        html += '<tr>';
                        html += '<td height="20" class="emp_title">'+ performance_data[i].job_position +'</td>';
                        html += '</tr>';
                        html += '<tr>';
                        html += '<td>';
                        html += '<table width="100%" border="0" style="border-spacing: 1px; border-collapse: separate;" cellpadding="0">';
                        html += '<tr>';
                        html += '<td width="19%" rowspan="2" style="background-color: #d9d9d9;"><img src="/web/image?model=hr.employee&field=image_128&id='+ performance_data[i].employee_id[0] +'" width="60" height="60" /></td>';
                        html += '<td width="27%" height="30" align="left" bgcolor="#d9d9d9" class="emp_range_label">Potencial</td>';
                        html += '<td width="20" align="center" valign="middle" bgcolor="'+ rate['bgcolor'] +'" class="emp_range_value">'+ rate['y_rating'] +'</td>';
                        html += '<td width="42%" align="left" bgcolor="'+ rate['bgcolor'] +'" class="emp_range">'+ rate['y'] +'</td>';
                        html += '</tr>';
                        html += '<tr>';
                        html += '<td height="30" align="left" bgcolor="#D9D9D9" class="emp_range_label">Desempeño</td>';
                        html += '<td width="20" align="center" valign="middle" bgcolor="'+ rate['bgcolor'] +'" class="emp_range_value">'+ rate['x_rating'] +'</td>';
                        html += '<td align="left" bgcolor="'+ rate['bgcolor'] +'" class="emp_range">'+ rate['x'] +'</td>';
                        html += '</tr>';
                        html += '</table>';
                        html += '</td>';
                        html += '</tr>';
                        html += '</table>';
                        html += '<div class="overlay"><img src="/ninebox_employee_performance/static/src/img/emp_details_icon_arrow.png" width="19" height="80" /></div>';
                        html += '</div>';

                        // Employee Profile Box Detailed// 
                        html += '<div class="employee_profile_box_detailed">';
                        html += '<table width="100%" border="0" style="border-spacing: 2px; border-collapse: separate;" cellpadding="0" class="right_p_emp_box">';
                        html += '<tr><td height="25" bgcolor="#d9d9d9" class="emp_name"><table width="100%" border="0" cellspacing="0" cellpadding="0" class="detailed_profile_arrow_back">';
                        html += '<tr><td width="91%">&nbsp;</td>';
                        html += '<td width="9%"><img src="/ninebox_employee_performance/static/src/img/large-hover-arrow-back.png" width="29" height="13" /></td></tr>';
                        html += '</table></td></tr>';
                        html += '<tr><td height="25" class="emp_name">'+ performance_data[i].employee_name +'</td></tr>';
                        html += '<tr><td height="20" class="emp_title">'+ performance_data[i].job_position +'</td></tr>';
                        html += '<tr><td>';
                        html += '<table width="100%" border="0" style="border-spacing: 1px; border-collapse: separate;" cellpadding="0"><tr>';
                        html += '<td width="19%" rowspan="2" style="background-color: #d9d9d9;"><img src="/web/image?model=hr.employee&field=image_128&id='+ performance_data[i].employee_id[0] +'" width="60" height="60" /></td>';
                        html += '<td width="27%" height="30" align="left" bgcolor="#d9d9d9" class="emp_range_label">Potencial</td>';
                        html += '<td width="20" align="center" valign="middle" bgcolor="'+ rate['bgcolor'] +'" class="emp_range_value">'+ rate['y_rating'] +'</td>';
                        html += '<td width="42%" align="left" bgcolor="'+ rate['bgcolor'] +'" class="emp_range">'+ rate['y'] +'</td></tr>';
                        html += '<tr>';
                        html += '<td height="30" align="left" bgcolor="#D9D9D9" class="emp_range_label">Desempeño</td>';
                        html += '<td width="20" align="center" valign="middle" bgcolor="'+ rate['bgcolor'] +'" class="emp_range_value">'+ rate['x_rating'] +'</td>';
                        html += '<td align="left" bgcolor="'+ rate['bgcolor'] +'" class="emp_range">'+ rate['x'] +'</td></tr>';
                        html += '</table>';
                        html += '</td></tr>';
                        html += '<tr><td>';
                        html += '<table width="100%" border="0" cellspacing="0" cellpadding="0">';
                        html += '<tr><td height="25" align="left" valign="middle" class="assesment_header p-2"> Employee Assessment Questions</td></tr>';
                        html += '<tr>';
                        html += '<td>'
                        
                        html += self.get_question_review(emp_id);
                        
                        html += '</td>';
                        html += '</tr>';
                        html += '</table>';
                        html += '</td></tr>';
                        html += '</table>';
                        html += '</div>';

                        self.$el.find('.emp_box_list_panel_area').append(html);                    
                    }
                }
            }
        },
        onclick_employee_profile_box: function(ev){
            ev.preventDefault();
            var $employee_profile_box = $(ev.currentTarget);
            $('[class=employee_profile_box]').hide();
            var $employee_profile_box_detailed = $employee_profile_box.next();
            $employee_profile_box_detailed.toggle(300);
        },
        onclick_profile_arrow_back: function(){
            $('[class=employee_profile_box_detailed]').hide();
            $('[class=employee_profile_box]').toggle(300);
        },
        get_question_review: function(employee_id){
            var self= this;
            var emp_asses_ques_rev = self.emp_asses_ques_rev;            
            var html = '';  
            if (typeof emp_asses_ques_rev != "undefined" && emp_asses_ques_rev != null && emp_asses_ques_rev.length != null && emp_asses_ques_rev.length > 0) {
                for (var i=0; i< emp_asses_ques_rev.length;i++){                      
                    if (employee_id === emp_asses_ques_rev[i].employee_id[0]){
                        if (emp_asses_ques_rev[i].assessment_question_id[1]){
                            html += '<h4 class="pl-2 pr-2" style="font-size: small; font-family: arial; padding-top: 10px;">'+ emp_asses_ques_rev[i].assessment_question_id[1]  +'</h4>';
                        }else{
                            html += '<h4 class="pl-2 pr-2" style="font-size: small; font-family: arial; padding-top: 10px;">  </h4>';
                        }

                        if (emp_asses_ques_rev[i].assessment_comment){
                            html += '<p class="pl-2 pr-2">'+ emp_asses_ques_rev[i].assessment_comment +'</p>';       
                        }else{
                            html += '<p class="pl-2 pr-2">  </p>';
                        }                               
                    }                              
                }
            }  
            return html;
        },
        show_all_employee_profile_box: function(){
            var self = this;
            var performance_data = this.performance_data;
            self.$el.find('.emp_box_list_panel_area').empty();
            var html = '';            
            if (typeof performance_data != "undefined" && performance_data != null && performance_data.length != null && performance_data.length > 0) {                
                for (var i = 0; i < performance_data.length; i++ ) {
                    var emp_id = performance_data[i].employee_id[0];
                    var rate = this.get_x_y_rate(performance_data[i].pot_per_rate);
                    
                    // Employee Profile Header //                 
                    html = '<div class="employee_profile_box">';
                    html += '<table width="100%" border="0" style="border-spacing: 2px; border-collapse: separate;" cellpadding="0" class="right_p_emp_box">';
                    html += '<tr>';
                    html += '<td width="89%" height="25" class="emp_name">'+ performance_data[i].employee_name +'</td>';                    
                    html += '</tr>';
                    html += '<tr>';
                    html += '<td height="20" class="emp_title">'+ performance_data[i].job_position +'</td>';
                    html += '</tr>';
                    html += '<tr>';
                    html += '<td>';
                    html += '<table width="100%" border="0" style="border-spacing: 1px; border-collapse: separate;" cellpadding="0">';
                    html += '<tr>';
                    html += '<td width="19%" rowspan="2" style="background-color: #d9d9d9;"><img src="/web/image?model=hr.employee&field=image_128&id='+ performance_data[i].employee_id[0] +'" width="60" height="60" /></td>';
                    html += '<td width="27%" height="30" align="left" bgcolor="#d9d9d9" class="emp_range_label">Potencial</td>';
                    html += '<td width="20" align="center" valign="middle" bgcolor="'+ rate['bgcolor'] +'" class="emp_range_value">'+ rate['y_rating'] +'</td>';
                    html += '<td width="42%" align="left" bgcolor="'+ rate['bgcolor'] +'" class="emp_range">'+ rate['y'] +'</td>';
                    html += '</tr>';
                    html += '<tr>';
                    html += '<td height="30" align="left" bgcolor="#D9D9D9" class="emp_range_label">Desempeño</td>';
                    html += '<td width="20" align="center" valign="middle" bgcolor="'+ rate['bgcolor'] +'" class="emp_range_value">'+ rate['x_rating'] +'</td>';
                    html += '<td align="left" bgcolor="'+ rate['bgcolor'] +'" class="emp_range">'+ rate['x'] +'</td>';
                    html += '</tr>';
                    html += '</table>';
                    html += '</td>';
                    html += '</tr>';
                    html += '</table>';
                    html += '<div class="overlay"><img src="/ninebox_employee_performance/static/src/img/emp_details_icon_arrow.png" width="19" height="80" /></div>';
                    html += '</div>';
                    
                    // Employee Profile Panel // 
                    html += '<div class="employee_profile_box_detailed">';
                    html += '<table width="100%" border="0" style="border-spacing: 2px; border-collapse: separate;" cellpadding="0" class="right_p_emp_box">';
                    html += '<tr><td height="25" bgcolor="#d9d9d9" class="emp_name"><table width="100%" border="0" cellspacing="0" cellpadding="0" class="detailed_profile_arrow_back">';
                    html += '<tr><td width="91%">&nbsp;</td>';
                    html += '<td width="9%"><img src="/ninebox_employee_performance/static/src/img/large-hover-arrow-back.png" width="29" height="13" /></td></tr>';
                    html += '</table></td></tr>';
                    html += '<tr><td height="25" class="emp_name">'+ performance_data[i].employee_name +'</td></tr>';
                    html += '<tr><td height="20" class="emp_title">'+ performance_data[i].job_position +'</td></tr>';
                    html += '<tr><td>';
                    html += '<table width="100%" border="0" style="border-spacing: 1px; border-collapse: separate;" cellpadding="0"><tr>';
                    html += '<td width="19%" rowspan="2" style="background-color: #d9d9d9;"><img src="/web/image?model=hr.employee&field=image_128&id='+ performance_data[i].employee_id[0] +'" width="60" height="60" /></td>';
                    html += '<td width="27%" height="30" align="left" bgcolor="#d9d9d9" class="emp_range_label">Potencial</td>';
                    html += '<td width="20" align="center" valign="middle" bgcolor="'+ rate['bgcolor'] +'" class="emp_range_value">'+ rate['y_rating'] +'</td>';
                    html += '<td width="42%" align="left" bgcolor="'+ rate['bgcolor'] +'" class="emp_range">'+ rate['y'] +'</td></tr>';
                    html += '<tr>';
                    html += '<td height="30" align="left" bgcolor="#D9D9D9" class="emp_range_label">Desempeño</td>';
                    html += '<td width="20" align="center" valign="middle" bgcolor="'+ rate['bgcolor'] +'" class="emp_range_value">'+ rate['x_rating'] +'</td>';
                    html += '<td align="left" bgcolor="'+ rate['bgcolor'] +'" class="emp_range">'+ rate['x'] +'</td></tr>';
                    html += '</table>';
                    html += '</td></tr>';
                    html += '<tr><td>';
                    html += '<table width="100%" border="0" cellspacing="0" cellpadding="0">';
                    html += '<tr><td height="25" align="left" valign="middle" class="assesment_header p-2"> Employee Assessment Questions</td></tr>';
                    html += '<tr>';
                    html += '<td>'
                    
                    html += self.get_question_review(emp_id);
                    
                    html += '</td>';
                    html += '</tr>';
                    html += '</table>';
                    html += '</td></tr>';
                    html += '</table>';
                    html += '</div>';                    
                                      
                    self.$el.find('.emp_box_list_panel_area').append(html);                    
                }
            }
        },
        print_ninebox_report: function(){
            var self = this;
            var period = self.$el.find('.selected_assessment_period_id').val();
            if (!period){
                Dialog.validation_error(
                       this,
                       _t("There is no any records to review report."),
                       {
                           onForceClose: function(){
                                self.onForceClose = false;
                           },
                           confirm_callback: function(){
                               self.confirm_callback = false;
                           },
                           cancel_callback: function(){
                               self.cancel_callback = false;
                           }
                       }
                    );
                return false;
            }
            framework.blockUI();
            session.get_file({
                url: '/ninebox_report/pdf/',
                data: { data: JSON.stringify([period]),'token':"dummy-because-api-expects-one"},
                complete: framework.unblockUI,
                error: (error) => this.call('crash_manager', 'rpc_error', error),
            });
        },

    });
    core.action_registry.add('ninebox_employee_performance.ninebox_report', NineBox);
    return NineBox;
});