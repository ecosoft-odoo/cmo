# -*- coding: utf-8 -*-
import datetime

from openerp import fields, models, api
from openerp.exceptions import ValidationError
# TODO: foreign key use, idex and ondelete


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_place = fields.Char(
        string='Project Place',
        states={'close': [('readonly', True)]},
    )
    agency_partner_id = fields.Many2one(
        'res.partner',
        string='Agency',
        states={'close': [('readonly', True)]},
        domain=[('category_id', 'like', 'Agency'), ],
    )
    brand_type_id = fields.Many2one(
        'project.brand.type',
        string='Brand type',
        related='partner_id.brand_type_id',
        readonly=True,
        store=True,
    )
    industry_id = fields.Many2one(
        'project.industry',
        string='Industry',
        related='partner_id.industry_id',
        readonly=True,
        store=True,
    )
    client_type_id = fields.Many2one(
        'project.client.type',
        string='Client Type',
        states={'close': [('readonly', True)]},
    )
    obligation_id = fields.Many2one(
        'project.obligation',
        string='Obligation',
        states={'close': [('readonly', True)]},
    )
    function_id = fields.Many2one(
        'project.function',
        string='Function',
        states={'close': [('readonly', True)]},
    )
    location_id = fields.Many2one(
        'project.location',
        string='Location',
        states={'close': [('readonly', True)]},
    )
    description = fields.Text(
        string='Description',
        states={'close': [('readonly', True)]},
    )
    project_from_id = fields.Many2one(
        'project.from',
        string='Project From',
        states={'close': [('readonly', True)]},
    )
    project_type_id = fields.Many2one(
        'project.type',
        string='Project Type',
        states={'close': [('readonly', True)]},
    )
    project_budget = fields.Float(
        string='Project Budget',
        states={'close': [('readonly', True)]},
    )
    actual_price = fields.Float(
        string='Actual Price',
        states={'close': [('readonly', True)]},
        compute='_compute_price_and_cost',
        store=True,
    )
    estimate_cost = fields.Float(
        string='Estimate Cost',
        states={'close': [('readonly', True)]},
        compute='_compute_price_and_cost',
        store=True,
    )
    pre_cost = fields.Float(
        string='Pre-Project',
        states={'close': [('readonly', True)]},
    )
    actual_po = fields.Float(
        string='Actual PO',
        states={'close': [('readonly', True)]},
        compute='_compute_actual_po',
        store=True,
    )
    remain_advance = fields.Float(
        string='Advance Balance',
        compute='_compute_remain_advance',
        states={'close': [('readonly', True)]},
    )
    expense = fields.Float(
        string='Expense',
        states={'close': [('readonly', True)]},
        compute='_compute_expense',
    )
    date_brief = fields.Date(
        string='Brief Date',
        default=lambda self: fields.Date.context_today(self),
        states={'close': [('readonly', True)]},
    )
    date = fields.Date(
        default=lambda self: fields.Date.context_today(self),
        states={'close': [('readonly', True)]},
    )
    competitor_ids = fields.Many2many(
        'project.competitor',
        'res_competitor_rel', 'project_id', 'competitor_id',
        string='Competitors',
        states={'close': [('readonly', True)]},
    )
    project_number = fields.Char(
        string='Project Code',
        readonly=True,
        states={'close': [('readonly', True)]},
        copy=False,
    )
    project_member_ids = fields.One2many(
        'project.team.member',
        'project_id',
        string='Team Member',
        states={'close': [('readonly', True)]},
    )
    close_reason = fields.Selection(
        [('close', 'Completed'),
         ('reject', 'Reject'),
         ('lost', 'Lost'),
         ('cancel', 'Cancelled'),
         ('terminate', 'Terminated'),
        ],
        string='Close Reason',
        states={'close': [('readonly', True)]},
    )
    department_id = fields.Many2one( # no use
        'hr.department',
        string='Department',
        states={'close': [('readonly', True)]},
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        default=lambda self: self.env.user.default_operating_unit_id,
        states={'close': [('readonly', True)]},
    )
    state = fields.Selection(
        [('template', 'Template'),
         ('draft','Draft'),
         ('validate', 'Validated'),
         ('open','In Progress'),
         ('ready_billing', 'Ready to Billing'),
         ('invoices', 'Invoices'),
         ('paid', 'Paid'),
         ('cancelled', 'Incompleted'),
         ('pending','Pending'),
         ('close','Completed'), ],
         string='Status',
         required=True,
         copy=False,
         default='draft',
    )
    state_before_inactive = fields.Char(
        string='Latest State',
    )
    is_active_state = fields.Boolean(
        string='Is Active State',
        compute='_get_state_before_inactive',
    )
    lost_reason_id = fields.Many2one(
        'project.lost.reason',
        string='Lost Reason',
    )
    lost_by_id = fields.Many2one(
        'res.partner',
        string='Lost By',
        domain=[('category_id', 'like', 'Competitor'), ],
    )
    reject_reason_id = fields.Many2one(
        'project.reject.reason',
        string='Reject Reason',
    )
    hold_reason = fields.Text(
        string='Hold Reason',
        states={'close': [('readonly', True)]},
    )
    assign_id = fields.Many2one(
        'res.users',
        string='Assign to',
        states={'close': [('readonly', True)]},
    )
    assign_description = fields.Text(
        string='Description',
        states={'close': [('readonly', True)]},
    )
    project_parent_id = fields.Many2one(
        'project.project',
        string='Parent Project',
        compute='_set_project_analytic_account',
        states={'close': [('readonly', True)]},
        store=True,
    )
    quote_related_ids = fields.One2many(
        'sale.order',
        'project_related_id',
        string='Related Quotation',
        domain=[('order_type', '=', 'quotation'), ],
    )
    purchase_related_ids = fields.One2many(
        'purchase.order',
        'project_id',
        string='Related Project',
    )
    invoice_related_ids = fields.One2many(
        'account.invoice',
        'project_ref_id',
        string='Related Invoice',
        domain=[('type', '=', 'out_invoice'), ],

    )
    is_paid = fields.Boolean(
        string='is paid',
        compute='_compute_invoice_related_ids',
    )
    remaining_cost = fields.Float(
        string='Remaining Cost',
        compute='_compute_remaining_cost',
    )

    _defaults = {
        'use_tasks': False
    }

    @api.model
    def create(self, vals):
        if vals.get('project_number', '/') == '/':
            ctx = self._context.copy()
            current_date = fields.Date.context_today(self)
            fiscalyear_id = self.env['account.fiscalyear'].find(dt=current_date)
            ctx["fiscalyear_id"] = fiscalyear_id
            vals['project_number'] = self.env['ir.sequence']\
                .with_context(ctx).get('cmo.project') # create sequence number
        project = super(ProjectProject, self).create(vals)
        return project

    @api.multi
    def write(self, vals):
        return super(ProjectProject, self).write(vals)

    @api.multi
    def action_validate(self):
        res = self.write({'state':'validate'})
        return res

    @api.multi
    def action_approve(self):
        res = self.write({'state': 'open'})
        return res

    @api.multi
    def action_back_to_draft(self):
        res = self.write({'state': 'draft'})
        return res

    @api.multi
    def action_invoices(self):
        res = self.write({'state': 'invoices'})
        return res

    @api.multi
    def action_received(self):
        res = self.write({'state': 'received'})
        return res

    @api.multi
    def action_ready_billing(self):
        res = self.write({'state': 'ready_billing'})
        return res

    @api.multi
    def action_back_to_open(self):
        res = self.write({'state': 'open'})
        return res

    @api.multi
    def action_released(self):
        if self.state_before_inactive:
            res = self.write({'state':self.state_before_inactive})  # state_bf_hold
        else:
            res = self.write({'state':'open'})
        self.write({
            'close_reason': False,
            'lost_reason_id': False,
            'lost_by_id': False,
            'reject_reason_id': False,
        })
        return res

    @api.multi
    def _get_state_before_inactive(self):
        for project in self:
            if project.state and \
               (project.state != 'pending') and \
               (project.state != 'close') and \
               (project.state != 'cancelled'):
               project.write({'state_before_inactive': project.state})

    @api.multi
    def _set_project_analytic_account(self):
        for project in self:
            parent_project = self.env['project.project'].browse(
                project.project_parent_id.id)
            project.parent_id = parent_project.analytic_account_id

    @api.multi
    @api.constrains('date_brief', 'date')
    def _check_date_briefs(self):
        self.ensure_one()
        if self.date_brief > self.date:
            return ValidationError("project brief-date must be lower than "
                                                        "project end-date.")

    @api.multi
    def quotation_relate_project_tree_view(self):
        self.ensure_one()
        domain = [
            ('project_related_id', 'like', self.id),
            ('order_type', '=', 'quotation'),
        ]
        action = self.env.ref('sale.action_quotations')
        result = action.read()[0]
        result.update({'domain': domain})
        return result

    @api.multi
    def purchase_relate_project_tree_view(self):
        self.ensure_one()
        domain = [
            ('project_id', 'like', self.id),
        ]
        action = self.env.ref('purchase.purchase_form_action')
        result = action.read()[0]
        result.update({'domain': domain})
        return result

    @api.multi
    def invoice_relate_project_tree_view(self):
        self.ensure_one()
        domain = [
            ('project_ref_id', 'like', self.id),
            ('type', '=', 'out_invoice'),
        ]
        action = self.env.ref('account.action_invoice_tree1')
        result = action.read()[0]
        result.update({'domain': domain})
        return result

    @api.multi
    @api.depends(
        'actual_price',
        'estimate_cost',
        'quote_related_ids',
        'quote_related_ids.order_line',
    )
    def _compute_price_and_cost(self):
        for project in self:
            actual_price = 0.0
            estimate_cost = 0.0
            quotes = project.quote_related_ids.filtered(
                lambda r: r.state in ('draft', 'done')
            )
            for quote in quotes:
                actual_price += quote.amount_untaxed
                estimate_cost += sum(quote.order_line.filtered(
                    lambda r: r.purchase_price > 0.0).mapped('purchase_price'))
            project.actual_price = actual_price
            project.estimate_cost = estimate_cost

    @api.multi
    @api.depends(
        'actual_po',
        'purchase_related_ids',
        'purchase_related_ids.state',
        'purchase_related_ids.amount_untaxed',
    )
    def _compute_actual_po(self):
        for project in self:
            purchase_orders = project.purchase_related_ids.filtered(
                lambda r: r.state in ('approved', 'done')
            )
            project.actual_po = sum(purchase_orders.mapped('amount_untaxed'))

    @api.multi
    def name_get(self):
        res = []
        for project in self:
            name = project.name or '/'
            if name and project.project_number:
                name = '['+project.project_number+'] ' + name
            res.append((project.id, name))
        return res

    @api.multi
    @api.depends('estimate_cost', 'pre_cost', 'actual_po', 'expense')
    def _compute_remaining_cost(self):
        for project in self:
            remaining = (project.estimate_cost + project.pre_cost) - \
                (project.actual_po + project.expense)
            project.remaining_cost = remaining

    @api.multi
    @api.depends('expense')
    def _compute_expense(self):
        for project in self:
            expense_lines = self.env['hr.expense.line'].search([
                 ['analytic_account', '=', project.analytic_account_id.id],
            ])
            expense = sum(expense_lines.filtered(
                lambda r: (r.expense_id.state in ('done', 'paid')) and
                          (r.expense_id.is_employee_advance is False)
            ).mapped('total_amount'))
            project.expense = expense

    @api.multi
    @api.depends('is_paid', 'invoice_related_ids', 'invoice_related_ids.state')
    def _compute_invoice_related_ids(self):
        for project in self:
            invoice_open = project.invoice_related_ids.filtered(
                lambda r: r.state in ('open', 'paid')
            )
            invoice_paid = project.invoice_related_ids.filtered(
                lambda r: r.state in ('paid')
            )
            if invoice_paid and \
                    (len(invoice_paid) == len(project.invoice_related_ids)):
                project.write({'state': 'paid'})
            elif invoice_open:
                project.write({'state': 'invoices'})
            else:
                project.write({'state': 'ready_billing'})

    @api.multi
    @api.depends('remain_advance')
    def _compute_remain_advance(self):
        for rec in self:
            Expense_line = self.env['hr.expense.line'].search([
                ('analytic_account', '=', rec.analytic_account_id.id),
            ])
            line_ids = Expense_line.filtered(
                lambda r: r.expense_id.is_employee_advance and
                (r.expense_id.state in 'paid'))
            rec.remain_advance = sum(
                line_ids.expense_id.mapped('amount_to_clearing'))


class ProjectTeamMember(models.Model):
    _name = 'project.team.member'
    _description = 'Project Team Member'
    _rec_name = 'employee_id'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        ondelete='cascade',
        index=True,
    )
    position_id = fields.Many2one(
        'project.position',
        string='Member Position',
        required=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Name',
        required=True,
    )
    date_start = fields.Date(
        string='Start',
    )
    date_end = fields.Date(
        string='End date',
    )
    remark = fields.Text(
        string="Remark"
    )


class ProjectBrandType(models.Model):
    _name = 'project.brand.type'
    _description = 'Project Brand Type'

    name = fields.Char(
        string='Brand Type',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Brand Type must be unique!'),
    ]

class ProjectClientType(models.Model):
    _name = 'project.client.type'
    _description = 'Project Client Type'

    name = fields.Char(
        string='Client Type',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Client Type must be unique!'),
    ]

class ProjectIndustry(models.Model):
    _name = 'project.industry'
    _description = 'Project Industry'

    name = fields.Char(
        string='Industry',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Industry must be unique!'),
    ]

class ProjectLocation(models.Model):
    _name = 'project.location'
    _description = 'Project Location'

    name = fields.Char(
        string='Location',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Location must be unique!'),
    ]

class ProjectObligation(models.Model):
    _name = 'project.obligation'
    _description = 'Project Obligation'

    name = fields.Char(
        string='Obligation',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Obligation must be unique!'),
    ]

class ProjectFrom(models.Model):
    _name = 'project.from'
    _description = 'Project From'

    name = fields.Char(
        string='Project From',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project From must be unique!'),
    ]

class ProjectFunction(models.Model):
    _name = 'project.function'
    _description = 'Project Function'

    name = fields.Char(
        string='Name',
        required=True,
        size=128,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Function must be unique!'),
    ]

class ProjectPosition(models.Model):
    _name = 'project.position'
    _description = 'Project Position'

    name = fields.Char(
        string='Position',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Position must be unique!'),
    ]


class ProjectType(models.Model):
    _name = 'project.type'
    _description = 'Project Type'

    name = fields.Char(
        string='Project Type',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Position must be unique!'),
    ]

class ProjectCompetitor(models.Model):
    _name = 'project.competitor'
    _description = 'Project Competitor'

    name = fields.Char(
        string='Name',
    )
    company = fields.Char(
        string='Company',
        required=True,
    )
    remark = fields.Text(
        string='Remark',
    )

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Lost by must be unique!'),
    ]

class ProjectLostReason(models.Model):
    _name = 'project.lost.reason'
    _description = 'Project Lost Reason'

    name = fields.Char(
        string='Reason',
        required=True,
    )


class ProjectRejectReason(models.Model):
    _name = 'project.reject.reason'
    _description = 'Project Reject Reason'

    name = fields.Char(
        string='Reason',
        required=True,
    )
