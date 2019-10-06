from odoo import api, fields, models


class SalesTeamSalesType(models.Model):
    _inherit = 'sale.order.type'
    _description = 'Sales Team in sale order type'

    sales_team_id = fields.Many2one('crm.team',string='Sales Team')


class SaleTeam(models.Model):
    _inherit = 'sale.order'
    _description = 'Onchange in Sales Team onchange sale order type'

    @api.multi
    @api.onchange('type_id')
    def onchange_type_id(self):
        self.team_id = self.type_id.sales_team_id.id

