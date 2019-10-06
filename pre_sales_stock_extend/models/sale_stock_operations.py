from odoo import models, fields, api, _


class PickingOrders(models.Model):
    _name = 'picking.order'

    name = fields.Many2one('delivery.agent', string='Delivery Agents', required=True)
    active = fields.Boolean(default=True)
    code = fields.Char(string='Code', copy=False, readonly=True)
    picking_lines = fields.One2many('order.picking', 'picking_id', string='Pickings')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('delivered', 'Delivered'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, copy=False, index=True, default='draft')
    barcode = fields.Char('Barcode', copy=False)
    delivery_line = fields.Many2one('delivery.line', string='Delivery Lines')

    @api.model
    def create(self, vals):
        if vals.get('name'):
            vals['code'] = self.env['ir.sequence'].next_by_code(
                'picking.order') or _('New')
        result = super(PickingOrders, self).create(vals)
        return result

    @api.onchange('barcode')
    def onchange_barcode(self):
        picking = self.env['stock.picking'].search([('name', '=', self.barcode)])
        if picking:
            self.picking_lines = self.env['order.picking'].create({
                'reference': picking.id,
                'partner_id': picking.partner_id.id,
                'phone': picking.partner_id.phone,
                'zone': picking.partner_id.zone.id
            })

    @api.multi
    def button_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def action_send_order(self):
        return self.write({'state': 'delivered'})

    @api.multi
    def action_confirm(self):
        return self.write({'state': 'confirm'})

    @api.onchange('delivery_line')
    def onchange_delivery_line(self):
        agents = self.env['delivery.agent'].search([('related_delivery_line', '=', self.delivery_line.id)])
        domain = {'name': [('id', 'in', agents.ids)]}
        return {'domain': domain}


class SendOutOrders(models.Model):
    _name = 'order.picking'
    _description = "Picking orders in send out form"

    reference = fields.Many2one('stock.picking', String='Reference', required=True)
    picking_id = fields.Many2one('picking.order', String='Picking')
    partner_id = fields.Many2one('res.partner', string='Customer')
    phone = fields.Char('Phone')
    doc_ref = fields.Char('Source Document')
    zone = fields.Many2one('sale.zone', string='Zone')

    @api.onchange('reference')
    def onchange_reference(self):
        self.update({
            'partner_id': self.reference.partner_id.id,
            'phone': self.reference.partner_id.phone,
            'zone': self.reference.partner_id.zone.id,
            'doc_ref': self.reference.origin
        })
        pickings = self.env['stock.picking'].search(
            [('delivery_line', '=', self.picking_id.delivery_line.id),('picking_sout', '=', False),('picking_type_code', '=', 'outgoing')])
        domain = {'reference': [('id', 'in', pickings.ids)]}
        return {'domain': domain}


class PickingOrder(models.Model):
    _inherit = 'stock.picking'
    _description = "Delivery line in stock picking"

    picking_sout = fields.One2many('order.picking', 'reference', 'Picking Send-Out Form')

    @api.model
    def create(self, vals_list):
        res = super(PickingOrder, self).create(vals_list)
        lines_to_deliver = self.env['delivery.line'].search([])
        for line in lines_to_deliver:
            for vals in line.delivery_line:
                if vals.id == res.partner_id.zone.id:
                    res.update({
                        'delivery_line': line.id
                    })
        return res

