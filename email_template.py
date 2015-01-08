# -*- coding: utf-8 -*-

import openerp

from openerp.osv import osv
from openerp.osv import fields

import base64

from openerp.tools.translate import _


class email_template (osv.Model):

    _inherit = "email.template"

    def generate_email_batch (self, cr, uid, template_id, res_ids, context={}, fields=None):
        results = super (email_template, self).generate_email_batch (cr, uid, template_id, res_ids,
                         context=context, fields=fields)

        report_xml_pool = self.pool.get ('ir.actions.report.xml')
        res_ids_to_templates = self.get_email_template_batch (cr, uid, template_id, res_ids, context)

        # templates: res_id -> template; template -> res_ids
        templates_to_res_ids = {}
        for res_id, template in res_ids_to_templates.iteritems ():
            templates_to_res_ids.setdefault (template, []).append (res_id)

        for template, template_res_ids in templates_to_res_ids.iteritems ():
            if template.report_template:
                for res_id in template_res_ids:
                    attachments = []
                    report_name = self.render_template(cr, uid, template.report_name, template.model, res_id, context=context)
                    report_service = report_xml_pool.browse(cr, uid, template.report_template.id, context).report_name
                    # Ensure report is rendered using template's language
                    ctx = context.copy()
                    if template.lang:
                        ctx['lang'] = self.render_template_batch(cr, uid, template.lang, template.model, res_id, context)  # take 0 ?
                    result, format = openerp.report.render_report(cr, uid, [res_id], report_service, {'model': template.model}, ctx)
                    result = base64.b64encode(result)
                    if not report_name:
                        report_name = 'report.' + report_service
                    ext = "." + format
                    if not report_name.endswith(ext):
                        report_name += ext
                    attachments.append((report_name, result))

                    results[res_id]['attachments'] = attachments

        return results

