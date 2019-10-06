from odoo import models, fields, api, _


class SaleOrderAgentSalesTeam(models.Model):
    _inherit = 'sale.order'
    _description = "Sales Agents in Sales Teams"

    agent_id_sales = fields.Many2one('sales.agent', string='Sales Agent',required=True)


    @api.onchange('partner_id', 'type_id')
    def onchange_partner_sales_ids(self):
        if self.partner_id:
            newfilter = None
            commercial_line = self.env['commercial.line'].search([('commercial_line', 'in', self.partner_id.zone.id)])
            sales_agent = self.env['sales.agent'].search([('related_commercial_line', 'in', commercial_line.ids)])
            crm_team = self.env['crm.team'].search([])
            for team in crm_team:
                if team == self.type_id.sales_team_id:
                    newfilter = team.agent_ids
            if not newfilter:
                domain = {'agent_id_sales': [('id', 'in', sales_agent.ids)]}
            else:
                domain = {'agent_id_sales': [('id', 'in', sales_agent.ids),('id', 'in', newfilter.ids)]}
            return {'domain': domain}
