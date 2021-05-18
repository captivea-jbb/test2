#  -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class Transfer(models.Model):
    _inherit = 'stock.picking'

    state_delivery = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'In Stock'),
        ('done', 'Print Docs'),
        ('completed', 'Completed'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed.\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows).\n"
             " * Waiting: if it is not ready to be sent because the required products could not be reserved.\n"
             " * Ready: products are reserved and ready to be sent. If the shipping policy is 'As soon as possible' this happens as soon as anything is reserved.\n"
             " * Done: has been processed, can't be modified or cancelled anymore.\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore.")

class CTRLotNumber(models.Model):
    _name= 'x_ctr_lot'

    def name_search(self):
        _logger.warning('Start')
        res = []
        for lot in self:

            remaining = lot.x_studio_reserved_qty - lot.x_studio_ctr_reserved_qty

            name = str(lot.x_name) + " (" + str(remaining) + " remaining)"

            res.append((lot.id, name))

        return res


# class ProductTemplate(models.Model):
#     _inherit = 'product.template'

#     test_field = fields.Boolean("TEST",default=True)

#     @api.multi
#     def _get_combination_info_jb(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
#         """ Return info about a given combination.
#         Note: this method does not take into account whether the combination is
#         actually possible.
#         :param combination: recordset of `product.template.attribute.value`
#         :param product_id: id of a `product.product`. If no `combination`
#             is set, the method will try to load the variant `product_id` if
#             it exists instead of finding a variant based on the combination.
#             If there is no combination, that means we definitely want a
#             variant and not something that will have no_variant set.
#         :param add_qty: float with the quantity for which to get the info,
#             indeed some pricelist rules might depend on it.
#         :param pricelist: `product.pricelist` the pricelist to use
#             (can be none, eg. from SO if no partner and no pricelist selected)
#         :param parent_combination: if no combination and no product_id are
#             given, it will try to find the first possible combination, taking
#             into account parent_combination (if set) for the exclusion rules.
#         :param only_template: boolean, if set to True, get the info for the
#             template only: ignore combination and don't try to find variant
#         :return: dict with product/combination info:
#             - product_id: the variant id matching the combination (if it exists)
#             - product_template_id: the current template id
#             - display_name: the name of the combination
#             - price: the computed price of the combination, take the catalog
#                 price if no pricelist is given
#             - list_price: the catalog price of the combination, but this is
#                 not the "real" list_price, it has price_extra included (so
#                 it's actually more closely related to `lst_price`), and it
#                 is converted to the pricelist currency (if given)
#             - has_discounted_price: True if the pricelist discount policy says
#                 the price does not include the discount and there is actually a
#                 discount applied (price < list_price), else False
#         """
#         _logger.debug('Launched!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n' + str(combination))
#         self.ensure_one()
#         # get the name before the change of context to benefit from prefetch
#         display_name = self.name

#         quantity = self.env.context.get('quantity', add_qty)
#         context = dict(self.env.context, quantity=quantity, pricelist=pricelist.id if pricelist else False)
#         product_template = self.with_context(context)

#         combination = combination or product_template.env['product.template.attribute.value']

#         if not product_id and not combination and not only_template:
#             combination = product_template._get_first_possible_combination(parent_combination)

#         if only_template:
#             product = product_template.env['product.product']
#         elif product_id and not combination:
#             product = product_template.env['product.product'].browse(product_id)
#         else:
#             product = product_template._get_variant_for_combination(combination)

#         if product:
#             # We need to add the price_extra for the attributes that are not
#             # in the variant, typically those of type no_variant, but it is
#             # possible that a no_variant attribute is still in a variant if
#             # the type of the attribute has been changed after creation.
#             no_variant_attributes_price_extra = [
#                 ptav.price_extra for ptav in combination.filtered(
#                     lambda ptav:
#                         ptav.price_extra and
#                         ptav not in product.product_template_attribute_value_ids
#                 )
#             ]
#             if no_variant_attributes_price_extra:
#                 product = product.with_context(
#                     no_variant_attributes_price_extra=no_variant_attributes_price_extra
#                 )
#             list_price = product.price_compute('list_price')[product.id]
#             price = product.price if pricelist else list_price
#         else:
#             product_template = product_template.with_context(current_attributes_price_extra=[v.price_extra or 0.0 for v in combination])
#             list_price = product_template.price_compute('list_price')[product_template.id]
#             price = product_template.price if pricelist else list_price

#         filtered_combination = combination._without_no_variant_attributes()
#         if filtered_combination:
#             if display_name != False:
#                  _logger.debug('Display Name' + str(display_name))
#                 display_name = '%s (%s)' % (display_name, ', '.join(filtered_combination.mapped('name')))
#             else:
#                 return {
#                     'product_id': False,
#                     'product_template_id': product_template.id,
#                     'display_name': "",
#                     'price': False,
#                     'list_price': False,
#                     'has_discounted_price': False,
#                 }
#         if pricelist and pricelist.currency_id != product_template.currency_id:
#             list_price = product_template.currency_id._convert(
#                 list_price, pricelist.currency_id, product_template._get_current_company(pricelist=pricelist),
#                 fields.Date.today()
#             )

#         price_without_discount = list_price if pricelist and pricelist.discount_policy == 'without_discount' else price
#         has_discounted_price = (pricelist or product_template).currency_id.compare_amounts(price_without_discount, price) == 1

#         return {
#             'product_id': product.id,
#             'product_template_id': product_template.id,
#             'display_name': display_name,
#             'price': price,
#             'list_price': list_price,
#             'has_discounted_price': has_discounted_price,
#         }
