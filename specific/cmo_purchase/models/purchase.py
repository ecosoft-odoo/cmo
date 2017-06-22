# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    project_id = fields.Many2one(
        'project.project',
        string='Project Name',
        ondelete='restrict',
    )
    order_ref = fields.Many2one(
        'sale.order',
        string='Quotation Number',
        ondelete='restrict',
    )
    event_date_description = fields.Char(
        string='Event Date',
        size=250,
    )
    venue_description = fields.Char(
        string='Venue',
        size=250,
    )
    po_type = fields.Selection(
        [('po_project', 'PO Project'), ('stationary', 'Stationary'),
         ('service', 'Service')],
        string='PO Type',
        required=True,
        default='po_project',
    )
    order_line2 = fields.One2many(
        'purchase.order.line', 'order_id',
        string='Order Lines',
        states={'approved': [('readonly', True)],
                'done': [('readonly', True)]},
        copy=True,
    )

    @api.onchange('order_ref')
    def _onchange_order_id(self):
        self.event_date_description = self.order_ref.event_date_description
        self.venue_description = self.order_ref.venue_description

    @api.onchange('project_id')
    def _onchange_product_id(self):
        self.order_ref = False
        self.event_date_description = False
        self.venue_description = False
        for line in self.order_line:
            line.product_ref = False


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_ref = fields.Many2one(
        'product.product',
        string='Product Ref',
    )
