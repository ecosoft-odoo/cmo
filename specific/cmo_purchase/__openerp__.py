# -*- coding: utf-8 -*-

{
    'name': "CMO :: Purchase Extension",
    'summary': "",
    'author': "Tharathip C.",
    'website': "http://ecosoft.co.th",
    'category': 'Purchase Management',
    "version": "1.0",
    'depends': [
        'purchase_operating_unit',
    ],
    'data': [
        'security/cmo_purchase_security.xml',
        'views/purchase_view.xml',
        'reports/purchase_report.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
