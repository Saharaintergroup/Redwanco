from odoo import models, fields, api, _


class SaleOrderAgentSalesTeam(models.Model):
    _inherit = 'sale.order.type'
    _description = "Sales Agents in Sales Teams"

    agent_id = fields.Many2one('sales.agent', string='Sales Agent')

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_ids(self):
        """Show sales agent based on customer zone"""
        if self.partner_id:
            commercial_line = self.env['commercial.line'].search([('commercial_line', 'in', self.partner_id.zone.id)])
            sales_agent = self.env['sales.agent'].search([('related_commercial_line', 'in', commercial_line.ids)])
            sales_teams = self.env['sale.order.type'].search([('sales_team_id','in',self.type_id.ids)])

            domain = {'agent_id': [('id', 'in', sales_agent.ids),('id', 'in', sales_teams.ids)]}
            return {'domain': domain}