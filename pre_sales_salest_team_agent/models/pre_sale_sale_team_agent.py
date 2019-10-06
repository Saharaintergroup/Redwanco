from odoo import models, fields, api, _


class SaleOrderAgentSalesTeam(models.Model):
    _inherit = 'sale.order'
    _description = "Sales Agents in Sales Teams"

    agent_id = fields.Many2one('sales.agent', string='Sales Agent')

    @api.onchange('partner_id','type_id')
    def onchange_partner__sales_ids(self):
        """Show sales agent based on customer zone and sales team"""
        if self.partner_id:
            commercial_line = self.env['commercial.line'].search([('commercial_line', 'in', self.partner_id.zone.id)])
            sales_agent = self.env['sales.agent'].search([('related_commercial_line', 'in', commercial_line.ids)])
            sales_team_agents = self.env['crm.team'].search([('agent_id','in',self.type_id.sales_team_id.agent_ids.ids)])

            domain = {'agent_id': [('id', 'in', sales_team_agents.ids)]}
            return {'domain': domain}
