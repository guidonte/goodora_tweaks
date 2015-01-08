# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp.osv import fields

from openerp.tools.translate import _


class mail_compose_message (osv.TransientModel):
    _inherit = 'mail.compose.message'

    def _get_default_reply_to (self, cr, uid, context):
        template_obj = self.pool.get ('email.template')
        template = template_obj.browse (cr, uid, context['default_template_id'])

        return template.reply_to or template.email_from

    _defaults = {
        'same_thread': False,
        'reply_to': _get_default_reply_to,
    }

    def send_mail(self, cr, uid, ids, context=None):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed. """
        if context is None:
            context = {}
        # clean the context (hint: mass mailing sets some default values that
        # could be wrongly interpreted by mail_mail)
        context.pop('default_email_to', None)
        context.pop('default_partner_ids', None)

        active_ids = context.get('active_ids')
        is_log = context.get('mail_compose_log', False)

        for wizard in self.browse(cr, uid, ids, context=context):
            mass_mail_mode = wizard.composition_mode == 'mass_mail'
            active_model_pool = self.pool[wizard.model if wizard.model else 'mail.thread']
            if not hasattr(active_model_pool, 'message_post'):
                context['thread_model'] = wizard.model
                active_model_pool = self.pool['mail.thread']

            # wizard works in batch mode: [res_id] or active_ids or active_domain
            if mass_mail_mode and wizard.use_active_domain and wizard.model:
                res_ids = self.pool[wizard.model].search(cr, uid, eval(wizard.active_domain), context=context)
            elif mass_mail_mode and wizard.model and active_ids:
                res_ids = active_ids
            else:
                res_ids = [wizard.res_id]

            all_mail_values = self.get_mail_values(cr, uid, wizard, res_ids, context=context)

            for res_id, mail_values in all_mail_values.iteritems():
                if mass_mail_mode and not wizard.post:
                    mail_id = self.pool.get('mail.mail').create(cr, uid, mail_values, context=context)
                    mail = self.pool.get('mail.mail').browse (cr, uid, mail_id)
                    # guidonte: Store the attachments and remember the IDs
                    for attachment in mail_values.get('attachments', []):
                        attachment_data = {
                                'name': attachment[0],
                                'datas_fname': attachment[0],
                                'datas': attachment[1],
                                'type': 'binary',
                                'res_model': 'mail.message',
                                'res_id': mail.mail_message_id.id,
                        }
                        attachment_id = self.pool.get('ir.attachment').create(cr, uid, attachment_data, context=context)
                        mail.write ({'attachment_ids': [(4, attachment_id)]})

                    # guidonte: Record origin data on the mail message
                    mail.write ({
                        'model': wizard.model,
                        'res_id': res_id,
                    })
                else:
                    subtype = 'mail.mt_comment'
                    if is_log:  # log a note: subtype is False
                        subtype = False
                    elif mass_mail_mode:  # mass mail: is a log pushed to recipients unless specified, author not added
                        if not wizard.notify:
                            subtype = False
                        context = dict(context,
                                       mail_notify_force_send=False,  # do not send emails directly but use the queue instead
                                       mail_create_nosubscribe=True)  # add context key to avoid subscribing the author
                    active_model_pool.message_post(cr, uid, [res_id], type='comment', subtype=subtype, context=context, **mail_values)

        return {'type': 'ir.actions.act_window_close'}

