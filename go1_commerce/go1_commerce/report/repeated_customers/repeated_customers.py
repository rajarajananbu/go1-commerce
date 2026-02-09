# Copyright (c) 2013, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart

def get_columns():
	return [
		_("Customer Name") + ":Data:200",
		_("Customer Email") + ":Data:250",
		_("No.Of Orders Placed") + ":Int:200",
	]

def get_data(filters):
	OrderDT = DocType('Order')
	query = (
		frappe.qb.from_(OrderDT)
		.select(
			OrderDT.customer_name,
			OrderDT.customer_email,
			Count('*').as_('order_count')
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.status != 'Cancelled')
	)
	if filters.get('from_date'):
		query = query.where(OrderDT.order_date >= filters.get('from_date'))
	if filters.get('to_date'):
		query = query.where(OrderDT.order_date <= filters.get('to_date'))
	query = (
		query
		.groupby(OrderDT.customer_name, OrderDT.customer_email)
		.having(Count('*') > 1)
		.orderby(Count('*'), order=frappe.qb.desc)
	)
	return query.run(as_list=True)

def get_chart_data(data):
	if not data:
		return None

	labels = [row[0] or row[1] for row in data[:20]]
	values = [int(row[2] or 0) for row in data[:20]]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Orders"), "values": values}]
		},
		"type": "bar",
		"colors": ["#5B8FF9"]
	}
