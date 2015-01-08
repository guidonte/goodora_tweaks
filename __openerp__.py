{
    'name': 'Goodora - Tweaks',
    'description': 'Miscellaneous tweaks by Goodora s.r.l.',
    'author': 'Goodora s.r.l.',
    'version': '0.1',
    'category': 'Hidden',
    'depends': [
        'web',
        'base',
        'mail',
        'email_template',
        'contacts',
        'product',
    ],
    'js': ['static/src/js/goodora_tweaks.js'],
    'css': ['static/src/css/goodora_tweaks.css'],
    'qweb': [
        'static/src/xml/base.xml',
    ],
    'data': [
        'ir_config_parameter_data.xml',
        'contacts_view.xml',
        'product_view.xml',
        'res_partner_view.xml',
        'mail_data.xml',
    ],
    'installable': True,
    'auto_install': False,
}

