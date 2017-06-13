# -*- coding: utf-8 -*-

from openerp import fields, models, api, _

class SaleCovenantDescription(models.Model):
    _name = 'sale.covenant.description'

    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Text(
        string='Description',
        translate=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_number = fields.Char(
        string='Project Code',
        readonly=True,
        compute='_compute_project_number',
        copy=False,
    )
    project_related_id = fields.Many2one(
        'project.project',
        string='Project',
        states={'done': [('readonly', True)]},
    )
    event_date_description = fields.Char(
        string='Event Date',
        size=250,
        states={'done': [('readonly', True)]},
    )
    venue_description = fields.Char(
        string='Venue',
        size=250,
        states={'done': [('readonly', True)]},
    )
    amount_before_management_fee = fields.Float(
        string="Before Management Fee",
        compute='_compute_before_management_fee',
    )
    payment_term_description = fields.Text(
        string='Payment Term',
        states={'done': [('readonly', True)]},
    )
    covenant_description = fields.Text(
        string='Covenant',
        translate=True,
        default=lambda self: self._default_covenant(),
        states={'done': [('readonly', True)]},
    )
    quote_ref_id = fields.Many2one(
        'sale.order',
        string='Ref.Quotation',
        states={'done': [('readonly', True)]},
    )

    @api.multi
    @api.depends('amount_before_management_fee')
    def _compute_before_management_fee(self):
        total = sum(self.order_line.filtered(\
            lambda r : r.order_lines_group == 'before'
            ).mapped('price_unit'))
        self.amount_before_management_fee = total

    @api.onchange('project_related_id')
    def _onchange_project_number(self):
        project = self.env['project.project']\
            .browse(self.project_related_id.id)
        self.project_id = project.analytic_account_id.id
        self.project_number = project.project_number

    @api.multi
    @api.depends('project_number', 'project_related_id')
    def _compute_project_number(self):
        for quote in self:
            parent_project = self.env['project.project']\
                .browse(quote.project_related_id.id)
            quote.project_id = parent_project.analytic_account_id.id
            quote.project_number = parent_project.project_number

    @api.model
    def _default_covenant(self):
        covenants = self.env['sale.covenant.description'].search([
            ['active', '=', True],
        ])
        if covenants:
            return _(covenants[0].description)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    order_lines_group = fields.Selection(
        [('before','Before Management Fee'),
         ('manage_fee','Management and Operation Fee'),
        ],
        string='Group',
        default='before',
    )
    sale_layout_custom_group_id = fields.Many2one(
        'sale_layout.custom_group',
        string='Custom Group',
    )
    sale_order_line_margin = fields.Float(
        string='Margin',
        compute='_compute_sale_order_line_margin',
        readonly=True,
    )
    so_line_percent_margin = fields.Float(
        string='Percentage',
        compute='_compute_so_line_percent_margin',
    )
    section_code = fields.Selection(
        [('A', 'A'),
         ('B', 'B'),
         ('C', 'C'),
         ('D', 'D'),
         ('E', 'E'),
         ('F', 'F'),
        ],
        string='Section Code',
    )

    @api.multi
    def action_cal_management_fee(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.cal.manage.fee',
            'src_model': 'sale.order',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'order_line_id': self.id, 'view_id': 'view_sale_management_fee',}
        }

    @api.multi
    @api.depends('sale_order_line_margin', 'price_unit',
                 'purchase_price', 'product_uom_qty',
                 )
    @api.onchange('price_unit', 'purchase_price', 'product_uom_qty')
    def _compute_sale_order_line_margin(self):
        for line in self:
            margin = (line.price_unit - line.purchase_price) * \
                line.product_uom_qty
            line.sale_order_line_margin = margin

    @api.multi
    @api.depends('so_line_percent_margin', 'price_unit', 'purchase_price')
    @api.onchange('price_unit', 'purchase_price')
    def _compute_so_line_percent_margin(self):
        for line in self:
            margin = (line.price_unit - line.purchase_price)
            if line.price_unit:
                line.so_line_percent_margin = margin * 100.0 / \
                    (line.price_unit or 1.0)
            else:
                line.so_line_percent_margin = 0.0


class SaleLayoutCustomGroup(models.Model):
    _name = 'sale_layout.custom_group'

    name = fields.Char(
        string='Name',
        required=True,
    )

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]
