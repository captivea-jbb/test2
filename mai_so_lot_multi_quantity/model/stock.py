from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    lot_ids = fields.Many2many('stock.production.lot', string="Crate", copy=False)
    assign_lot = fields.Boolean(string='Assign Lot')
    
    def create_stock_move_line(self):
        for move in self:
            if move.move_line_ids:
                if move.sale_line_id and move.sale_line_id.lot_ids:
                    move.move_line_ids.unlink()
                    for lot_id in move.sale_line_id.lot_ids:
                        vals = {
                                'move_id': move.id,
                                'product_id': move.product_id.id,
                                'product_uom_id': move.product_uom.id,
                                'location_id': move.location_id.id,
                                'location_dest_id': move.location_dest_id.id,
                                'picking_id': move.picking_id.id,
                                'lot_id':lot_id.id,
                                #'product_uom_qty':lot_id.product_qty,
                                'qty_done':lot_id.product_qty
                                }
                        self.env['stock.move.line'].create(vals)
     
    def _action_assign(self):
        res = super(StockMove, self)._action_assign()
        for move in self:
            if not move.assign_lot:
                move.create_stock_move_line()
                move.assign_lot = True
        return res
    
    
#     @api.model
#     def create(self, vals):
#         if vals.get('sale_line_id'):
#             sale_line_id = self.env['sale.order.line'].browse(vals['sale_line_id'])
#             if sale_line_id and sale_line_id.lot_id:
#                 vals.update({'lot_id': sale_line_id.lot_id.id})
#         return super(StockMove, self).create(vals)
# 
#     @api.multi
#     def write(self,vals):
#         res = super(StockMove, self).write(vals)
#         for rec in self:
#             if rec.sale_line_id and rec.picking_id and rec.lot_id and rec.move_line_ids and sum(rec.move_line_ids.mapped('qty_done')) == 0.0:
#                 for line in rec.move_line_ids:
#                     line.lot_id = rec.lot_id.id
#                     line.qty_done = rec.product_uom_qty
#         return res
