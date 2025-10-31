/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
//var ajax = require('web.ajax');
import { _t } from "@web/core/l10n/translation";
var current_fs, next_fs, previous_fs; //fieldsets
var opacity;
var current = 1;
var steps = document.querySelectorAll("fieldset").length;
var reload = false;
import publicWidget from '@web/legacy/js/public/public_widget';

    publicWidget.registry.ecommerce_checkout = publicWidget.Widget.extend({
    selector: '.setu_ecommerce_checkout_extended',
    events: {
            'click .next,#account_information_form_submit': 'onClickNext',
            'click .previous': 'onClickPrevious',
            'click .btn-add-address' : 'onClickAddAddress',
//            'click .btn-default-address' : 'onClickSetAddress', ########----------no more needed
            'click .step_link' : 'onClickSteps',
            'blur .rfc_box': '_rfc_box_change',
            'change #required_invoice': 'onChangeRequiredInvoice',
            'change .shipping #country_id': 'onChangeShippingCountry',
            'change .billing #billing_country_id': 'onChangeBillingCountry',
            'click .delete_address' : 'onClickDeleteAddress',
            'click .edit_address' : 'onClickEditAddress',
            'click #request_as_user' : 'onClickRequestUser',
            'blur #billing_zip, #shipping_postal_code': 'onBlurBillingZip',
        },
        start: function () {
            var self = this;
            var url = new URL(window.location.href);
            // set default progressbar value and animation
             if(url.searchParams.get('steps')){

                if(!(parseInt(url.searchParams.get('steps')) <= 0 || parseInt(url.searchParams.get('steps')) > $("fieldset").length)){
                    if(! $('#required_invoice').is(":checked")){
                            if(url.searchParams.get('steps') == 3){
                                url.searchParams.set("steps", "1")
                            }
                    }
                    current = parseInt(url.searchParams.get('steps'));
                        window.history.pushState("", "", '/my/manage-address');
                    $('fieldset').hide()
                    $($('fieldset')[current-1]).show()

                    for (var i=1; i<current; i++)
                    {
                        $("#progressbar li").eq(i).addClass("active");
                    }
                }
             }
            self.setProgressBar(current)
            // set required_invoice checked value based on state
            var required_invoice = document.getElementById('required_invoice')
            if(required_invoice){
                if (required_invoice.getAttribute('readonly') == 'notdisabled'){
                     required_invoice.readonly = false
                }
                if ($(".company_information_form").find('input[name="rfc"]')[0].getAttribute('readonly') == 'notdisabled'){
                     $(".company_information_form").find('input[name="rfc"]').attr('readonly', false);
                }
                if ($(".company_information_form").find('input[name="company_name"]')[0].getAttribute('readonly') == 'notdisabled'){
                     $(".company_information_form").find('input[name="company_name"]').attr('readonly', false);
                }
                if (required_invoice.getAttribute('readonly') == 'notdisabled'){
                     required_invoice.readonly = false
                }
                if (required_invoice.getAttribute('checked') == 'False'){
                    required_invoice.checked = false
                    $('.required_invoice').addClass('d-none');
                    $('#rfc_form').removeClass('d-block');
                    $('#rfc_form').addClass('d-none');
                }
                else if(required_invoice.checked){
                    $('.required_invoice').removeClass('d-none');
                    $('#rfc_form').removeClass('d-none');
                    $('#rfc_form').addClass('d-block');
                }
            }
            return this._super.apply(this, arguments);
        },
        onClickNext:async function(ev){
        debugger
            var self = this;
            var form_id = $(ev.currentTarget).attr('data-id')
            var frm = $("."+form_id);

            var validated = await self.checkValidation(frm)
             var arr_data = frm.serializeArray()
            var msg = " has been Saved Successfully."
                    if($('html').attr('lang')== "es-MX"){
                        msg = " ha sido guardada."
                    }
            var error_msg = "Something Went Wrong Please Check Data Properly Before Submitting."
                    if($('html').attr('lang')== "es-MX"){
                        error_msg = "Algo ha fallado Por favor, compruebe los datos correctamente antes de enviarlos."
                    }
            if(validated == true){
                $('.setu_loader_class').addClass('show_loader');
                $('#msform').addClass('pe-none')
                $.ajax({
                type: 'post',
                url: '/my/manage-address/account',
                data: frm.serialize(),
                success: function (data) {
                    if(! (required_invoice.getAttribute('disabled') == 'disabled' && $(ev.currentTarget).attr('data-id') == 'company_information_form')){
                        self.custom_toast($($('#progressbar').find('li.active')[$('#progressbar').find('li.active').length - 1]).children().html() +msg,'success')
                    }
                    else{
                        self.custom_toast('Your Data Saved Successfully','info')
                    }
                    reload = true
                    if(reload){
                        var url = new URL(window.location.href);
                        if(current >= 4){
                            current = 3
                        }
                        if(! $('#required_invoice').is(":checked")){
                                if(current == 2){
                                    current = 3
                                }
                        }
                        url.searchParams.set('steps', (current+1));
                        window.location.href = url;
                    }
                    current_fs = $(ev.currentTarget).parent().parent();

                    next_fs = current_fs.next();
                        //Add Class Active
                        $("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");
                        //show the next fieldset
                        next_fs.show();
                        //hide the current fieldset with style
                        current_fs.animate({
                            opacity: 0
                        }, {
                            step: function(now) {
                                // for making fielset appear animation
                                opacity = 1 - now;
                                current_fs.css({
                                    'display': 'none',
                                    'position': 'relative'
                                });
                                next_fs.css({
                                    'opacity': opacity
                                });
                            },
                            duration: 500
                        });
                        self.setProgressBar(++current)
                },
                error: function (data) {
                    self.custom_toast(_t(data.statusText),'error')
                    self.custom_toast(_t(error_msg),'error')
                },
            });
            }
       },
       onClickPrevious: function(ev){
            current_fs = $(ev.currentTarget).parent().parent();
            previous_fs = current_fs.prev();
            $('.setu_loader_class').addClass('show_loader');
             reload = true
                if(reload){
                    if(! $('#required_invoice').is(":checked")){
                            if(current == 4){
                                current = 3
                            }
                    }
                    var url = new URL(window.location.href);
                    if(!(current < 0 && current >= $("fieldset").length)){
                        url.searchParams.set('steps', (current-1));
                        window.location.href = url;
                    }

                }
            //Remove class active
            $("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");

            //show the previous fieldset
            previous_fs.show();

            //hide the current fieldset with style
            current_fs.animate({
            opacity: 0
            }, {
            step: function(now) {
            // for making fielset appear animation
            opacity = 1 - now;

            current_fs.css({
            'display': 'none',
            'position': 'relative'
            });
            previous_fs.css({
            'opacity': opacity
            });
            },
            duration: 500
            });
            this.setProgressBar(--current)
        },
        onClickAddAddress: function(ev){
            var self= this
            var msg = "You Already Open Form"
                    if($('html').attr('lang')== "es-MX"){
                        msg = "Ya tiene un formulario abierto"
                    }
            if( $('.form-shipping').hasClass('d-none')){
                $('.form-shipping').removeClass('d-none')
                $('.btn-last-previous').addClass('d-none')
            }
            else{
                self.custom_toast(_t(msg),'info')
            }
        },
        onClickSteps: function(ev){
            var self = this
            var cus_form = $('fieldset[style=""]')
            if(cus_form.length == 0){
                var cus_form = $('fieldset[style="display: block;"]')
            }
            if(cus_form.length == 0){
                var cus_form = $(document.querySelector('fieldset:first-of-type'))
            }
            var cur_url = new URL(window.location.href);
            var cur_step = parseInt($('#progressbar').find('.active').last().attr('data-step'));

            if(parseInt($(ev.currentTarget).attr('data-step')) < cur_step){
                var link = parseInt($(ev.currentTarget).attr('data-step'))
                var url = new URL(window.location.href);
                 url.searchParams.set('steps', (link));
                  window.location.href = url;
            }
            else if(! (parseInt($(ev.currentTarget).attr('data-step')) == cur_step)){
                var cus_click = cus_form.find('.next').trigger('click')
            }
            if($('.toast-error').length == 0){
                var link = parseInt($(ev.currentTarget).attr('data-step'))
                var url = new URL(window.location.href);
                 url.searchParams.set('steps', (link));
                 window.location.href = url;
            }
        },
        _rfc_box_change: async function(ev){
             var self = this;
            var form_id = $(ev.currentTarget).attr('data-id')
             var frm = $("."+form_id);
             if(! frm.find('input[name="rfc"]').attr('readonly')){
                 await rpc('/my/manage-address/check_rfc', {'rfc': frm.find('[name="rfc"]').val(),'company_name':frm.find('[name="company_name"]').val()}).then(async function (data){
                        if(data['company_name'] != ''){
                            $('button[data-id="company_information_form"].next').addClass('d-none')
                         }
                         else{
                            $('button[data-id="company_information_form"].next').removeClass('d-none')
                         }
                      if(data['company_name'] != ''){
                        $(".company_box").val(data['company_name'])
                        var company_type = data['setu_company_type']
                        $('.company_information_form select[name="setu_company_type"] option[value='+data['setu_company_type']+']').attr("selected", "selected");
                        if(! $('.company_information_form select[name="setu_company_type"]').hasClass('pe-none')){
                            $('.company_information_form select[name="setu_company_type"]').addClass('pe-none');
                        }
                        $('#request_as_user').attr("value",data['company_id']);
                        $('.contact_alert').removeClass('d-none');
                      }
                      else{
                        $(".company_box").val('')
                         if($('.company_information_form select[name="setu_company_type"]').hasClass('pe-none')){
                            $('.company_information_form select[name="setu_company_type"]').removeClass('pe-none');
                        }
                        if(! $('.contact_alert').hasClass('d-none')){
                            $('.contact_alert').addClass('d-none');
                        }
                      }
                  })
             }
        },
        onChangeRequiredInvoice: function(ev){
             if(ev.currentTarget.checked) {
                $('.required_invoice').removeClass('d-none');
                    $('#rfc_form').removeClass('d-none');
                    $('#rfc_form').addClass('d-block');
                }
            else{
                $('.required_invoice').addClass('d-none');
                $('#rfc_form').removeClass('d-block');
                $('#rfc_form').addClass('d-none');
            }
        },
        onChangeShippingCountry: function(e){
             var optionSelected = $(".shipping #country_id option:selected");
            $(".shipping #country_states_id").find('option').prop('disabled', true);
            var current_country_id =  optionSelected.val()
            var enabled_options = $(".shipping #country_states_id").find("[states='" + current_country_id + "']")
            enabled_options.prop('disabled', false)
            if(enabled_options.length == 0){
                $(".shipping #country_states_id").prop('selectedIndex', -1)
            }
            if(enabled_options.length > 0){
                $(".shipping #country_states_id").css("display", "block");
                $(".shipping #country_states_id").parent().find('.shipping_states').css("display", "block");
            }
            else{
                $(".shipping #country_states_id").parent().find('.shipping_states').css("display", "none");
                 $(".shipping #country_states_id").css("display", "none");
            }
        },
        onChangeBillingCountry: function(e){

             var optionSelected = $(".billing #billing_country_id option:selected");
            $(".billing #country_states_id").find('option').prop('disabled', true);
            var current_country_id =  optionSelected.val()
            var enabled_options = $(".billing #country_states_id").find("[states='" + current_country_id + "']")
            enabled_options.prop('disabled', false)
            if(enabled_options.length == 0){
                $(".billing #country_states_id").prop('selectedIndex', -1)
            }
            if(enabled_options.length > 0){
                $(".billing #country_states_id").css("display", "block");
                $(".billing #country_states_id").parent().find('.billing_states').css("display", "block");
            }
           else{
                $(".billing #country_states_id").parent().find('.billing_states').css("display", "none");
                $(".billing #country_states_id").css("display", "none");
            }
        },
        onClickDeleteAddress: function(ev){
            var self = this ;
            var partner_id = parseInt($(ev.currentTarget).attr('data-value'))
            var delete_success_msg = "Deleted Successful"
                    if($('html').attr('lang')== "es-MX"){
                        delete_success_msg = "Borrado con éxito"
                    }
            $('.setu_loader_class').addClass('show_loader');
            $.ajax({
                type: 'get',
                url: '/my/manage-address/account',
                data: {'partner_id':partner_id,'delete_address':true},
                success: function (data_obj) {
                    self.custom_toast(_t(delete_success_msg),'success')
                    document.location.href = '/my/manage-address?steps=4'
                },
                error: function (data_obj) {
                    self.custom_toast(_t(data_obj.statusText),'error')
                },
          })
        },
        onClickEditAddress: async function(ev){
        debugger
            var partner_id = parseInt($(ev.currentTarget).attr('data-value'))
            var values = {'partner_id': partner_id};
            await rpc('/my/manage-address/account/edit_address', values).then(async function (data){
                if( $('.form-shipping').hasClass('d-none')){
                    $('.form-shipping').removeClass('d-none')
                    $('.btn-last-previous').addClass('d-none')
                }
                $('#shipping_partner_id').val(data['partner_id'])
                $('#shipping_name').val(data['name'])
                $('#shipping_email').val(data['email'])
                $('#shipping_telephone').val(data['phone'])
                $('#shipping_postal_code').val(data['zip'])
                $('#shipping_street_and_number').val(data['street_number'])
                $('#shipping_street2').val(data['street2'])
                if(data['is_colony_selection']){
                    $('#shipping_colony').removeClass('d-none')
                    $('#shipping_colony_text').addClass('d-none')
                }
                else{
                    $('#shipping_colony_text').removeClass('d-none')
                    if(! $('#shipping_colony').hasClass('d-none')){
                        $('#shipping_colony').addClass('d-none')
                    }
                }
                $('#shipping_colony_text').val(data['colony'])
                $('#shipping_colony').html(data['colony_selection_string'])
                $('#shipping_city').val(data['city'])
                $(".shipping #country_states_id").find('option').prop('selected', false);
                $(".shipping #country_id").find("[value='" + data['country_id']  + "']").prop('selected', true)

                if(data['state_id']){
                debugger
                     $(".shipping #country_states_id").css("display", "block");
                     $(".shipping #country_states_id").find("[value='" + data['state_id']  + "']").prop('selected', true)
                }
            });
        },
        onClickRequestUser: async function(ev){
            var self = this

            var partner_id = parseInt($(ev.currentTarget).attr('value'))
            await rpc('/my/manage-address/request', {'partner_id':partner_id}).then(async function (data){
                   if(data['alert']){
                    self.custom_toast(data['alert'],'warning')
                   }
                  else if(! data['message'] == ''){
                    self.custom_toast(data['message'],'success')
                  }
                  else{
                    self.custom_toast('Something Went Wrong','error')
                  }
              })
        },
        onBlurBillingZip: async function(ev){
        debugger
            if($(ev.currentTarget).prop('id')=='shipping_postal_code'){
                 var self = this
                var zip = $(ev.currentTarget).val()
                var values = {'zip_code': zip};
                await rpc('/my/manage-address/account/colony', values).then(async function (data){
                console.log(data['colony'])
                    $('#shipping_city').val(data['city'] )
                    $('#shipping_colony').html(data['colony'] )
                    $('#shipping_colony_text').val(data['colony_text'])
                    if( data['country_id']){
                        $(".shipping #country_id").find("[value='" + data['country_id']  + "']").prop('selected', true)
                        $(".shipping #country_states_id").html(data['state_ids'])
                        $(".shipping #country_states_id").find("[value='" + data['state_id']  + "']").prop('selected', true)
                        $(".shipping #country_states_id").css("display", "block");
                    }
                     if(data['colony'] == ''){
                         $('#shipping_colony_text').removeClass('d-none')
                        $('#shipping_colony_text').addClass('d-block')
                        $('#shipping_colony').removeClass('d-block')
                        $('#shipping_colony').addClass('d-none')
                    }
                    else{
                        $('#shipping_colony_text').removeClass('d-block')
                        $('#shipping_colony_text').addClass('d-none')
                        $('#shipping_colony').removeClass('d-none')
                        $('#shipping_colony').addClass('d-block')
                    }
                });
            }
            else{
            debugger
                var self = this
                var zip = $(ev.currentTarget).val()
                var values = {'zip_code': zip};
                if (! ev.currentTarget.getAttribute('readonly')){
                    await rpc('/my/manage-address/account/colony', values).then(async function (data){
                    $('#billing_city').val(data['city'] )
                    $('#billing_colony').html(data['colony'] )
                    $('#billing_colony_text').val(data['colony_text'])
                    if( data['country_id']){
                        $(".billing #billing_country_id").find("[value='" + data['country_id']  + "']").prop('selected', true)
                        $(".billing #country_states_id").html(data['state_ids'])
                        $(".billing #country_states_id").find("[value='" + data['state_id']  + "']").prop('selected', true)
                        $(".billing #country_states_id").css("display", "block");
                        $(".billing #country_states_id").parent().find('.billing_states').css("display", "block");
                    }
                    if(data['colony'] == ''){
                         $('#billing_colony_text').removeClass('d-none')
                        $('#billing_colony_text').addClass('d-block')
                        $('#billing_colony').removeClass('d-block')
                        $('#billing_colony').addClass('d-none')
                    }
                    else{
                        $('#billing_colony_text').removeClass('d-block')
                        $('#billing_colony_text').addClass('d-none')
                        $('#billing_colony').removeClass('d-none')
                        $('#billing_colony').addClass('d-block')
                    }
                });
                }
            }
        },
        setProgressBar: function (curStep) {
            var steps = $("fieldset").length;
            var percent = parseFloat(100 / steps) * curStep;
            percent = percent.toFixed();
            $(".progress-bar").css("width", percent + "%")
        },
       checkValidation:  function(data){
            var arr_data = data.serializeArray()
            var self = this;
            var pre_fix = ""
            if(data.hasClass('account_information_form')){
                pre_fix = 'account_information_form'
            }
            if(data.hasClass('company_information_form')){
                pre_fix = 'company_information_form'
            }
            if(data.hasClass('billing_information_form')){
                pre_fix = 'billing_information_form'
            }
            if(data.hasClass('shipping_information_form')){
                pre_fix = 'shipping_information_form'
            }
//            var phoneno = /^\d{10}$/;
            var email = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
            var rfc = /[ `!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]/;
            var postal_code =  /[a-zA-Z]/g;
            var name_msg = "Please Fill Out Name"
                    if($('html').attr('lang')== "es-MX"){
                        name_msg = "Por favor, llene el campo Nombre"
                    }
            var street_msg = "Please Fill Out Street Name"
                    if($('html').attr('lang')== "es-MX"){
                        street_msg = "Por favor, llene el campo Calle"
                    }
            var state_msg = "Please Fill Out State"
                    if($('html').attr('lang')== "es-MX"){
                        state_msg = "Por favor, llene el campo Estado"
                    }
            var email_msg = "Please Fill Out Email"
                    if($('html').attr('lang')== "es-MX"){
                        email_msg = "Por favor, llene el campo Email"
                    }
            var proper_email_msg = "Please Fill Proper Email"
                    if($('html').attr('lang')== "es-MX"){
                        proper_email_msg = "Por favor, capture el campo Email correctamente"
                    }
            var number_msg = "Please Fill Out Phone Number"
                    if($('html').attr('lang')== "es-MX"){
                        number_msg = "Por favor, llene el campo Teléfono"
                    }
//            var proper_number_msg = "Please Fill Proper Phone Number"
//                    if($('html').attr('lang')== "es-MX"){
//                        proper_number_msg = "Por favor, capture el campo Télefono correctamente"
//                    }
            var postal_msg = "Please Fill Out Postal Code"
                    if($('html').attr('lang')== "es-MX"){
                        postal_msg = "Por favor, llene el campo Código postal"
                    }
            var proper_postal_msg = "Please Fill Proper Postal Code"
                    if($('html').attr('lang')== "es-MX"){
                        proper_postal_msg = "Por favor, capture el campo Código Postal correctamente"
                    }
            var rfc_msg = "Please Fill Out RFC Code"
                    if($('html').attr('lang')== "es-MX"){
                        rfc_msg = "Por favor, llene el campo RFC"
                    }
            var proper_rfc_msg = "Please Fill Proper RFC Code"
                    if($('html').attr('lang')== "es-MX"){
                        proper_rfc_msg = "Por favor, capture el campo RFC correctamente"
                    }
            var country_msg = "Please Fill Out Country"
                    if($('html').attr('lang')== "es-MX"){
                        country_msg = "Por favor, llene el campo País"
                    }
            var company_msg = "Please Fill Out Company Name"
                    if($('html').attr('lang')== "es-MX"){
                        company_msg = "Por favor, llene el campo Empresa"
                    }
            var colony_msg = "Please Fill Out Colony"
                    if($('html').attr('lang')== "es-MX"){
                        colony_msg = "Por favor, llene el campo Colonia"
                    }
            var city_msg = "Please Fill Out City"
                    if($('html').attr('lang')== "es-MX"){
                        city_msg = "Por favor, llene el campo Ciudad"
                    }

            for(var i=1;i<arr_data.length;i++){

                 if(arr_data[i]['name'] == 'name'){
                    if(arr_data[i]['value'] == ''){
                        self.custom_toast(_t(name_msg),'error')
                        $('.'+pre_fix+' input[name="name"]').addClass('border-danger')
                        return false
                    }
                    else{
                        $('.'+pre_fix+' input[name="name"]').removeClass('border-danger')
                    }
                }

                 if(arr_data[i]['name'] == 'email'){
                    if(arr_data[i]['value'] == ''){
                        self.custom_toast(_t(email_msg),'error')
                        $('.'+pre_fix+' input[name="email"]').addClass('border-danger')
                        return false
                    }
                    if(! arr_data[i]['value'].match(email)){
                        self.custom_toast(_t(proper_email_msg),'error')
                        $('.'+pre_fix+' input[name="email"]').addClass('border-danger')
                        return false
                    }
                    else
                    {
                        $('.'+pre_fix+' input[name="email"]').removeClass('border-danger')
                    }
                }

//                if(arr_data[i]['name'] == 'phone'){
//                    if(arr_data[i]['value'] == ''){
//                        self.custom_toast(_t(number_msg),'error')
//                        $('.'+pre_fix+' input[name="phone"]').addClass('border-danger')
//                        return false
//                    }
//                    if(! arr_data[i]['value'].match(phoneno)){
//                        self.custom_toast(_t(proper_number_msg),'error')
//                        $('.'+pre_fix+' input[name="phone"]').addClass('border-danger')
//                        return false
//                    }
//                    else
//                    {
//                        $('.'+pre_fix+' input[name="phone"]').removeClass('border-danger')
//                    }
//                }

                if(arr_data[i]['name'] == 'rfc'){
                    if(! $('.required_invoice').hasClass('d-none')){
                        if(arr_data[i]['value'] == ''){
                            self.custom_toast(_t(rfc_msg),'error')
                            $('.'+pre_fix+' input[name="rfc"]').addClass('border-danger')
                            return false
                        }
debugger
                        if($('select[name="setu_company_type"]').val() == 'pisical'){
                            if((arr_data[i]['value'].length<13 || arr_data[i]['value'].length>13)){
                                self.custom_toast(_t(proper_rfc_msg),'error')
                                $('.'+pre_fix+' input[name="rfc"]').addClass('border-danger')
                                return false
                            }
                        }
                        if(arr_data[i]['value'].match(rfc)){
                            self.custom_toast(_t(proper_rfc_msg),'error')
                            $('.'+pre_fix+' input[name="rfc"]').addClass('border-danger')
                            return false
                        }
                        else
                        {
                            $('.'+pre_fix+' input[name="rfc"]').removeClass('border-danger')
                        }
                    }
                }

                if(arr_data[i]['name'] == 'postal_code'){
                    if(arr_data[i]['value'] == ''){
                        self.custom_toast(_t(postal_msg),'error')
                        $('.'+pre_fix+' input[name="postal_code"]').addClass('border-danger')
                        return false
                    }
                    if(arr_data[i]['value'].match(postal_code)){
                        self.custom_toast(_t(proper_postal_msg),'error')
                        $('.'+pre_fix+' input[name="postal_code"]').addClass('border-danger')
                        return false
                    }
                    else
                    {
                        $('.'+pre_fix+' input[name="postal_code"]').removeClass('border-danger')
                    }
                }

                if(arr_data[i]['name'] == 'company_name'){
                    if(! $('.required_invoice').hasClass('d-none')){
                        if(arr_data[i]['value'] == ''){
                            self.custom_toast(_t(company_msg),'error')
                            $('.'+pre_fix+' input[name="company_name"]').addClass('border-danger')
                            return false
                        }
                        else
                        {
                            $('.'+pre_fix+' input[name="company_name"]').removeClass('border-danger')
                        }
                    }
                }

                if(arr_data[i]['name'] == 'street_and_number'){
                    var msg = "Please Fill Out Street And Number"
                    if($('html').attr('lang')== "es-MX"){
                        msg = "Por Favor, llene el campo Calle y Numero "
                    }
                    if(arr_data[i]['value'] == ''){
                        self.custom_toast(_t(msg),'error')
                        $('.'+pre_fix+' input[name="street_and_number"]').addClass('border-danger')
                        return false
                    }
                    else{
                        $('.'+pre_fix+' input[name="street_and_number"]').removeClass('border-danger')
                    }
                }

                if(arr_data[i]['name'] == 'city'){
                    if(arr_data[i]['value'] == ''){
                        self.custom_toast(_t(city_msg),'error')
                        $('.'+pre_fix+' input[name="city"]').addClass('border-danger')
                        return false
                    }
                    else{
                        $('.'+pre_fix+' input[name="city"]').removeClass('border-danger')
                    }
                }
                if(data.attr('class') == 'billing_information_form'){
                     if(arr_data[i]['name'] == 'colony' && (!$("#billing_colony").hasClass('d-none'))){
                        if(arr_data[i]['value'] == ''){
                            self.custom_toast(_t(colony_msg),'error')
                            $('.'+pre_fix+' input[name="colony"]').addClass('border-danger')
                            return false
                        }
                        else{
                            $('.'+pre_fix+' input[name="colony"]').removeClass('border-danger')
                        }
                    }

                     if(arr_data[i]['name'] == 'colony_text' && (! $("#billing_colony_text").hasClass('d-none'))){
                        if(arr_data[i]['value'] == ''){
                            self.custom_toast(_t(colony_msg),'error')
                             $('.'+pre_fix+' input[name="colony_text"]').addClass('border-danger')
                            return false
                        }
                         else{
                            $('.'+pre_fix+' input[name="colony_text"]').removeClass('border-danger')
                        }
                    }
                }
                if(data.attr('class') == 'form-shipping shipping_information_form'){
                    if(arr_data[i]['name'] == 'colony' && (!$("#shipping_colony").hasClass('d-none'))){
                        if(arr_data[i]['value'] == ''){
                            self.custom_toast(_t(colony_msg),'error')
                            $('.'+pre_fix+' input[name="colony"]').addClass('border-danger')
                            return false
                        }
                        else{
                            $('.'+pre_fix+' input[name="colony"]').removeClass('border-danger')
                        }
                    }

                     if(arr_data[i]['name'] == 'shipping_colony_text' && (! $("#shipping_colony_text").hasClass('d-none'))){
                        if(arr_data[i]['value'] == ''){
                            self.custom_toast(_t(colony_msg),'error')
                            $('.'+pre_fix+' input[name="shipping_colony_text"]').addClass('border-danger')
                            return false
                        }
                        else{
                            $('.'+pre_fix+' input[name="shipping_colony_text"]').removeClass('border-danger')
                        }
                    }
                }

                if(arr_data[i]['name'] == 'country_id'){
                    if(arr_data[i]['value'] == ''){
                        self.custom_toast(_t(country_msg),'error')
                        $('.'+pre_fix+' input[name="country_id"]').addClass('border-danger')
                        return false
                    }
                    else{
                        $('.'+pre_fix+' input[name="country_id"]').removeClass('border-danger')
                    }
                }

                if(arr_data[i]['name'] == 'street_name'){
                    if(arr_data[i]['value'] == ''){
                        self.custom_toast(_t(street_msg),'error')
                        $('.'+pre_fix+' input[name="street_name"]').addClass('border-danger')
                        return false
                    }
                    else{
                        $('.'+pre_fix+' input[name="street_name"]').removeClass('border-danger')
                    }
                }

                if(arr_data[i]['name'] == 'country_states_id'){
                    if(arr_data[i]['value'] == ''){
                        self.custom_toast(_t(state_msg),'error')
                        $('.'+pre_fix+' input[name="country_states_id"]').addClass('border-danger')
                        return false
                    }
                    else{
                        $('.'+pre_fix+' input[name="country_states_id"]').removeClass('border-danger')
                    }
                }

            }
                return true
       },
        custom_toast: function(title,type){
        debugger
            var self = this;
            var toasts = document.getElementById('toasts')
            var notif = document.createElement('div')
            notif.classList.add('my_toast')
            $(notif).addClass('toast-'+type)

                notif.innerText = title

                toasts.appendChild(notif)

                setTimeout(() => {
                   notif.remove()
                }, 3000);
        },
//         -----NO MORE NEEDED COMMENT BY JAY -------
//        onClickSetAddress: async function(ev){
//            var $form = $(ev.currentTarget).parent();
//            await $.ajax({
//            type: 'post',
//            url: $form.attr('action'),
//            data: $form.serialize()
//            }).then(function () {
//                console.log("success")
//            }).catch(function () {
//                console.log("error")
//            });
//
//            document.location.href = '/my/manage-address?steps=4'
////            await $.post($form.attr('action'), $form.serialize()+'&xhr=1')
//        },
    });
//});
