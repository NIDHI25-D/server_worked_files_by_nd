# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import re
from markupsafe import Markup


def get_last_value(self, record_id, model=None, field=None, fieldtype=None):
    """
    Author: siddharth.vasani@setuconsulting.com
    Date: 14/02/2025
    Task: Log Note (Migration)
    Purpose: This method will used to get last value of the field
    :param self:
    :param record_id:
    :param model:
    :param field:
    :param fieldtype:
    :return: field and value
    """
    field = record_id and field or []
    model_obj = self.env[model]
    browse_record_id = model_obj.browse(record_id)
    if 'many2one' in fieldtype:
        value = field and browse_record_id[field] and browse_record_id[field].display_name or ''
        # value = value and value[0][1]
    elif 'many2many' in fieldtype:
        value = field and [rec_order_id.id for rec_order_id in browse_record_id[field]]
    else:
        value = field and browse_record_id[field] or ''
    return field and value or ''


def prepare_many_info(self, record_ids, string, env_model_obj, last=None):
    """
    Author: siddharth.vasani@setuconsulting.com
    Date: 14/02/2025
    Task: Log Note (Migration)
    Purpose: This method will prepare log not when create new line, update line, remove line, remove and add
    :param self:
    :param record_ids:
    :param string:
    :param env_model_obj:
    :param last:
    :return: message
    """
    info = {0: _('Created New Line'),
            1: _('Updated Line'),
            2: _('Removed Line'),
            3: _('Removed'),
            4: _('Added'),
            6: _('many2many')}

    message = '<ul>'
    model_obj = self.env[env_model_obj]
    r_name = model_obj._rec_name
    mes = ''
    last = last or []
    new_list = []
    for record_id in record_ids:
        if record_id and type(record_id) is not int and info.get(record_id[0], False):
            if record_id[0] == 0:
                value = record_id[2]
                message = '%s\n<li><b>%s<b>: %s</li>' % (get_encode_value(message),
                                                         get_encode_value(info.get(record_id[0])),
                                                         get_encode_value(value.get(r_name)))
            elif record_id[0] in (2, 3):
                model_brw = model_obj.browse(record_id[1])
                # last_value = model_brw.name_get()
                last_value = model_brw.display_name
                # last_value = last_value and last_value[0][1]
                message = '%s\n<li><b>%s<b>: %s</li>' % (get_encode_value(message),
                                                         get_encode_value(info.get(record_id[0])),
                                                         get_encode_value(last_value))
            elif record_id[0] == 4:
                model_brw = model_obj.browse(record_id[1])
                last_value = model_brw.display_name
                message = '%s\n<li><b>%s<b>: %s</li>' % (get_encode_value(message),
                                                         get_encode_value(info.get(record_id[0])),
                                                         get_encode_value(last_value))

            elif record_id[0] == 6:
                lastv = list(set(record_id[2]) - set(last))
                # lastv = list(set(record_id[2]) - set(last))
                new = list(set(last) - set(record_id[2]))
                add = _('Added')
                delete = _('Deleted')
                if lastv and not new:
                    # dele = [model_obj.browse(i).name_get()[0][1] for i in lastv]
                    dele = [model_obj.browse(i).display_name for i in lastv]
                    mes = ' - '.join(dele)
                    message = '%s\n<li><b>%s %s<b>: %s</li>' % (get_encode_value(message),
                                                                get_encode_value(add),
                                                                get_encode_value(string),
                                                                get_encode_value(mes))
                if not lastv and new:
                    # dele = [model_obj.browse(i).name_get()[0][1] for i in new]
                    dele = [model_obj.browse(i).display_name for i in new]
                    mes = '-'.join(dele)
                    message = '%s\n<li><b>%s %s<b>: %s</li>' % (get_encode_value(message),
                                                                get_encode_value(delete),
                                                                get_encode_value(string),
                                                                get_encode_value(mes))

            elif record_id[0] == 1:
                vals = record_id[2]
                id_line = 0
                for field in vals:
                    if model_obj._fields[field].type in ('one2many', 'many2many'):
                        is_many = model_obj._fields[field].type == 'many2many'
                        last_value = is_many and get_last_value(self, record_id[1], env_model_obj, field, 'many2many')
                        field_str = get_string_by_field(model_obj, field)
                        new_n_obj = model_obj._fields[field].comodel_name
                        mes = prepare_many_info(self, vals[field], field_str, new_n_obj, last_value)
                    elif model_obj._fields[field].type == 'many2one':
                        mes = prepare_many2one_info(self, record_id[1], env_model_obj, field, vals)
                    elif 'many' not in model_obj._fields[field].type:
                        mes = prepare_simple_info(self, record_id[1], env_model_obj, field, vals)
                    if mes and mes != '<p>':
                        line_message = _('%s\n<h3>Line %s</h3>' % (message, record_id[1]))
                        supinfo_mod = self.env['product.supplierinfo']
                        if model_obj._name  == 'product.supplierinfo' and field != 'product_tmpl_id':
                            if record_id[1] and message:
                                sup_info = supinfo_mod.search([('id','=',record_id[1])])
                                line_message = _('%s\n<h3>Line <b>%s</b></h3>' % (message, sup_info.product_tmpl_id.name))
                        message = id_line != record_id[1] and line_message or message
                        message = '%s\n%s' % (get_encode_value(message), mes)
                        # message = '%s' % (mes)
                        id_line = record_id[1]

        elif type(record_id) is int:
            new_list.append(record_id)
            if len(last) == len(new_list):
                message = '\n<li><b>%s<b>: %s</li>' % (
                    get_encode_value(string),
                    # get_encode_value(self.env[env_model_obj].browse(record_ids).name_get()[0][1]))
                    get_encode_value(self.env[env_model_obj].browse(record_ids).mapped('display_name')))

    message = '%s\n</ul>' % get_encode_value(message)
    return message


def get_selection_value(source_obj, field, value):
    """
    Author: siddharth.vasani@setuconsulting.com
    Date: 14/02/2025
    Task: Log Note (Migration)
    Purpose: This method will used to get selection value
    :param source_obj:
    :param field:
    :param value:
    :return: dict
    """
    val = source_obj.fields_get([field])
    val = val and val.get(field, {})
    val = val and val.get('selection', ()) or ()
    val = [i[1] for i in val if value in i]
    val = val and val[0] or ''
    return val


def get_string_by_field(source_obj, field):
    """
    Author: siddharth.vasani@setuconsulting.com
    Date: 14/02/2025
    Task: Log Note (Migration)
    Purpose: This method will prepare string by field
    :param source_obj:
    :param field:
    :return: str
    """
    description = source_obj.fields_get([field])
    description = description and description.get(field, {})
    description = description and description.get('string', '') or ''
    return description


def prepare_many2one_info(self, ids, n_obj, field, vals):
    """
    Author: siddharth.vasani@setuconsulting.com
    Date: 14/02/2025
    Task: Log Note (Migration)
    Purpose: This method will prepare many2one info for log note
    :param self:
    :param ids:
    :param n_obj:
    :param field:
    :param vals:
    :return: str
    """
    obj = self.env[n_obj]
    last_value = get_last_value(self, ids, obj._name, field, obj._fields[field].type)
    model_obj = self.env[obj._fields[field].comodel_name]
    model_brw = model_obj.browse(vals[field])
    if model_brw:
        new_value = model_brw[0].display_name
    else:
        new_value = model_brw.display_name
    # new_value = new_value and new_value[0][1]

    return f'<li><b>{get_string_by_field(obj, field)}<b>: {get_encode_value(last_value)} → {get_encode_value(new_value)}</li>' if last_value != new_value and any(
        (new_value, last_value)) else '<p>'


def get_encode_value(value):
    """
    Author: siddharth.vasani@setuconsulting.com
    Date: 14/02/2025
    Task: Log Note (Migration)
    Purpose: This method will get encode value
    :param value:
    :return:
    """
    return value


def prepare_simple_info(self, ids, n_obj, field, vals):
    """
    Author: siddharth.vasani@setuconsulting.com
    Date: 14/02/2025
    Task: Log Note (Migration)
    Purpose: This method will prepare simpler field info which change by user
    :param self:
    :param ids:
    :param n_obj:
    :param field:
    :param vals:
    :return:
    """
    obj = self.env[n_obj]
    last_value = get_last_value(self,
                                ids, obj._name, field,
                                obj._fields[field].type)

    last_value = obj._fields[field].type == 'selection' and \
                 get_selection_value(obj, field, last_value) or last_value
    new_value = obj._fields[field].type == 'selection' and \
                get_selection_value(obj, field, vals[field]) or vals[field]
    last_value = get_encode_value(last_value)
    new_value = get_encode_value(new_value)

    return ((last_value != new_value) and any((last_value, vals[
        field]))) and f'<li><b>{get_string_by_field(obj, field)}<b>: {last_value} → {new_value}</li>' or '<p>'


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def write(self, vals):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 14/02/2025
        Task: Log Note (Migration)
        Purpose: This method will prepare log note and message post in chatter to the current model record,
                 which changed by user.
        :param vals:
        :return: True
        """
        model = self.env['ir.model'].search([('model', '=', str(self._name))])
        if model.is_tracked_module_field:
            if model:
                for idx in self:
                    body = '<ul>'
                    message = ''
                    for field in vals:
                        if self._fields[field].type in ('one2many', 'many2many'):
                            is_many = self._fields[field].type == 'many2many'
                            last_value = is_many and get_last_value(self, idx.id, self._name, field, 'many2many')
                            field_str = get_string_by_field(self, field)
                            n_obj = self._fields[field].comodel_name
                            message = prepare_many_info(self, vals[field], field_str, n_obj, last_value)
                            body = len(message.split('\n')) > 2 and '%s\n%s: %s' % (body, field_str, message) or body
                        elif self._fields[field].type == 'many2one':
                            message = prepare_many2one_info(self, idx.id, self._name, field, vals)
                            body = '%s\n%s' % (body, message)

                        elif 'many' not in self._fields[field].type:
                            message = prepare_simple_info(self, idx.id, self._name, field, vals)
                            body = '%s\n%s' % (body, message)
                    body = body and '%s\n</ul>' % body
                    clean = re.compile('<.*?>')
                    cleantext = re.sub(clean, '', body)
                    body_text = cleantext.strip('\n')
                    if body_text and body_text != '<ul>\n</ul>' and message and hasattr(idx, 'message_post'):
                        idx = idx if isinstance(idx.id, int) else idx._origin
                        if idx:
                            # idx.message_post(body=body_text.replace('\n', '<br/>'))
                            body_mark = body_text.replace('\n', '<br/>')
                            idx.message_post(body=Markup(body_mark))

        return super(MailThread, self).write(vals)
