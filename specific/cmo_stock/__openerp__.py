# -*- coding: utf-8 -*-
{
    "name": "CMO :: Stock Extension",
    "summary": "",
    "version": "1.0",
    "category": "Warehouse Management",
    "description": """

    """,
    "website": "http://ecosoft.co.th",
    "author": "Tharathip C.",
    "license": "AGPL-3",
    "depends": [
        'stock_operating_unit',
        'stock_account',
    ],
    "data": [
        'views/stock_view.xml',
        'views/report_stockpicking.xml',
        'views/stock_report.xml',
        'views/stock_valuation_history_view.xml',
    ],
    "application": False,
    "installable": True,
}
