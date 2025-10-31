/** @odoo-module **/

import {registry} from "@web/core/registry";
import {_t} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";
import { ensureJQuery } from "@web/core/ensure_jquery";
import { loadJS } from "@web/core/assets";
import {Component, useState, onWillStart} from "@odoo/owl";

export class cusattachXmlsWizard extends Component {

    static template = "l10n_mx_edi_vendor_bills.attach_xmls_template";
    setup() {
        super.setup();
        this.files = {};
        this.uploading_files = false;
        this.invoice_ids = [];
        this.action = useService("action");


        var handler = $(this)//.$el.find("#dragandrophandler");
        // events drag and drop inside the page
        $(document).on('dragenter', function (e) {
            e.stopPropagation();
            e.preventDefault();
            handler.removeClass('dnd_inside dnd_normal').addClass('dnd_out');
        });
        $(document).on('dragover', function (e) {
            // allows to execute the drop event
            e.stopPropagation();
            e.preventDefault();
        });
        $(document).on('drop', function (e) {
            e.stopPropagation();
            e.preventDefault();
            handler.removeClass('dnd_out dnd_inside').addClass('dnd_normal');
        });
        $(document).on('dragleave', function (e) {
            e.stopPropagation();
            e.preventDefault();
            if (!e.originalEvent.clientX && !e.originalEvent.clientY) {
                handler.removeClass('dnd_out dnd_inside').addClass('dnd_normal');
            }
        });
    }

    _onDragEnter(e) {
        console.log(e)
    }

    _onSave(e) {
        e.preventDefault();
        $('.alert-warning.dnd-alert').remove();
        if (Object.keys(this.files).length <= 0) {
        this.env.model.notification.add(_t("There is no files selected"), {type: "warning",});
//            this.env.model.notification.add(
//                this.env._t("There is no files selected"),
//                {
//                    type: "warning",
//                },
//            );
        } else if (Object.keys(this.files).length > 1 && this.env.model.root.context.active_ids) {
            this.env.model.notification.add(_t("You cannot attach more than one xml to an invoice"), {type: "warning",});
//            this.env.model.notification.add(
//                this.env._t("You cannot attach more than one xml to an invoice"),
//                {
//                    type: "warning",
//                },
//            );
        } else {
            $("#dragandrophandler").hide();
            $('#dndfooter button#save').attr('disabled', true);
            $("#filescontent").find('.xml_cont').removeClass('xml_cont_hover');
            this.readFiles(this.files);
        }
    }

    readFiles(files) {
        /* Convert the file object uploaded to a base64 string */
        var self = this;
        var readfiles = {};
        $.each(files, function (key, file) {
            var fr = new FileReader();
            fr.onload = function () {
                readfiles[key] = fr.result;
                if (Object.keys(files).length === Object.keys(readfiles).length) {
                    self.sendFileToServer(readfiles);
                }
            };
            fr.readAsDataURL(file);
        });
    }

    _onCancel(e) {
        e.preventDefault();
        this.action.doAction({'type': 'ir.actions.act_window_close'});
    }

    handleCancel(cancelDocs) {
        var self = this;
        var data = '<ul>';
        $.each(cancelDocs, function (key, val) {
            data += "<li>" + Object.keys(val) + "</li><ul><li>" + Object.values(val) + "</li></ul>";
            $('#filescontent').html(data)
        });
        data = '</ul>';
    }

    handleFileUpload(files) {
        /* Creates the file element in the DOM and shows alerts wheter the extension
        file is not the correct one or the file is already uploaded */
        var self = this;
        if (self.uploading_files) {
        this.env.model.notification.add(_t("There are files uploading"), {type: "warning",});
//            this.env.model.notification.add(
//                this.env._t("There are files uploading"),
//                {
//                    type: "warning",
//                },
//            );
        } else {
            self.uploading_files = true;
            var files_used = [];
            var wrong_files = [];
            $.each(files, function (i, file) {
                if (file.type !== 'text/xml') {
                    wrong_files.push(file.name);
                } else if (Object.prototype.hasOwnProperty.call(self.files, file.name)) {
                    files_used.push(file.name);
                } else {
                    self.files[file.name] = file;
                    var newelement = $('<div class="xml_cont xml_cont_hover" title="' + file.name + '">' +
                        '<img class="xml_img" height="100%" align="left" hspace="5"/>' +
                        '<p>' + file.name + '</p><div class="remove_xml">&times;</div>' +
                        '</div>').css('opacity', '0');
                    $("#filescontent").append(newelement);
                    newelement.animate({'opacity': '1'}, 500);
                }
            });
            var alert_message = '';
            if (wrong_files.length > 0) {
                alert_message += _t('<strong>Info!</strong> You only can upload XML files.<br>') +
                    wrong_files.join(" <b style='font-size:15px;font-wight:900;'>&#8226;</b> ");
            }
            if (files_used.length > 0) {
                if (alert_message !== '') {
                    alert_message += '<br>';
                }
                alert_message += _t('<strong>Info!</strong> Some files are already loaded.<br>') +
                    files_used.join(" <b style='font-size:15px;font-wight:900;'>&#8226;</b> ");
            }
            if (alert_message !== '') {
                $("#alertscontent").html('<div class="alert alert-warning dnd-alert">' +
                    '<a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>' + alert_message +
                    '</div>');
            }
            self.uploading_files = false;
        }
    }

    getFields() {
        var self = this;
        var fields = {};
        $.each(this.env.model.root.data, function (field, value) {
            if (!value || field === 'omit_cfdi_related') {
                fields[field] = value;
            } else if (value.data.constructor === Array) {
                var valueList = [];
                $.each(value.data, function (index, val) {
                    valueList.push(val.data.id);
                });
                fields[field] = valueList;
            } else {
                fields[field] = value.data.id;
            }
        });
        return fields;
    }

    sendFileToServer(files) {
        /* Sends each base64 file string to the back-end server to create the invoices */
        var self = this;
        var options = this.env.model.root.data;
        var ctx = this.env.model.root.context;
        ctx.account_id = options.account_id && options.account_id[0];
        ctx.custom_journal_id = options.journal_id && options.journal_id[0];
        ctx.omit_cfdi_related = options.omit_cfdi_related;
        ctx.partner_id = options.partner_id && options.partner_id[0];
        ctx.account_analytic_id = options.account_analytic_id && options.account_analytic_id[0];
        this.env.model.orm.call(
            'attach.xmls.wizard',
            'check_xml',
            [files],
            {context: ctx}
        ).then(function (result) {
            var wrongfiles = result.wrongfiles;
            var invoices = result.invoices;
            var cancelDocs = result.cancelDocs;
            $.each(invoices, function (key, data) {
                self.invoice_ids.push(data.invoice_id);
                self.createdCorrectly(key);
            });
            if (cancelDocs && Object.keys(cancelDocs).length > 0) {
                self.handleCancel(cancelDocs);
            }
            if (Object.keys(wrongfiles).length > 0) {
                self.handleFileWrong(wrongfiles);
            }
            if (!cancelDocs && (Object.keys(wrongfiles).length === 0 || self.alerts_in_queue.total === 0)) {
                self.correctFinalRegistry();
            }
        });
    }

    correctFinalRegistry() {
        /* Shows the final success alert and the button to see the invoices created */
        var self = this;
        var alert = $('<div class="alert alert-success dnd-alert"><strong>' + _t('Congratulations') + '!</strong> ' +
            _t('Your invoices were created correctly') + '.</div>').hide();
        $("#alertscontent").html(alert);
        alert.slideDown(500, function () {
            $('#dndfooter button#show').show();
        });
    }

    handleFileWrong(wrongfiles) {
        /* Saves the exceptions occurred in the invoices creation */
        this.alerts_in_queue = {'alertHTML': {}, total: Object.keys(wrongfiles).length};
        var self = this;
        $.each(wrongfiles, function (key, file) {
            if ('cfdi_type' in file) {
                if (Object.keys(self.files).length === 0) {
                    self.restart();
                }
                self.alerts_in_queue.total -= 1;
                $('#filescontent div[title="' + key + '"]').remove();
                this.env.model.notification.add(
                    _t('XML removed, the TipoDeComprobante is not I or E.'),
                    {
                        type: "warning",
                    },
                );
            } else {
                var alert_parts = self.prepareWrongAlert(key, file);

                var alertelement = $('<div tag="' + key + '" class="alert alert-' + alert_parts.alerttype + ' dnd-alert">' +
                    alert_parts.errors + '<div>' + alert_parts.buttons + _t('<span>Wrong File: <span class="index-alert"></span>') + '/' + self.alerts_in_queue.total +
                    '<b style="font-size:15px;font-wight:900;">&#8226;</b> ' + key + '</span></div></div>');
                self.alerts_in_queue.alertHTML[key] = {'alert': alertelement, 'xml64': file.xml64};
            }
            if (self.alerts_in_queue.total > 0 && self.alerts_in_queue.total === Object.keys(self.alerts_in_queue.alertHTML).length) {
                self.nextWrongAlert();
            }
        });
    }

    nextWrongAlert() {
        /* Shows the next error alert */
        var self = this;
        var keys = Object.keys(self.alerts_in_queue.alertHTML);
        var alert = self.alerts_in_queue.alertHTML[keys[0]].alert.hide();
        alert.find('div:last-child .index-alert').html(self.alerts_in_queue.total - (keys.length - 1));
        $("#alertscontent").html(alert);
        $("button[tag='remove']").on('click', self._handleButtonTagEvent.bind(self))
        $("button[tag='supplier']").on('click', self._handleButtonTagEvent.bind(self))
        $("button[tag='tryagain']").on('click', self._handleButtonTagEvent.bind(self))
        $("button[tag='forcesave']").on('click', self._handleButtonTagEvent.bind(self))
        alert.slideDown(500);
    }

    prepareWrongAlert(key, data) {
        /* Prepares the buttons and message the invoice alert exception will contain */
        var self = this;
        var errors = '';
        var buttons = '';
        var able_buttons = [];
        var alerttype = '';
        if ('error' in data) {
            errors += self.wrongMsgServer(data, able_buttons);
            alerttype = 'danger';
        } else {
            errors += self.wrongMsgXml(data, able_buttons);
            alerttype = 'info';
        }
        if (able_buttons.includes('remove')) {
            $("button[tag='remove']").css('visibility', 'visible')
            buttons += $("button[tag='remove']")[0].outerHTML
        } else if (able_buttons.includes('supplier') && !able_buttons.includes('remove')) {
            $("button[tag='supplier']").css('visibility', 'visible')
            buttons += $("button[tag='supplier']")[0].outerHTML
        } else if (able_buttons.includes('tryagain')) {
            $("button[tag='remove']").css('visibility', 'visible')
            buttons += $("button[tag='remove']")[0].outerHTML
            $("button[tag='tryagain']").css('visibility', 'visible')
            buttons += $("button[tag='tryagain']")[0].outerHTML
        } else if (able_buttons.includes('invoice_not_found')) {
            $("button[tag='remove']").css('visibility', 'visible')
            buttons += $("button[tag='remove']")[0].outerHTML
            $("button[tag='forcesave']").css('visibility', 'visible')
            buttons += $("button[tag='forcesave']")[0].outerHTML
        }
        return {'errors': errors, 'buttons': buttons, 'alerttype': alerttype};
    }

    wrongMsgServer(data, able_buttons) {
        /* Prepares the message to the server error */
        var typemsg = {
            'CheckXML': _t('Error checking XML data.'),
            'CreatePartner': _t('Error creating supplier.'),
            'CreateInvoice': _t('Error creating invoice.')
        };
        var errors = '<div><span level="2">' + data.error[0] + '</span> <span level="1">' + data.error[1] + '</span>.<br>' + typemsg[data.where] + '</div>';
        able_buttons.push('tryagain');
        return errors;
    }

    wrongMsgXml(file, able_buttons) {
        /* Prepares the message to the xml errors */
        var self = this;
        var errors = '';
        var map_error = {
            signed: _t('<div><span level="1">UUID</span> not found in the XML.</div>'),
            notinstalled: _t('<div><span level="1">Receiver does not have fiscal regime and external trade type</span></div>'),
            tradenotmatch:_t('<div><span level="1">Receiver trade type does not match with the document</span></div>'),
            regimenotmatch: _t('<div><span level="1">Receiver fiscal regim  does not match with the document</span></div>'),
            version: _t('<div><span level="1">Unable to generate invoices from an XML with version 3.2.</span>You can create the invoice manually and then attach the xml.</div>'),
            cancel: _t('<div><span level="1">The XML state</span> is CANCELED in the SAT system.</div>'),
            nothing: _t('<div><strong>Info!</strong> XML data could not be read correctly.</div>'),
            no_xml_related_uuid: _t('<div><span level="1">The DocumentType is "E" and The XML UUID / and the node CfdiRelacionados</span> were not found in the XML.</div>'),
        };
        $.each(file, function (ikey, val) {
            if (ikey !== 'supplier' && ikey !== 'xml64' && ikey !== 'invoice_not_found' && !able_buttons.includes('remove')) {
                able_buttons.push('remove');
            }
            if (ikey === 'supplier') {
                errors += _t('<div><span level="1">The XML Supplier</span> was not found: <span level="2">') + val + '</span>.</div>';
                able_buttons.push('supplier');
            } else if (ikey === 'rfc') {
                errors += _t('<div><span level="1">The XML Receptor RFC</span> does not match with <span level="1">your Company RFC</span>: ') +
                    _t('XML Receptor RFC: <span level="2">') + val[0] +_t(', </span> Your Company RFC: <span level="2">') + val[1] + '</span></div>';
            } else if (ikey === 'currency') {
                errors += _t('<div><span level="1">The XML Currency</span> <span level="2">') + val + _t('</span> was not found or is disabled.</div>');
            } else if (ikey === 'taxes') {
                errors += _t('<div><span level="1">Some taxes</span> do not exist: <span level="2">') + val.join(', ') + '</span>.</div>';
            } else if (ikey === 'taxes_wn_accounts') {
                errors += _t('<div><span level="1">Some taxes</span> do not have account asigned: <span level="2">') + val.join(', ') + '</span>.</div>';
            } else if (ikey === 'folio') {
                errors += _t('<div><span level="1">The XML Folio</span> does not match with <span level="1">Supplier Invoice Number</span>: ') +
                    _t('XML Folio: <span level="2">') + val[0] + _t(', </span> Supplier invoice number: <span level="2">') + val[1] + '</span></div>';
            } else if (ikey === 'rfc_supplier') {
                errors += _t('<div><span level="1">The XML Emitter RFC</span> does not match with <span level="1">Customer RFC</span>: ') +
                    _t('XML Emitter RFC: <span level="2">') + val[0] + _t(', </span> Customer RFC: <span level="2">') + val[1] + '</span></div>';
            } else if (ikey === 'amount') {
                errors += _t('<div><span level="1">The XML amount total</span> does not match with <span level="1">Invoice total</span>: ') +
                    _t('XML amount total: <span level="2">') + val[0] + _t(', </span> Invoice Total: <span level="2">') + val[1] + '</span></div>';
            } else if (ikey === 'uuid_duplicate') {
                errors += _t('<div><span level="1">The XML UUID</span> belong to other invoice. <span level="1">UUID: </span>') + val + '</div>';
            } else if (ikey === 'reference') {
                errors += _t('<div><span level="1">The invoice reference</span> belong to other invoice of same partner. <span level="1">Partner: </span>') + val[0] + _t('<span level="1"> Reference: </span>') + val[1] + '</div>';
            } else if (ikey === 'invoice_not_found') {
                errors += _t('<div><span level="1">The DocumentType is "E" and The XML UUID</span> is not related to any invoice. <span level="1">UUID: </span>') + val + '</div>';
                $.when(self.getSession().user_has_group('l10n_mx_edi_vendor_bills.allow_force_invoice_generation')).then(function (has_group) {
                    if (has_group) {
                        able_buttons.push('invoice_not_found');
                    } else {
                        able_buttons.push('remove');
                    }
                });
            } else if (Object.prototype.hasOwnProperty.call(map_error, ikey)) {
                errors += map_error[ikey];
            }
        });
        return errors;
    }

    _handleButtonTagEvent(e) {
        var type = e.currentTarget.attributes.tag.value;
        var alertnode = e.currentTarget.parentElement.parentElement;
        var filekey = alertnode.attributes.tag.value;
        var self = this;
        if (type === 'remove') {
            this.removeWrongAlerts($(alertnode), filekey, true);
        } else if (type === 'supplier') {
            console.log('entro aca')
            this.env.model.orm.call(
                'attach.xmls.wizard',
                'create_partner',
                [self.alerts_in_queue.alertHTML[filekey].xml64, filekey],
                {context: self.env.model.root.context}
            ).then(function () {
                self.sendErrorToServer(self.alerts_in_queue.alertHTML[filekey].xml64, filekey, 'check_xml');
            });
        } else if (type === 'tryagain') {
            this.sendErrorToServer(this.alerts_in_queue.alertHTML[filekey].xml64, filekey, 'check_xml');
        } else if (type === 'forcesave') {
            self.env.model.root.context = _.extend(self.env.model.root.context, {'force_save': true});
            self.sendErrorToServer(self.alerts_in_queue.alertHTML[filekey].xml64, filekey, 'check_xml');
        }
    }

    sendErrorToServer(xml64, key, function_def) {
        //     /* Sends again the base64 file string to the server to tries to create the invoice, or sends the partner data to create him if does not exist */
        var self = this;
        var xml_file = {};
        xml_file[key] = xml64;
        var options = this.env.model.root.data;
        var ctx = this.env.model.root.context;
        ctx.account_id = options.account_id && options.account_id[0];
        this.env.model.orm.call(
            'attach.xmls.wizard',
            function_def,
            [xml_file],
            {context: ctx}
        ).then(function (data) {
            var wrongfiles = data.wrongfiles;
            var invoices = data.invoices;
            $.each(invoices, function (rkey, result) {
                var alertobj = $('#alertscontent div[tag="' + rkey + '"].alert.dnd-alert');
                self.invoice_ids.push(result.invoice_id);
                self.createdCorrectly(rkey);
                self.removeWrongAlerts(alertobj, rkey, false);
            });
            $.each(wrongfiles, function (rkey, result) {
                var alert_parts = self.prepareWrongAlert(rkey, result);
                var alertobj = $('#alertscontent div[tag="' + rkey + '"].alert.dnd-alert');
                var footer = alertobj.find('div:last-child span:not(.index-alert)');
                alertobj.removeClass('alert-danger alert-info').addClass('alert-' + alert_parts.alerttype);
                alertobj.html(alert_parts.errors + '<div>' + alert_parts.buttons + '</div>');
                alertobj.find('div:last-child').append(footer);
                $("button[tag='remove']").on('click', self._handleButtonTagEvent.bind(self))
                $("button[tag='supplier']").on('click', self._handleButtonTagEvent.bind(self))
                $("button[tag='tryagain']").on('click', self._handleButtonTagEvent.bind(self))
                $("button[tag='forcesave']").on('click', self._handleButtonTagEvent.bind(self))
            });
        });
    }

    createdCorrectly(key) {
        /* Colors the files content in the DOM when the invoice is created with that XML */
        var self = this;
        var alert = $('#filescontent div[title="' + key + '"]');
        alert.addClass('xml_correct');
        alert.find('div.remove_xml').html('&#10004;');
    }

    removeWrongAlerts(alertobj, filekey, removefile) {
        /* Removes the current error alert to continue with the others */
        var self = this;
        alertobj.slideUp(500, function () {
            delete self.alerts_in_queue.alertHTML[filekey];
            if (removefile) {
                delete self.files[filekey];
                $('#filescontent div[title="' + filekey + '"]').animate({'opacity': '0'}, 500, function () {
                    $.when($(this).remove()).done(function () {
                        self.continueAlert(alertobj);
                    });
                });
            } else {
                self.continueAlert(alertobj);
            }
        });
    }

    continueAlert(alertobj) {
        /* After the error alert is removed, execute the next actions
        (Next error alert, Restarts to attach more files, or Shows the final success alert) */
        var self = this;

        if (Object.keys(self.alerts_in_queue.alertHTML).length > 0) {
            self.nextWrongAlert();
        } else if (Object.keys(self.files).length === 0) {
            self.restart();
        } else {
            self.correctFinalRegistry();
        }

    }

    restart() {
        /* Restarts all the variables and restores all the DOM element to attach more new files */
        this.files = {};
        this.invoice_ids = [];
        this.uploading_files = false;
        this.alerts_in_queue = {};
        $("#dragandrophandler").show();
        $("#filescontent").html('');
        $("#files").val('');
        $('#dndfooter button#save').attr('disabled', false);
        $("button[tag='remove']").css('visibility', 'hidden')
        $("button[tag='supplier']").css('visibility', 'hidden')
        $("button[tag='tryagain']").css('visibility', 'hidden')
        $("button[tag='forcesave']").css('visibility', 'hidden')
        $('#dndfooter button#show').hide();
    }

    _onDragClick(e) {
        $(this).find("#files").val("");
        $(this).find("#files").click();
    }

    _onDragDrop(e) {
        console.log(e)
        this.handleFileUpload(e.dataTransfer.files);
    }

    _onFilesChange(e) {
        console.log("files Change")
    }

    _onShowInvoice() {
    debugger
        if (this.invoice_ids.length > 0) {
            var domain = [['id', 'in', this.invoice_ids]];
            const ctx = {...this.env.model.root.context,
                            default_move_type: 'in_invoice'};
            return this.action.doAction({
                name: _t('Supplier Invoices'),
                view_type: 'list',
                view_mode: 'list,form',
                res_model: 'account.move',
                type: 'ir.actions.act_window',
                views: [[false, 'list'], [false, 'form']],
                targe: 'current',
                domain: domain,
                context: ctx,
            });
        }
    }
};

export const attachXmlsWizard = {
    component: cusattachXmlsWizard,
    displayName: _t("Attach Multiple Supplier Xml's"),
    supportedTypes: ["char"],
};

registry.category("fields").add('attach_xmls_wizard_widget', attachXmlsWizard);
