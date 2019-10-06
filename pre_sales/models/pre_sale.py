from odoo import models, fields, api, _


class PreSalesZone(models.Model):
    _name = 'sale.zone'
    _description = 'Sales Zones'

    name = fields.Char(string='Name', required=True, help="Name of the zone")
    code = fields.Char(string='Code', required=True, help='Code defined for the zone')
    active = fields.Boolean(default=True, help="If unchecked, it will allow you to hide the zones")


class CommercialLines(models.Model):
    _name = 'commercial.line'
    _description = 'Commercial Lines'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    active = fields.Boolean(default=True,
                            help="If unchecked, it will allow you to hide the Commercial Lines")
    commercial_line = fields.Many2many('sale.zone', string='Commercial Zones')


class DeliveryLines(models.Model):
    _name = 'delivery.line'
    _description = 'Delivery Lines'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    active = fields.Boolean(default=True,
                            help="If unchecked, it will allow you to hide the Delivery Lines")
    delivery_line = fields.Many2many('sale.zone', string='Delivery Zones')


class SalesAgent(models.Model):
    _name = 'sales.agent'
    _description = 'Sales Agent'
    _rec_name = 'agent_name'

    agent_name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', copy=False, readonly=True)
    email = fields.Char('Email', required=True)
    mobile = fields.Char('Mobile', required=True)
    active = fields.Boolean(default=True,
                            help="If unchecked, it will allow you to hide the Sales Agent")
    related_commercial_line = fields.Many2one('commercial.line', string='Commercial Line')
    total_sales = fields.Integer(compute='_compute_total_sales_count')

    def _compute_total_sales_count(self):

        """Sale Count in sales agent form"""

        all_partners = self.search([('id', 'in', self.ids)])
        sale_order_groups = self.env['sale.order'].read_group(
            domain=[('agent_id', 'in', all_partners.ids)],
            fields=['agent_id'], groupby=['agent_id']
        )
        for group in sale_order_groups:
            partner = self.browse(group['agent_id'][0])
            if partner in self:
                partner.total_sales += group['agent_id_count']

    @api.model
    def create(self, vals):

        """Create a related partner for sales agent"""

        if vals.get('name', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code(
                'sales.agent') or _('New')
        result = super(SalesAgent, self).create(vals)

        user = self.env['res.users'].create({
            'name': result.agent_name,
            'login': result.email,
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
        })
        user.partner_id.update({
            'mobile': result.mobile
        })
        return result


class DeliveryAgent(models.Model):
    _name = 'delivery.agent'
    _description = 'Delivery Agent'
    _rec_name = 'agent_name'

    agent_name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', copy=False, readonly=True)
    email = fields.Char('Email', required=True)
    mobile = fields.Char('Mobile', required=True)
    active = fields.Boolean(default=True,
                            help="If unchecked, it will allow you to hide the Delivery Agent")
    related_delivery_line = fields.Many2one('delivery.line', string='Delivery Line')
    orders_count = fields.Integer(compute='_compute_send_orders')

    def _compute_send_orders(self):

        """Picking Orders Count in delivery agent"""

        all_partners = self.search([('id', 'in', self.ids)])
        send_order_groups = self.env['picking.order'].read_group(
            domain=[('name', 'in', all_partners.ids)],
            fields=['name'], groupby=['name']
        )
        for group in send_order_groups:
            partner = self.browse(group['name'][0])
            if partner in self:
                partner.orders_count += group['name_count']

    @api.model
    def create(self, vals):

        """Create a related partner for delivery agent """

        if vals.get('name', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code(
                'delivery.agent') or _('New')
        result = super(DeliveryAgent, self).create(vals)

        user = self.env['res.users'].create({
            'name': result.agent_name,
            'login': result.email,
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
        })
        user.partner_id.update({
            'mobile': result.mobile
        })
        return result


class ResPartnerForm(models.Model):
    _inherit = 'res.partner'

    zone = fields.Many2one('sale.zone', string='Zone')

