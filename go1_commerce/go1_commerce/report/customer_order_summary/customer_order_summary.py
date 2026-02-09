# Copyright (c) 2023, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count, Sum

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart

def get_columns():
	return [
		_("Customer Id") + ":Link/Customers:200",
		_("Customer Name") + ":Data:200",
		_("Customer Email") + ":Data:250",
		_("Customer Phone No") + ":Phone:200",
		_("Total Order Count") + ":Int:150",
		_("Total Amount") + ":Currency:120",
	]

def get_data(filters):
	CustomerDT = DocType('Customers')
	OrderDT = DocType('Order')
	query = (
		frappe.qb.from_(CustomerDT)
		.left_join(OrderDT).on(
			(OrderDT.customer == CustomerDT.name) &
			(OrderDT.docstatus == 1)
		)
		.select(
			CustomerDT.name,
			CustomerDT.full_name,
			CustomerDT.email,
			CustomerDT.phone,
			Count(OrderDT.name).as_("total_order_count"),
			Sum(OrderDT.total_amount).as_("total_amount")
		)
		.where(CustomerDT.customer_status == 'Approved')
	)
	if filters.get('from_date'):
		query = query.where(OrderDT.order_date >= filters.get('from_date'))
	if filters.get('to_date'):
		query = query.where(OrderDT.order_date <= filters.get('to_date'))
	query = query.groupby(CustomerDT.name)
	query = query.having(Count(OrderDT.name) > 0)
	query = query.orderby(Count(OrderDT.name), order=frappe.qb.desc)
	return query.run(as_list=True)

def get_chart_data(data):
	if not data:
		return None

	labels = [row[1] or row[0] for row in data[:20]]
	values = [float(row[5] or 0) for row in data[:20]]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Total Spend"), "values": values}]
		},
		"type": "bar",
		"colors": ["#36A2EB"]
	}
