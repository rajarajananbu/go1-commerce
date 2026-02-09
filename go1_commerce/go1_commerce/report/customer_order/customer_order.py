# Copyright (c) 2013, sivaranjani and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType, Field
from frappe.query_builder.functions import Sum

def execute(filters=None):
	columns, data = [], []
	if not filters: filters = {}
	columns = get_columns()
	data = customer_report(filters)
	chart = get_chart_data(filters)
	return columns, data, None, chart

def get_columns():
	return [
		_("Order Number") + ":Link/Order:120",
		_("Order Date") + ":Date:120",
		_("Order Status") + ":Data:120",
		_("Payment Status") + ":Data:120",
		_("Customer Name") + ":Data:180",
		_("Customer Email") + ":Data:180",
		_("Customer Phone") + ":Data:140",
		_("Total Amount") + ":Currency:120",
		_("Order From") + ":Data:120",
	]

def customer_report(filters):
	OrderDT = DocType('Order')
	query = (
		frappe.qb.from_(OrderDT)
		.select(
			OrderDT.name,
			OrderDT.order_date,
			OrderDT.status,
			OrderDT.payment_status,
			OrderDT.customer_name,
			OrderDT.customer_email,
			OrderDT.phone,
			OrderDT.total_amount,
			OrderDT.order_from
		)
		.where(OrderDT.naming_series != "SUB-ORD-")
		.where(OrderDT.docstatus == 1)
	)
	if filters.get('from_date'):
		query = query.where(OrderDT.order_date >= filters.get('from_date'))
	if filters.get('to_date'):
		query = query.where(OrderDT.order_date <= filters.get('to_date'))
	if filters.get('status'):
		query = query.where(OrderDT.status == filters.get('status'))
	if filters.get('payment_status'):
		query = query.where(OrderDT.payment_status == filters.get('payment_status'))
	if filters.get('order_from'):
		query = query.where(OrderDT.order_from == filters.get('order_from'))
	return query.run(as_list=True)

def get_chart_data(filters):
	OrderDT = DocType('Order')
	query = (
		frappe.qb.from_(OrderDT)
		.select(
			OrderDT.order_date,
			Sum(OrderDT.total_amount).as_('total')
		)
		.where(OrderDT.naming_series != "SUB-ORD-")
		.where(OrderDT.docstatus == 1)
		.groupby(OrderDT.order_date)
		.orderby(OrderDT.order_date)
	)
	if filters.get('from_date'):
		query = query.where(OrderDT.order_date >= filters.get('from_date'))
	if filters.get('to_date'):
		query = query.where(OrderDT.order_date <= filters.get('to_date'))
	if filters.get('status'):
		query = query.where(OrderDT.status == filters.get('status'))
	if filters.get('payment_status'):
		query = query.where(OrderDT.payment_status == filters.get('payment_status'))

	data = query.run(as_dict=True)
	if not data:
		return None

	labels = [str(row.order_date) for row in data]
	values = [float(row.total or 0) for row in data]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Order Total"), "values": values}]
		},
		"type": "line"
	}
