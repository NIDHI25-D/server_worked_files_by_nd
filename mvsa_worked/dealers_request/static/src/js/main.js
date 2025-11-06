/** @odoo-module **/
debugger
//const {getCookie, setCookie} = require('web.utils.cookies');
import { rpc } from "@web/core/network/rpc";
import { cookie } from "@web/core/browser/cookie";
import publicWidget from "@web/legacy/js/public/public_widget";

var myfile1, myfile2, myfile3,cash_myfile1,cash_myfile2;

//    $('#modal_close').click(function(){
//        document.cookie = 'no_more_popup' + "=" + true
//    });

    publicWidget.registry.dealer_request = publicWidget.Widget.extend({
    selector: '.dealer_request',
    events: {
            'change #cash_dealer': 'onChangeCashDealer',
//            'change #credit_dealer': 'onChangeCreditLimitRequest',
            'change #credit_limit_requested, #credit_dealer': 'onChangeCreditLimitRequest',
            'change #cash_jpg_pdf_format': 'onChangeCashDealerFileJpgPdfFormat',
            'change #cash_jpg_format': 'onChangeCashDealerFileJpgFormat',
            'change #jpg_pdf_format': 'onChangeCreditDealerFileJpgPdfFormat',
            'change #jpg_format': 'onChangeCreditDealerFileJpgFormat',
            'change #pdf_format': 'onChangeCreditDealerFilePdfFormat',
        },

        start: function () {
            if(cookie.get('no_more_popup') !='true'){
                document.cookie = 'no_more_popup' + "=" + false
                }
            if(cookie.get('no_more_popup')=='false'){
                $('.help_modal_add').click()
            }
//            $('.help_modal_add').click()
            $('.check_box_class').find('input[type="checkbox"]').change(function(ev){
                console.log($(ev.currentTarget.checked)[0])
                if($(ev.currentTarget.checked)[0]){
                    $(ev.currentTarget).parent().find("[type=file]").removeClass('d-none')
                    $(ev.currentTarget).parent().find("[type=file]").attr('required','1')
                }
                else{
                    $(ev.currentTarget).parent().find("[type=file]").addClass('d-none')
                    $(ev.currentTarget).parent().find("[type=file]").attr('required','false')
                }
            })
            return this._super.apply(this, arguments);
        },

        onChangeCashDealer: function(ev){
             if(ev.currentTarget.checked){
                $('.cash_dealer_view').removeClass('d-none');
                $('.credit_dealer_view').addClass('d-none');
                }
        },
//        onChangeCreditDealer: function(ev){
//            if(ev.currentTarget.checked){
//
//                this.onChangeCreditLimitRequest
//                $('.credit_dealer_view').removeClass('d-none');
//                $('.cash_dealer_view').addClass('d-none');
//            }
//        },
        onChangeCreditLimitRequest: function(ev){
        debugger
        if(ev.currentTarget.checked){

                this.onChangeCreditLimitRequest
                $('.credit_dealer_view').removeClass('d-none');
                $('.cash_dealer_view').addClass('d-none');
            }
            
            var creditLimit = document.getElementById('credit_limit_requested').options[document.getElementById('credit_limit_requested').selectedIndex].text;
            $('.credit_limit_req_value').val(creditLimit)
            if ($('.current_login').val() ==  'pisical'){
                if(parseInt(creditLimit.replace(/,/g, '')) < parseInt('450000')){

                    $('.balance_sheet').hide()
                    $('.income_statements').hide()
                     $('.power_of_attorney').hide()
                    $('.constitutive_act').hide()
//                    $('.power_of_attorney').show()
//                    $('.constitutive_act').show()
                    $('.check_box_class').find('input[type="file"][id="pdf_format"][name="balance_sheet"]').addClass('d-none');
                    $('.check_box_class').find('input[type="file"][id="pdf_format"][name="income_statements"]').addClass('d-none');
                    $('.check_box_class').find('input[type="file"][id="pdf_format"][name="power_of_attorney"]').addClass('d-none');
                    $('.check_box_class').find('input[type="file"][id="pdf_format"][name="constitutive_act"]').addClass('d-none');

                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="balance_sheet"]').attr('required',false);
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="income_statements"]').attr('required',false)
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="power_of_attorney"]').attr('required',false)
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="constitutive_act"]').attr('required',false);
                }
                if (parseInt('450000') <= parseInt(creditLimit.replace(/,/g, '')) && parseInt(creditLimit.replace(/,/g, '')) <= parseInt('9999999')){

                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="power_of_attorney"]').addClass('d-none');
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="constitutive_act"]').addClass('d-none');
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="balance_sheet"]').removeClass('d-none');
                      $('.power_of_attorney').hide()
                      $('.constitutive_act').hide()
                     $('.balance_sheet').show()
                     $('.income_statements').show()
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="income_statements"]').removeClass('d-none');

                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="balance_sheet"]').attr('required',true);
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="income_statements"]').attr('required',true)
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="power_of_attorney"]').attr('required',false)
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="constitutive_act"]').attr('required',false);
                }
            }
           if ($('.current_login').val() ==  'legal'){
           if(parseInt(creditLimit.replace(/,/g, '')) < parseInt('450000')){
                    $('.balance_sheet').hide()
                    $('.income_statements').hide()
//                     $('.power_of_attorney').hide()
//                    $('.constitutive_act').hide()
                    $('.power_of_attorney').show()
                    $('.constitutive_act').show()
                    $('.check_box_class').find('input[type="file"][id="pdf_format"][name="balance_sheet"]').addClass('d-none');
                    $('.check_box_class').find('input[type="file"][id="pdf_format"][name="income_statements"]').addClass('d-none');
                    $('.check_box_class').find('input[type="file"][id="pdf_format"][name="power_of_attorney"]').removeClass('d-none');
                    $('.check_box_class').find('input[type="file"][id="pdf_format"][name="constitutive_act"]').removeClass('d-none');

                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="balance_sheet"]').attr('required',false);
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="income_statements"]').attr('required',false)
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="power_of_attorney"]').attr('required',true)
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="constitutive_act"]').attr('required',true);
                }
                if (parseInt('450000') <= parseInt(creditLimit.replace(/,/g, '')) && parseInt(creditLimit.replace(/,/g, '')) <= parseInt('9999999')){
                     $('.power_of_attorney').show()
                     $('.constitutive_act').show()
                     $('.balance_sheet').show()
                     $('.income_statements').show()
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="power_of_attorney"]').removeClass('d-none');
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="constitutive_act"]').removeClass('d-none');
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="balance_sheet"]').removeClass('d-none');
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="income_statements"]').removeClass('d-none');

                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="balance_sheet"]').attr('required',true);
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="income_statements"]').attr('required',true)
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="power_of_attorney"]').attr('required',true);
                     $('.check_box_class').find('input[type="file"][id="pdf_format"][name="constitutive_act"]').attr('required',true)
                }
           }
        },
        onClickSubmit: function(ev){
            let cash_dealer_form = document.getElementById("cash_dealers_information_form");
            let cash_dealer = document.getElementById("cash_dealer");
            if ($(cash_dealer_form.elements).filter(':checked').length < 1 && cash_dealer.checked){
                alert("Please Upload at least one Document")
                ev.preventDefault();
            }
            cash_dealer_form.addEventListener("submit", (ev) => {

               let submitted_data = $(cash_dealer_form.elements).filter('input[type="file"]')
               for (let dict of submitted_data) {
                    if(dict.value === ''){
                        dict.remove()
                    }
                }
                console.log(submitted_data)
            });


            let credit_dealer_form = document.getElementById("credit_dealers_information_form");
            let credit_dealer = document.getElementById("credit_dealer");
            if ($(credit_dealer_form.elements).filter(':checked').length < 1 && credit_dealer.checked){
                alert("Please Upload at least one Document")
                ev.preventDefault();
            }
            credit_dealer_form.addEventListener("submit", (ev) => {
               let submitted_data = $(credit_dealer_form.elements).filter('input[type="file"]')
               for (let dict of submitted_data) {
                    if(dict.value === ''){
                        dict.remove()
                    }
                }
            });
        },
        onChangeCashDealerFileJpgPdfFormat: function(ev){

          cash_myfile1 = ev.currentTarget;
          var ext = cash_myfile1.value.split('.').pop();
          if(cash_myfile1.value.length > 1 && ext!="pdf" && ext!="jpeg" && ext!="jpg" && ext!="png"){
                cash_myfile1.value = '';
               alert("Please Upload PDF or jpg/jpeg/png documents");
           }
        },
        onChangeCashDealerFileJpgFormat: function(ev){

          cash_myfile2 = ev.currentTarget;
          var ext = cash_myfile2.value.split('.').pop();
          if(cash_myfile2.value.length > 1 && ext!="pdf" && ext!="jpeg" && ext!="jpg" && ext!="png"){
                cash_myfile2.value = '';
               alert("Please Upload PDF or jpg/jpeg/png documents");
           }
        },
        onChangeCreditDealerFileJpgPdfFormat: function(ev){
          myfile1 = ev.currentTarget;
          var ext = myfile1.value.split('.').pop();
          if(myfile1.value.length > 1 && ext!="pdf" && ext!="jpeg" && ext!="jpg" && ext!="png"){
                myfile1.value = '';
               alert("Please Upload PDF or jpg/jpeg/png documents");
           }
        },
        onChangeCreditDealerFileJpgFormat: function(ev){
          myfile2= ev.currentTarget;
          var ext = myfile2.value.split('.').pop();
           if (myfile2.value.length > 1 && ext!="jpeg" && ext!="jpg" && ext!="png"){
               myfile2.value = '';
               alert("Please Upload jpg/jpeg/png document");

           }
        },
        onChangeCreditDealerFilePdfFormat: function(ev){
          myfile3= ev.currentTarget;
          var ext = myfile3.value.split('.').pop();
           if (myfile3.value.length > 1 && ext!="pdf"){
               myfile3.value = '';
               alert("Please Upload PDF Document");
           }
        }
    });

