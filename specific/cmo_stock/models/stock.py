# -*- coding: utf-8 -*-
from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    partner_id = fields.Many2one(
        'res.partner',
        default=lambda self: self._get_partner_id(),
    )

    @api.model
    def _get_partner_id(self):
        user = self.env['res.users'].browse(self._uid)
        return user.partner_id and user.partner_id.id or False


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
