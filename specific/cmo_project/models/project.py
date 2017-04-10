# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ProjectProject(models.Model):
    _inherit = "project.project"
    # TODO match all selection field with master data
    project_place = fields.Char(
        string='Project Place',
        states={'close': [('readonly', True)]}
    )
    agency = fields.Many2one(
        'res.partner',
        string="Agency",
        states={'close': [('readonly', True)]},
        domain=[('category_id', 'like', 'Agency'), ],
    )
    brand_type = fields.Many2one(
        'project.brand.type',
        string="Brand type",
        states={'close': [('readonly', True)]},
    )
    industry = fields.Many2one(
        'project.industry',
        string="Industry",
        states={'close':[('readonly', True)]},
    )
    client_type = fields.Many2one(
        'project.client.type',
        string='Client Type',
        states={'close': [('readonly', True)]},
    )
    obligation = fields.Many2one(
        'project.obligation',
        string='Obligation',
        states={'close': [('readonly', True)]},
    )
    function_id = fields.Many2one(
        'project.function',
        string='Function',
        states={'close': [('readonly', True)]},
    )
    lead_source = fields.Selection(
        [('compaign', 'Campaign'),
         ('cold_call', 'Cold Call'),
         ('comference', 'Conference'),
         ('direct_mail', 'Direct Mail'),
         ('email', 'Email'),
         ('employee', 'Employee'),
         ('existing_customer', 'Existing Customer'),
         ('other', 'Others'),
         ('partner', 'Partner'),
         ('campaign', 'Campaign'),
         ],
        string='Lead Source',
        states={'close': [('readonly', True)]},
    )
    location = fields.Many2one(
        'project.location',
        string='Location',
        states={'close': [('readonly', True)]},
    )
    description = fields.Text(
        string='Description',
        states={'close': [('readonly', True)]},
    )
    project_from = fields.Many2one(
        'project.from',
        string='Project From',
        states={'close': [('readonly', True)]},
    )
    project_type = fields.Many2one(
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
    )
    estimate_cost = fields.Float(
        string='Estimate cost',
        states={'close': [('readonly', True)]},
    )
    pre_cost = fields.Float(
        string='Pre-project',
        states={'close': [('readonly', True)]},
    )
    actual_po = fields.Float(
        string='Actual PO',
        states={'close': [('readonly', True)]},
    )
    remain_advance = fields.Float(
        string='Remain Advance',
        states={'close': [('readonly', True)]},
    )
    expense = fields.Float(
        string='Expense',
        states={'close': [('readonly', True)]},
    )
    brief_date = fields.Date(
        string='Brief date',
        default=fields.Date.today,
        states={'close': [('readonly', True)]},
    )
    competitor =fields.Many2many(
        'res.partner',
        string='Competitors',
        states={'close': [('readonly', True)]},
        domain=[('category_id', 'like', 'Competitor'), ],
    )
    project_number = fields.Char(
        string='Project Code',
        readonly=True,
        states={'close': [('readonly', True)]},
    )
    project_members = fields.One2many(
        'project.team.member',
        'project_ids',
        string='Team Member',
        states={'close': [('readonly', True)]},
    )
    close_reason = fields.Selection([
        ('close', "Closed"),
        ('reject', "Reject"),
        ('lost', "Lost"),
        ],
        states={'close': [('readonly', True)]},
    )
    department = fields.One2many(
        'hr.department',
        'hr_ids',
        string='Department',
        states={'close': [('readonly', True)]},
    )
    state = fields.Selection(
        selection_add=[
            ('draft','Draft'),
            #('complete', 'Completed'),
            ('billing', 'Billing'),
            ('received', 'Received'),
            ]
    )
    _defaults = {
        'state': 'draft',
    }

    @api.model
    def create(self, vals):
        vals['project_number'] = self.env['ir.sequence'].get('cmo.project') # create sequence nummber
        project = super(ProjectProject, self).create(vals)
        Task = self.env['project.task']
        task_list = [{'name': u"Task {}".format(vals['name'])}, ]
        for task in task_list:
            Task.create({'name': task.get('name', False),
                         'project_id': project.id, })
        return project

    @api.multi
    def action_approve(self):
        res = self.write({'state': 'open'})
        return res

    @api.multi
    def action_back_to_draft(self):
        res = self.write({'state': 'draft'})
        return res

    @api.multi
    def action_billing(self):
        res = self.write({'state': 'billing'})
        return res

    @api.multi
    def action_received(self):
        res = self.write({'state': 'received'})
        return res
    # @api.multi TODO: if all state task are complete then project is complete
    # def write(self, vals):
    #     super().write()
    #     if vals.get('state') == 'Completed':
    #         for task in self:
    #             project = task.project_id
    #             tasks = project.task_ids
    #             not_done_tasks = tasks.filtered(lambda l: l.state != 'Completed')
    #             if not_done_tasks:
    #                 continue
    #             else:
    #                 project.state = 'Completed'

class ProjectTeamMember(models.Model):
    _name = "project.team.member"
    _description = "Project Team Member"

    project_ids = fields.Many2one(
        'project.project',
    )
    member_position = fields.Many2one(
        'project.position',
        string='Member Position',
        required=True,
    )
    team_member = fields.Many2one(
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

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Project Team Member must be unique!'),
    ]

class ProjectBrandType(models.Model):
    _name = "project.brand.type"
    _description = "Project Brand Type"

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
    _name = "project.client.type"
    _description = "Project Client Type"

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

class Projectindustry(models.Model):
    _name = "project.industry"
    _description = "Project Industry"

    name = fields.Char(
        string='industry',
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
    _name = "project.location"
    _description = "Project Location"

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
    _name = "project.obligation"
    _description = "Project Obligation"

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
    _name = "project.from"
    _description = "Project From"

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
    _name = "project.function"
    _description = "Project Function"

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
    _name = "project.position"
    _description = "Project Position"

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
    _name = "project.type"
    _description = "Project Type"

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
