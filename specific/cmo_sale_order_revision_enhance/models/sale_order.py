# -*- coding: utf-8 -*-

from openerp import fields, models, api
from openerp.tools.translate import _


class sale_order(models.Model):
    _inherit = "sale.order"

    current_revision_id = fields.Many2one(
        'sale.order',
        string='Current Revision',
        readonly=True,
        copy=True,
    )
    old_revision_ids = fields.One2many(
        'sale.order',
        'current_revision_id',
        string='Old Revision',
        readonly=True,
        context={'active_test': False},
    )
    revision_number = fields.Integer(
        string='Revision',
        copy=False,
    )
    unrevisioned_name = fields.Char(
        string='Order Reference',
        copy=True,
        readonly=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        copy=True,
    )

    _sql_constraints = [
        ('revision_unique',
         'unique(unrevisioned_name, revision_number, company_id)',
         'Order Reference and revision must be unique per Company.'),
    ]

    @api.model
    def create(self, vals):
        if 'unrevisioned_name' not in vals:
            if vals.get('name', '/') == '/':
                seq = self.env['ir.sequence']
                vals['name'] = seq.next_by_code('sale.order') or '/'
            vals['unrevisioned_name'] = vals['name']
        return super(sale_order, self).create(vals)

    @api.multi
    def copy_quotation(self):
        self.ensure_one()
        revision_self = self.with_context(new_sale_revision=True)
        action = super(sale_order, revision_self).copy_quotation()
        old_revision = self.browse(action['res_id'])
        action['res_id'] = self.id
        self.delete_workflow()
        self.create_workflow()
        self.write({'state': 'draft'})
        self.order_line.write({'state': 'draft'})
        # remove old procurements
        self.mapped('order_line.procurement_ids').write(
            {'sale_line_id': False},
        )
        msg = _('New revision created: %s') % self.name
        self.message_post(body=msg)
        old_revision.message_post(body=msg)
        return action

    @api.returns('self', lambda value: value.id)
    @api.multi
    def copy(self, defaults=None):
        copy_id = self
        context_update = {}
        if not defaults:
            defaults = {}
        if self.env.context.get('new_sale_revision'):
            prev_name = self.name
            if self.current_revision_id:
                current_quote = self.env['sale.order'].browse(self.current_revision_id.id)
                revno = current_quote.revision_number
                copy_id = current_quote
                context_update = {
                    'name': current_quote.name,
                    'active': False,
                    'state': 'cancel',
                    'current_revision_id': self.current_revision_id.id,
                    'unrevisioned_name': current_quote.unrevisioned_name,
                    'revision_number': revno,
                }
                current_quote.write({'revision_number': revno + 1,
                            'name': '%s-%02d' % (self.unrevisioned_name,
                                                 revno + 1),
                            })
            else:
                revno = self.revision_number
                context_update = {
                    'name': prev_name,
                    'revision_number': revno,
                    'active': False,
                    'state': 'cancel',
                    'current_revision_id': self.id,
                    'unrevisioned_name': self.unrevisioned_name,
                }
                self.write({'revision_number': revno + 1,
                            'name': '%s-%02d' % (self.unrevisioned_name,
                                                 revno + 1),
                            })
            defaults.update(context_update)
        return super(sale_order, copy_id).copy(defaults)
