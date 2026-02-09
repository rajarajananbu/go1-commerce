# Copyright (c) 2013, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType

def execute(filters=None):
	columns = get_columns()
	data = products_never_purchased(filters)
	return columns, data

def get_columns():
	return [
		_("Product Id") + ":Link/Product:180",
		_("Product Name") + ":Data:250",
	]

def products_never_purchased(filters):
	Product = DocType('Product')
	OrderItem = DocType('Order Item')
	subquery = (
		frappe.qb.from_(OrderItem)
		.select(OrderItem.item)
		.where(OrderItem.parenttype == 'Order')
		.distinct()
	)
	products_query = (
		frappe.qb.from_(Product)
		.select(Product.name, Product.item)
		.where(
			(Product.is_active == 1) &
			(Product.status == 'Approved') &
			(Product.name.notin(subquery))
		)
		.orderby(Product.item)
	)
	return products_query.run(as_list=True)
