# Copyright (c) 2013, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart

def get_columns():
	return [
		_("Order ID") + ":Link/Order:150",
		_("Order Status") + ":Data:120",
		_("Payment Status") + ":Data:120",
		_("Customer Name") + ":Data:180",
		_("Order Date") + ":Date:120",
		_("Total Amount") + ":Currency:120",
	]

def get_data(filters):
	OrderDT = DocType("Order")
	OrderDeliverySlot = DocType("Order Delivery Slot")
	query = (
		frappe.qb.from_(OrderDT)
		.inner_join(OrderDeliverySlot).on(OrderDT.name == OrderDeliverySlot.order)
		.select(
			OrderDT.name,
			OrderDT.status,
			OrderDT.payment_status,
			OrderDT.customer_name,
			OrderDT.order_date,
			OrderDT.total_amount
		)
		.where(OrderDT.docstatus == 1)
	)
	if filters.get('date'):
		query = query.where(OrderDT.order_date == filters.get('date'))
	return query.run(as_list=True)

def get_chart_data(data):
	if not data:
		return None

	labels = [row[0] for row in data]
	values = [float(row[5] or 0) for row in data]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Order Amount"), "values": values}]
		},
		"type": "bar"
	}
