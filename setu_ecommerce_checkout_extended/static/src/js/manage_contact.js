/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import publicWidget from '@web/legacy/js/public/public_widget';

publicWidget.registry.manage_contact = publicWidget.Widget.extend({
        selector: '.manage_contacts',
        events: {
            'click .delete_person': 'onClickDeletePerson',
            'submit #validate_contact': 'onSubmitContact',
            'submit .add_contact_form': 'onSubmitForm',
        },
        start: function () {
            var self = this;
            if(document.getElementById("person_email") != null){
                if(document.getElementById("person_email").getAttribute("readonly") != 'readonly'){
                    document.getElementById("person_email").removeAttribute("readonly")
                }
            }
            return this._super.apply(this, arguments);
        },
        custom_toast: function(title,type){
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
        onClickDeletePerson: function(ev){
        debugger
            var self = this
            var partner_id = $(ev.currentTarget).attr('value')
            $.ajax({
                type: 'get',
                url: '/my/manage-address/delete_person',
                data: {'partner_id':partner_id},
                success: function (data_obj) {
                    self.custom_toast('Deleted Successful','success')
                    location.reload()
                },
                error: function (data_obj) {
                    self.custom_toast(data_obj.statusText,'error')
                },
          })
        },
        onSubmitContact: function(ev) {
            debugger;
            var self = this;
            var $form = $(ev.currentTarget);
            var action = $form.attr('action');
            var data = $form.serializeArray();
            var email = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/

            for (var i = 1; i < data.length; i++) {
                 if (data[i]['name'] === 'name') {
                    if (data[i]['value'] === '') {
                        self.custom_toast("Please Fill Out Name", 'error');
                        return false;
                    }
                }
                if (data[i]['name'] === 'email') {
                    if (data[i]['value'] === '') {
                        self.custom_toast("Please Fill Out Email", 'error');
                        return false;
                    }
                    if (!data[i]['value'].match(email)) {
                        self.custom_toast("Please Fill Proper Email", 'error');
                        return false;
                    }
                }
            }
            var $buttons = $(ev.currentTarget).find('button[type="submit"], a.a-submit');
            $buttons.each(function(index, btn) {
//            _.each($buttons, function (btn) {
                var $btn = $(btn);
                $btn.html('<i class="fa fa-spinner fa-spin"></i> ' + $btn.text());
                $btn.prop('disabled', true);
            });

        },
        onSubmitForm: function(ev) {
        debugger
        const $form = $(ev.currentTarget);
        if (!$form.attr('id')) {
            const $buttons = $form.find('button[type="submit"], a.a-submit');
            $buttons.each(function(index, btn) {
                const $btn = $(btn);
                $btn.html('<i class="fa fa-spinner fa-spin"></i> ' + $btn.text());
                $btn.prop('disabled', true);
            });
        }
    }

    });
//});
