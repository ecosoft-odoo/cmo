# -*- coding: utf-8 -*-
from openerp import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        context = self._context.copy()
        if context.get('order_ref', False):
            order = self.env['sale.order'].browse(context.get('order_ref'))
            product_ids = order.order_line.mapped('product_id.id')
            args = [('id', 'in', product_ids)] + args
        elif 'order_ref' in context:
            args = [('id', 'in', [])]

        # Search products by category
        if 'po_type' in context:
            Category = self.env['product.category']
            category = []
            po_type = context.get('po_type', False)
            if po_type == 'stationary':
                category = Category.search([('name', '=', 'Stationary')])
            elif po_type == 'service':
                category = Category.search([('name', '=', 'Service')])
            elif po_type == 'po_project':
                category = Category.search([('name', '=', 'Project Cost')])
            categ_ids = category.mapped('id')
            product = self.search([('categ_id', 'in', categ_ids)])
            product_ids = product.mapped('id')
            args = [('id', 'in', product_ids)] + args
        return super(ProductProduct, self).name_search(
            name, args=args, operator=operator, limit=limit)
