# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'

    def activity_schedule(self, act_type_xmlid='', date_deadline=None, summary='', note='', **act_values):
        """
            Authour: nidhi@setconsulting
            Date: 19/05/25
            Task: Migration from V16 to V18
            Purpose: This method is used to send activities to multiple contacts which are selected in server.actions
            Procedure : In this method need to create a ir.server.action with the configuration of
                            Action to Do(state) = Create Next Activity,
                            Activity User Type : Several Users,
                            Select Multiple resposible in activity tab
                      Create an automated action: select any model, assign trigger and multiple responsible
                      Now when in model according to the trigger, multiple users(mentioned in multiple responsible) will be send the activity
        """
        automated_act = self._context.get('__action_done')
        if automated_act:
            act = list(self._context.get('__action_done').keys())[0]
            for action in act.action_server_ids:
                if action.activity_sevral_users_ids and action.activity_user_type == 'sevrals_users':
                    for user in action.activity_sevral_users_ids:
                        act_values.update({'user_id': user.id})
                        x = super(MailActivityMixin, self).activity_schedule(act_type_xmlid=act_type_xmlid,
                                                                             date_deadline=date_deadline,
                                                                             summary=summary,
                                                                             note=note, **act_values)
                else:
                    return super(MailActivityMixin, self).activity_schedule(act_type_xmlid=act_type_xmlid,
                                                                            date_deadline=date_deadline, summary=summary,
                                                                            note=note, **act_values)
        else:
            return super(MailActivityMixin, self).activity_schedule(act_type_xmlid=act_type_xmlid,
                                                                    date_deadline=date_deadline, summary=summary,
                                                                    note=note, **act_values)
