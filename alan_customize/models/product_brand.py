# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

# class SalesOrderLine(models.Model):
#     _inherit = 'sale.order.line'
    
#     website_lot_info = fields.Char(string="Website CTR Lot information")

class SalesOrder(models.Model):
    _inherit = 'sale.order'

    def get_lot_info(self, product_id, quantity):
        st = "Approx. 16-20 Weeks"
        lots = self.env['x_ctr_lot'].sudo().search([('x_product_id','=',product_id.id)])
        # product = self.env['product.product'].sudo().browse(product_id)
        # _logger.warning("TEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEST" + str(product_id))
        qty = product_id.sudo().qty_available
        lot_date = False
        lot_name = False

        if qty > quantity:
            st = "In Stock"
        else:
            for lot in lots:
                if not lot.x_lot_id:
                    # CTR Lot initial demand - CTR reserved QTY
                    remaining = lot.x_studio_reserved_qty - lot.x_studio_ctr_reserved_qty
                    if remaining > 0:
                        # Compare
                        qty += remaining
                        _logger.warning("Lot Name: " + str(lot.x_name))
                        _logger.warning("Remaining: " + str(remaining))
                        if qty >= quantity:
                            lot_date = lot.x_studio_receipt_scheduled_date
                            lot_name = lot.x_name
                            break

        if lot_date and lot_name:
            lot_date = str(lot_date).split(' ')[0]
            year,month,date = str(lot_date).split('-')

            # Day
            if int(date) < 11:
                date = " Early"
            elif int(date) < 20:
                date = " Mid"
            elif int(date) < 32:
                date = " Late"

            # Month
            if month == '01':
                month = "January"
            elif month == "02" :
                month = "February"
            elif month == "03":
                month = "March"
            elif month == "04":
                month = "April"
            elif month == "05":
                month = "May"
            elif month == "06":
                month = "June"
            elif month == "07":
                month = "July"
            elif month == "08":
                month = "August"
            elif month == "09":
                month = "September"
            elif month == "10":
                month = "October"
            elif month == "11":
                month = "November"
            elif month == "12":
                month = "December"

            st = lot_name + " - Estimated Arrival: " + date + " " + month

        return st

    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        """ Add or set product quantity, add_qty can be negative """
        self.ensure_one()
        product_context = dict(self.env.context)
        product_context.setdefault('lang', self.sudo().partner_id.lang)
        SaleOrderLineSudo = self.env['sale.order.line'].sudo().with_context(product_context)

        try:
            if add_qty:
                add_qty = int(add_qty)
        except ValueError:
            add_qty = 1
        try:
            if set_qty:
                set_qty = int(set_qty)
        except ValueError:
            set_qty = 0
        quantity = 0
        order_line = False
        if self.state != 'draft':
            request.session['sale_order_id'] = None
            raise UserError(_('It is forbidden to modify a sales order which is not in draft status.'))
        if line_id is not False:
            order_line = self._cart_find_product_line(product_id, line_id, **kwargs)[:1]

        # Create line if no line with product_id can be located
        if not order_line:
            # change lang to get correct name of attributes/values
            product = self.env['product.product'].with_context(product_context).browse(int(product_id))

            if not product:
                raise UserError(_("The given product does not exist therefore it cannot be added to cart."))

            no_variant_attribute_values = kwargs.get('no_variant_attribute_values') or []
            received_no_variant_values = product.env['product.template.attribute.value'].browse([int(ptav['value']) for ptav in no_variant_attribute_values])
            received_combination = product.product_template_attribute_value_ids | received_no_variant_values
            product_template = product.product_tmpl_id

            # handle all cases where incorrect or incomplete data are received
            combination = product_template._get_closest_possible_combination(received_combination)

            # get or create (if dynamic) the correct variant
            product = product_template._create_product_variant(combination)

            if not product:
                raise UserError(_("The given combination does not exist therefore it cannot be added to cart."))

            product_id = product.id

            values = self._website_product_id_change(self.id, product_id, qty=1)

            # add no_variant attributes that were not received
            for ptav in combination.filtered(lambda ptav: ptav.attribute_id.create_variant == 'no_variant' and ptav not in received_no_variant_values):
                no_variant_attribute_values.append({
                    'value': ptav.id,
                    'attribute_name': ptav.attribute_id.name,
                    'attribute_value_name': ptav.name,
                })

            # save no_variant attributes values
            if no_variant_attribute_values:
                values['product_no_variant_attribute_value_ids'] = [
                    (6, 0, [int(attribute['value']) for attribute in no_variant_attribute_values])
                ]

            # add is_custom attribute values that were not received
            custom_values = kwargs.get('product_custom_attribute_values') or []
            received_custom_values = product.env['product.attribute.value'].browse([int(ptav['attribute_value_id']) for ptav in custom_values])

            for ptav in combination.filtered(lambda ptav: ptav.is_custom and ptav.product_attribute_value_id not in received_custom_values):
                custom_values.append({
                    'attribute_value_id': ptav.product_attribute_value_id.id,
                    'attribute_value_name': ptav.name,
                    'custom_value': '',
                })

            # save is_custom attributes values
            if custom_values:
                values['product_custom_attribute_value_ids'] = [(0, 0, {
                    'attribute_value_id': custom_value['attribute_value_id'],
                    'custom_value': custom_value['custom_value']
                }) for custom_value in custom_values]

            # create the line
            order_line = SaleOrderLineSudo.create(values)
            # Generate the description with everything. This is done after
            # creating because the following related fields have to be set:
            # - product_no_variant_attribute_value_ids
            # - product_custom_attribute_value_ids
            order_line.name = order_line.get_sale_order_line_multiline_description_sale(product)

            try:
                order_line._compute_tax_id()
            except ValidationError as e:
                # The validation may occur in backend (eg: taxcloud) but should fail silently in frontend
                _logger.debug("ValidationError occurs during tax compute. %s" % (e))
            if add_qty:
                add_qty -= 1

        

        # compute new quantity
        if set_qty:
            quantity = set_qty
        elif add_qty is not None:
            quantity = order_line.product_uom_qty + (add_qty or 0)

        # Remove zero of negative lines
        if quantity <= 0:
            order_line.unlink()
        else:
            # update line
            no_variant_attributes_price_extra = [ptav.price_extra for ptav in order_line.product_no_variant_attribute_value_ids]
            values = self.with_context(no_variant_attributes_price_extra=no_variant_attributes_price_extra)._website_product_id_change(self.id, product_id, qty=quantity)
            if self.pricelist_id.discount_policy == 'with_discount' and not self.env.context.get('fixed_price'):
                order = self.sudo().browse(self.id)
                product_context.update({
                    'partner': order.partner_id,
                    'quantity': quantity,
                    'date': order.date_order,
                    'pricelist': order.pricelist_id.id,
                    'force_company': order.company_id.id,
                })
            product = self.env['product.product'].with_context(product_context).browse(product_id)
            values['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                order_line._get_display_price(product),
                order_line.product_id.taxes_id,
                order_line.tax_id,
                self.company_id
            )

            # Added by Captivea, the rest is base Odoo - 05/07/2021 - BEGIN

            # _logger.warning("++++++++++++++++++++++++ ENTERED HERE ++++++++++++++++++++++++")
            # if kwargs.get('lot_info'):
            #     values['website_lot_info'] = self.get_lot_info(product_id=product, quantity=quantity)

            # Added by Captivea - 05/07/2021 - END

            order_line.write(values)

            # link a product to the sales order
            if kwargs.get('linked_line_id'):
                linked_line = SaleOrderLineSudo.browse(kwargs['linked_line_id'])
                order_line.write({
                    'linked_line_id': linked_line.id,
                    'name': order_line.name + "\n" + _("Option for:") + ' ' + linked_line.product_id.display_name,
                })
                linked_line.write({"name": linked_line.name + "\n" + _("Option:") + ' ' + order_line.product_id.display_name})

        option_lines = self.order_line.filtered(lambda l: l.linked_line_id.id == order_line.id)
        for option_line_id in option_lines:
            self._cart_update(option_line_id.product_id.id, option_line_id.id, add_qty, set_qty, **kwargs)

        return {'line_id': order_line.id, 'quantity': quantity, 'option_ids': list(set(option_lines.ids))}

class ProductBrand(models.Model):
    _name = 'product.brand'
    _inherit = ['website.multi.mixin']
    _description = 'Product brands'


    name = fields.Char('Brand Name', required=True)
    logo = fields.Binary('Logo File')
    sequence = fields.Integer(string="Sequence")
    product_ids = fields.One2many(
        'product.template',
        'product_brand_id',
        string='Brand Products',
    )
    products_count = fields.Integer(
        string='Number of products',
        compute='_get_products_count',
    )
    visible_slider=fields.Boolean("Visible in Website",default=True)
    active=fields.Boolean("Active",default=True)

    @api.one
    @api.depends('product_ids')
    def _get_products_count(self):
        self.products_count = len(self.product_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_brand_id = fields.Many2one(
        'product.brand',
        string='Brand',
        help='Select a brand for this product'
    )
    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        # _logger.info('Launched!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n' + str(parent_combination))
        self.ensure_one()
        # get the name before the change of context to benefit from prefetch
        display_name = self.name

        quantity = self.env.context.get('quantity', add_qty)
        context = dict(self.env.context, quantity=quantity, pricelist=pricelist.id if pricelist else False)
        product_template = self.with_context(context)

        combination = combination or product_template.env['product.template.attribute.value']

        if not product_id and not combination and not only_template:
            combination = product_template._get_first_possible_combination(parent_combination)

        if only_template:
            product = product_template.env['product.product']
        elif product_id and not combination:
            product = product_template.env['product.product'].browse(product_id)
        else:
            product = product_template._get_variant_for_combination(combination)

        if product:
            # We need to add the price_extra for the attributes that are not
            # in the variant, typically those of type no_variant, but it is
            # possible that a no_variant attribute is still in a variant if
            # the type of the attribute has been changed after creation.
            no_variant_attributes_price_extra = [
                ptav.price_extra for ptav in combination.filtered(
                    lambda ptav:
                        ptav.price_extra and
                        ptav not in product.product_template_attribute_value_ids
                )
            ]
            if no_variant_attributes_price_extra:
                product = product.with_context(
                    no_variant_attributes_price_extra=no_variant_attributes_price_extra
                )
            list_price = product.price_compute('list_price')[product.id]
            price = product.price if pricelist else list_price
        else:
            product_template = product_template.with_context(current_attributes_price_extra=[v.price_extra or 0.0 for v in combination])
            list_price = product_template.price_compute('list_price')[product_template.id]
            price = product_template.price if pricelist else list_price

        filtered_combination = combination._without_no_variant_attributes()
        filtered_false = False
        for f in filtered_combination.mapped('name'):
            if f == False:
                filtered_false = True
        if filtered_combination:
            if display_name != False and filtered_combination != False and filtered_combination[0] != False and filtered_false == False:
                # _logger.info('___________________-Filtered: ' + str(filtered_combination.mapped('name')[0]) + " _____ " + str(filtered_combination[0]))

                display_name = '%s (%s)' % (display_name, ', '.join(filtered_combination.mapped('name')))
            else:
                return {
                    'product_id': False,
                    'product_template_id': product_template.id,
                    'display_name': "",
                    'virtual_available': "",
                    'price': False,
                    'list_price': False,
                    'has_discounted_price': False,
                    'custom_message': "",
                }
        if pricelist and pricelist.currency_id != product_template.currency_id:
            list_price = product_template.currency_id._convert(
                list_price, pricelist.currency_id, product_template._get_current_company(pricelist=pricelist),
                fields.Date.today()
            )

        price_without_discount = list_price if pricelist and pricelist.discount_policy == 'without_discount' else price
        has_discounted_price = (pricelist or product_template).currency_id.compare_amounts(price_without_discount, price) == 1

        if product.custom_message and product.custom_message != "":
            st = product.custom_message
        else:
            st = "Approx. 16-20 Weeks"
        # if product.x_studio_availability != False:
        #     st = str(product.x_studio_availability)
        #     if product.virtual_available > 0:
        #         st += " ( " + str(int(product.virtual_available)) + " available )"

        # Here is where we do our checks on CTR Lots
        lots = self.env['x_ctr_lot'].sudo().search([('x_product_id','=',product.id)])
        qty = product.qty_available
        lot_date = False
        lot_name = False
        for lot in lots:
            if not lot.x_lot_id:
                            # CTR Lot initial demand - CTR reserved QTY
                remaining = lot.x_studio_reserved_qty - lot.x_studio_ctr_reserved_qty

                if remaining > 0:
                    # Compare
                    qty += remaining
                    _logger.warning("Lot Name: " + str(lot.x_name))
                    _logger.warning("Remaining: " + str(remaining))
                    if qty >= quantity:
                        lot_date = lot.x_studio_receipt_scheduled_date
                        lot_name = lot.x_name
                        break

        if lot_date:
            lot_date = str(lot_date).split(' ')[0]
            year,month,date = str(lot_date).split('-')

            # Day
            if int(date) < 11:
                date = " Early"
            elif int(date) < 20:
                date = " Mid"
            elif int(date) < 32:
                date = " Late"

            # Month
            if month == '01':
                month = "January"
            elif month == "02" :
                month = "February"
            elif month == "03":
                month = "March"
            elif month == "04":
                month = "April"
            elif month == "05":
                month = "May"
            elif month == "06":
                month = "June"
            elif month == "07":
                month = "July"
            elif month == "08":
                month = "August"
            elif month == "09":
                month = "September"
            elif month == "10":
                month = "October"
            elif month == "11":
                month = "November"
            elif month == "12":
                month = "December"

            st = "Estimated Arrival: " + date + " " + month

        # _logger.warning("Here")

        return {
            'product_id': product.id,
            'product_template_id': product_template.id,
            'virtual_available': product.qty_available - quantity + 1,
            'display_name': display_name,
            'price': price,
            'list_price': list_price,
            'has_discounted_price': has_discounted_price,
            'custom_message': st,
        }
