from odoo import models, fields, api, _


class SaleOrderAgentSalesTeam(models.Model):
    _inherit = 'sale.order'
    _description = "Sales Agents in Sales Teams"

    agent_id_sales = fields.Many2one('sales.agent', string='Sales Agent')
"""Show sales agent based on customer zone and sales team"""
    @api.onchange('partner_id')
    def onchange_partner_sales_ids(self):
        if self.partner_id:
            commercial_line = self.env['commercial.line'].search([('commercial_line', 'in', self.partner_id.zone.id)])
            sales_agent = self.env['sales.agent'].search([('related_commercial_line', 'in', commercial_line.ids)])
            domain = {'agent_id_sales': [('id', 'in', sales_agent.ids)]}
            return {'domain': domain}

    @api.onchange('type_id')
    def onchange_type_sales_ids(self):
        if self.type_id:
            sales_team = self.env['sale.order.type'].search ([('sales_team_id','in',self.team_id.id)])
            sales_team_order_agents = self.env['sales.agent'].search ([('related_sales_team','in',sales_team.ids)])
            domain = {'agent_id_sales': [('id', 'in', sales_team_order_agents.ids)]}
            return {'domain': domain}
