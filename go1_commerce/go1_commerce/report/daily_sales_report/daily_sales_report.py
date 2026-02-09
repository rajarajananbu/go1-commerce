# Copyright (c) 2013, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	chart = get_chart_data(filters)
	return columns, data, None, chart

def get_columns(filters):
	return [
		_("Order Id") + ":Link/Order:120",
		_("Order Date") + ":Date:120",
		_("Order Status") + ":Data:120",
		_("Payment Status") + ":Data:120",
		_("Payment Method") + ":Data:120",
		_("Customer Name") + ":Data:180",
		_("Customer Email") + ":Data:180",
		_("Customer Phone") + ":Data:140",
		_("Order Total") + ":Currency:120",
	]

def get_data(filters):
	OrderDT = DocType("Order")
	query = (
		frappe.qb.from_(OrderDT)
		.select(
			OrderDT.name,
			OrderDT.order_date,
			OrderDT.status,
			OrderDT.payment_status,
			OrderDT.payment_method_name,
			OrderDT.customer_name,
			OrderDT.customer_email,
			OrderDT.phone,
			OrderDT.total_amount
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.order_date == filters.get('date'))
	)
	return query.run(as_list=True)

def get_chart_data(filters):
	OrderDT = DocType("Order")
	query = (
		frappe.qb.from_(OrderDT)
		.select(
			OrderDT.name,
			OrderDT.total_amount
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.order_date == filters.get('date'))
		.orderby(OrderDT.creation)
	)
	data = query.run(as_list=True)
	if not data:
		return None

	labels = [row[0] for row in data]
	values = [float(row[1] or 0) for row in data]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Order Total"), "values": values}]
		},
		"type": "bar"
	}
