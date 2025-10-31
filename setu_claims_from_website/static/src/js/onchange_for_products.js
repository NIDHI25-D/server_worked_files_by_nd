/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";


console.log($('.js_invoice_box'))
$('.js_invoice_box').click(function(ev){
    console.log("demo")
    var invoice_id = $(this).val()
    // For Auto update the products of the selected invoice.
    debugger
    rpc('/web/dataset/call_kw/account.move/search_invoice_product_readonly', {
                    model: 'account.move',
                    method: 'search_invoice_product',
                    args: [[]],
                    kwargs: {'invoice_id':invoice_id,},
                }).then(function (result) {
               $(".js_model_opt").remove()
               $.each(result, function(key, value){
                    $('.js_models').append($('<option>').addClass('js_model_opt').val(key).text(value));
                })
        });

    // For Auto update the Service agent as per invoice.
    rpc('/web/dataset/call_kw/account.move/search_sale_team_readonly', {
                    model: 'account.move',
                    method: 'search_sale_team',
                    args: [[]],
                    kwargs: {'invoice_id':invoice_id,},
                }).then(function (result) {
               $('.js_service_box').val(result.name)
               $('.js_service_box_id').val(result.sale_team)
        });
    })

    //For Required invoice checkbox or ! in Address page
    $('.js_invoice_box').trigger('click')

    //  For Document Upload in claims
    $("div[id='file_image']").hide()
    $("div[id='file_video']").hide()
    $("div[id='file_text']").hide()
    $("input[name='image_upload']").click(function(ev){
        debugger
        if($(this).prop("checked")){ $("div[id='file_image']").show() }
        else{ $("div[id='file_image']").hide() }
    });

    $("input[name='video']").click(function(ev){
        debugger
        if($(this).prop("checked")){ $("div[id='file_video']").show() }
        else{ $("div[id='file_video']").hide() }
    });

    $("input[name='text']").click(function(ev){
        debugger
        if($(this).prop("checked")){ $("div[id='file_text']").show() }
        else{$("div[id='file_text']").hide()}
    });

    $(".js_claims_form").submit(function(){
        debugger
        if (! $("[name='image_upload']").prop("checked") && ! $("[name='video']").prop("checked") && ! $("[name='text']").prop("checked"))
        { //show error
            alert("Please Select atleast one attachment option and upload file.")
            return false
        }
        if ($("[name='image_upload']").prop("checked") && (! $("[name='add_evidence_image']").val() || ! $("[name='add_evidence_image_1']").val() || ! $("[name='add_evidence_image_2']").val()))
        { //show error
            alert("Please upload appropriate file(s).")
            return false
        }
        if ($("[name='video']").prop("checked") && ! $("[name='add_evidence_video']").val())
        { //show error
            alert("Please upload appropriate file(s).")
            return false
        }
        if ($("[name='text']").prop("checked") && ! $("[name='add_evidence_text']").val())
        { //show error
            alert("Please upload appropriate file(s).")
            return false
        }
    })
