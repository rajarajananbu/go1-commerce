# Copyright (c) 2013, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum

def execute(filters=None):
	columns = get_columns()
	data = best_selling(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart

def get_columns():
	return [
		_("Product Id") + ":Link/Product:180",
		_("Product Name") + ":Data:200",
		_("SKU") + ":Data:200",
		_("Sold Qty") + ":Int:180",
	]

def best_selling(filters):
	Product = DocType("Product")
	OrderItem = DocType("Order Item")
	OrderDT = DocType("Order")
	query = (
		frappe.qb.from_(Product)
		.left_join(OrderItem).on(OrderItem.item == Product.name)
		.left_join(OrderDT).on(OrderDT.name == OrderItem.parent)
		.select(
			Product.name,
			Product.item,
			Product.sku,
			Sum(OrderItem.quantity).as_('qty')
		)
		.where(OrderDT.payment_status == "Paid")
		.where(OrderDT.docstatus == 1)
	)
	if filters.get('from_date'):
		query = query.where(OrderDT.order_date >= filters.get('from_date'))
	if filters.get('to_date'):
		query = query.where(OrderDT.order_date <= filters.get('to_date'))
	query = (
		query.groupby(Product.name)
		.having(Sum(OrderItem.quantity) > 0)
		.orderby(Sum(OrderItem.quantity), order=frappe.qb.desc)
	)
	return query.run(as_list=True)

def get_chart_data(data):
	if not data:
		return None

	labels = [row[1] or row[0] for row in data[:20]]
	values = [int(row[3] or 0) for row in data[:20]]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Qty Sold"), "values": values}]
		},
		"type": "bar",
		"colors": ["#FF6F61"]
	}
