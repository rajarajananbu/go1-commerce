# Copyright (c) 2013, sivaranjani and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count

def execute(filters=None):
	columns = get_columns()
	data = products_report(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart

def get_columns():
	return [
		_("Vendor Name") + ":Link/Business:180",
		_("Product") + ":Data:200",
		_("Quantity") + ":Int:120",
	]

def products_report(filters):
	Product = DocType('Product')
	OrderItem = DocType('Order Item')
	OrderDT = DocType('Order')
	query = (
		frappe.qb.from_(Product)
		.left_join(OrderItem).on(
			(OrderItem.item == Product.name) &
			(OrderItem.parenttype == "Order")
		)
		.left_join(OrderDT).on(OrderItem.parent == OrderDT.name)
		.select(
			Product.restaurant,
			Product.item,
			Count(OrderItem.name).as_("qty")
		)
		.where(OrderDT.docstatus == 1)
		.groupby(Product.name)
		.having(Count(OrderItem.name) > 0)
		.orderby(Count(OrderItem.name), order=frappe.qb.desc)
	)
	return query.run(as_list=True)

def get_chart_data(data):
	if not data:
		return None

	labels = [row[1] for row in data[:15]]
	values = [int(row[2] or 0) for row in data[:15]]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Order Count"), "values": values}]
		},
		"type": "bar",
		"colors": ["#6C5CE7"]
	}
