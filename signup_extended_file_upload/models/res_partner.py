# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    tax_certificate = fields.Binary("Tax Certificate")
    filename = fields.Char("Filename")
    comments = fields.Text("Comments")
    account_type = fields.Selection([('hospitality', 'Hospitality - Commercial Design'),
                                    ('stocking_dealer', 'Stocking Dealer - $2,500 Opening Order - ($2,500 Yearly) - Save 30% over wholesale'),
                                    ('wholesale_account', 'Wholesale Account - No Minium Order - (No Commitment)')],
                                    string='Account Type')

    business_type = fields.Selection([('retail_furniture_store', 'Retail Furniture Store'),
                                    ('interior_design_pro', 'Interior Design Professionals'),
                                    ('architects_builders', 'Architects / Builders'),
                                    ('e_commerce_store', 'E-commerce Store: Furniture / Interior Design'),
                                    ('hospitality', 'Hospitality')],
                                    string='Trade Business Type')
