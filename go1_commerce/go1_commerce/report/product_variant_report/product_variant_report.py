# Copyright (c) 2023, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.custom import ConstantColumn

def execute(filters=None):
	columns, data = get_columns(), get_datas(filters)
	return columns, data

def get_columns():
	return [
		_("Product ID") + ":Link/Product:100",
		_("Product Name") + ":Data:300",
		_("Variant ID") + ":Data:220",
		_("Variant") + ":Data:350",
		_("SKU") + ":Data:100",
	]

def get_datas(filters):
	Product = DocType('Product')
	VariantCombination = DocType('Product Variant Combination')
	query = (
		frappe.qb.from_(Product)
		.inner_join(VariantCombination)
		.on(Product.name == VariantCombination.parent)
		.select(
			Product.name.as_("product_id"),
			Product.item.as_("product_name"),
			VariantCombination.attribute_id.as_("variant_id"),
			VariantCombination.sku
		)
		.where(Product.has_variants == 1)
		.where(VariantCombination.attribute_id.isnotnull())
		.where(VariantCombination.disabled == 0)
		.where(VariantCombination.show_in_market_place == 1)
	)

	if filters and filters.get('product_id'):
		query = query.where(Product.name == filters.get('product_id'))

	query = query.orderby(Product.creation, order=frappe.qb.desc)

	response = query.run(as_dict=True)
	result = []
	for res in response:
		variant_text = ""
		try:
			from go1_commerce.go1_commerce.v2.product import get_attributes_combination
			combination_txt_resp = get_attributes_combination(res.variant_id)
			if combination_txt_resp:
				variant_text = combination_txt_resp[0].combination_txt if hasattr(combination_txt_resp[0], 'combination_txt') else ""
		except Exception:
			pass
		variant_id_display = (res.variant_id or "").replace("\n", "\\n")
		result.append([res.product_id, res.product_name, variant_id_display, variant_text, res.sku])
	return result
