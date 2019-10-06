from odoo import models, fields, api, _


class SaleOrderAgentSalesTeam(models.Model):
    _inherit = 'sale.order'
    _description = "Sales Agents in Sales Teams"

    agent_id_sales = fields.Many2one('sales.agent', string='Sales Agent')

    @api.onchange('partner_id','type_id')
    def onchange_partner__sales_ids(self):
        """Show sales agent based on customer zone and sales team"""
        if self.partner_id:
            commercial_line = self.env['commercial.line'].search([('commercial_line', 'in', self.partner_id.zone.id)])
            sales_agent = self.env['sales.agent'].search([('related_commercial_line', 'in', commercial_line.ids)])
            sales_team = self.env['sale.order.type'].search ([('sales_team_id','=',self.type_id.sales_team_id.name)])
            sales_team_order_agents = self.env['sales.agent'].search ([('agent_id','in',sales_team.sales_team_id.agent_ids.ids)])
            # agent_list = []
            # teams = self.env['crm.team'].search([])
            # for val in teams:
            #     for agents in self.team_id.agent_ids:
            #         if agents.id == val.agents.id:
            #             agent_list.append(val.id)

            domain = {'agent_id_sales': [('id', 'in', sales_team_order_agents)]}
            return {'domain': domain}
            # ('id', 'in', sales_agent.ids),
