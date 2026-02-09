# Copyright (c) 2013, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Count

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart

def get_columns():
	return [
		_("Order ID") + ":Link/Order:150",
		_("Order Date") + ":Date:90",
		_("Item ID") + ":Link/Product:140",
		_("Item Name") + ":Data:180",
		_("Customer ID") + ":Link/Customers:120",
		_("Customer Name") + ":Data:120",
		_("Customer Email") + ":Data:180",
		_("Customer Phone") + ":Data:100",
		_("Price") + ":Currency:140",
		_("Quantity") + ":Int:140",
	]

def get_data(filters):
	OrderDT = DocType('Order')
	OrderItem = DocType('Order Item')

	query = (
		frappe.qb.from_(OrderDT)
		.inner_join(OrderItem).on(OrderDT.name == OrderItem.parent)
		.select(
			OrderDT.name,
			OrderDT.order_date,
			OrderItem.item,
			OrderItem.item_name,
			OrderDT.customer,
			OrderDT.customer_name,
			OrderDT.customer_email,
			OrderDT.phone,
			OrderItem.price,
			OrderItem.quantity
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.payment_status == 'Paid')
	)
	if filters.get('from_date'):
		query = query.where(OrderDT.order_date >= filters.get('from_date'))
	if filters.get('to_date'):
		query = query.where(OrderDT.order_date <= filters.get('to_date'))
	query = query.orderby(OrderDT.order_date, order=frappe.qb.desc)
	return query.run(as_list=True)

def get_chart_data(data):
	if not data:
		return None

	item_totals = {}
	for row in data:
		item_name = row[3] or row[2]
		qty = int(row[9] or 0)
		item_totals[item_name] = item_totals.get(item_name, 0) + qty

	sorted_items = sorted(item_totals.items(), key=lambda x: x[1], reverse=True)[:15]
	labels = [item[0] for item in sorted_items]
	values = [item[1] for item in sorted_items]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Quantity Sold"), "values": values}]
		},
		"type": "bar",
		"colors": ["#7B68EE"]
	}
