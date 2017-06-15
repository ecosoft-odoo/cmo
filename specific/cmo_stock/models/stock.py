# -*- coding: utf-8 -*-
from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    partner_id = fields.Many2one(
        'res.partner',
        default=lambda self: self._get_partner_id(),
    )
    default_operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Default Operating Unit',
    )

    @api.model
    def _get_partner_id(self):
        user = self.env['res.users'].browse(self._uid)
        return user.partner_id and user.partner_id.id or False

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        User = self.env['res.users']
        self.default_operating_unit_id = False
        if self.partner_id:
            user = User.search([('partner_id', '=', self.partner_id.id)])
            if user:
                self.default_operating_unit_id = \
                    user.default_operating_unit_id.id


class StockMove(models.Model):
    _inherit = 'stock.move'

    project_id = fields.Many2one(
        'project.project',
        string='Project name',
        domain=lambda self: self._get_domain(),
    )
    location_dest_id = fields.Many2one(
        'stock.location',
        default=lambda self: self._get_location_dest_id(),
    )

    @api.model
    def _get_domain(self):
        user = self.env['res.users'].browse(self._uid)
        operating_unit_ids = []
        for operating_unit in user.operating_unit_ids:
            operating_unit_ids.append(operating_unit.id)
        return [('operating_unit_id', 'in', operating_unit_ids)]

    @api.model
    def _get_location_dest_id(self):
        Location = self.env['stock.location']
        user = self.env['res.users'].browse(self._uid)
        ou_id = user.default_operating_unit_id and \
            user.default_operating_unit_id.id or False
        if ou_id:
            location = Location.search([('operating_unit_id', '=', ou_id)])
        return location and location[0].id or False

    @api.multi
    @api.onchange('product_id', 'location_id', 'location_dest_id',
                  'picking_id.partner_id')
    def onchange_product_id(self):
        for move in self:
            res = super(StockMove, move).onchange_product_id(
                move.product_id.id, move.location_id.id,
                move.location_dest_id.id, move.picking_id.partner_id.id
            )
            if res:
                res = res['value']
                move.name = res.get('name', False)
                move.product_uom = res.get('product_uom', False)
                move.product_uos = res.get('product_uos', False)
                move.product_uom_qty = res.get('product_uom_qty', False)
                move.product_uos_qty = res.get('product_uos_qty', False)
                move.location_id = res.get('location_id', False)
                move.location_dest_id = res.get('location_dest_id', False)
