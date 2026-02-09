# Copyright (c) 2013, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType, Field
from frappe.query_builder.functions import Count, Sum, Function

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	chart = get_chart_data(filters)
	return columns, data, None, chart

def get_columns(filters):
	return [
		_("Month") + ":Data:120",
		_("Total Orders") + ":Int:120",
		_("Total Sales") + ":Currency:120",
		_("Payment Method") + ":Data:120",
	]

def get_data(filters):
	OrderDT = DocType('Order')
	conditions = (OrderDT.docstatus == 1) & (OrderDT.payment_status == 'Paid')
	if filters.get('year'):
		conditions = conditions & (Function('YEAR', OrderDT.order_date) == int(filters.get('year')))
	if filters.get('from_date'):
		conditions = conditions & (OrderDT.order_date >= filters.get('from_date'))
	if filters.get('to_date'):
		conditions = conditions & (OrderDT.order_date <= filters.get('to_date'))
	query = (
		frappe.qb.from_(OrderDT)
		.select(
			Function('MONTHNAME', OrderDT.order_date).as_('month'),
			Count(OrderDT.name).as_('total_orders'),
			Sum(OrderDT.total_amount).as_('total_sales'),
			OrderDT.payment_method_name
		)
		.where(conditions)
		.groupby(Function('MONTH', OrderDT.order_date))
		.orderby(Function('MONTH', OrderDT.order_date))
	)
	return query.run(as_list=True)

def get_chart_data(filters):
	OrderDT = DocType('Order')
	month_list = ['January','February','March','April','May','June','July','August','September','October','November','December']
	conditions = (OrderDT.docstatus == 1) & (OrderDT.payment_status == 'Paid')
	if filters.get('year'):
		conditions = conditions & (Function('YEAR', OrderDT.order_date) == int(filters.get('year')))
	if filters.get('from_date'):
		conditions = conditions & (OrderDT.order_date >= filters.get('from_date'))
	if filters.get('to_date'):
		conditions = conditions & (OrderDT.order_date <= filters.get('to_date'))

	query = (
		frappe.qb.from_(OrderDT)
		.select(
			Function('MONTHNAME', OrderDT.order_date).as_('month'),
			Sum(OrderDT.total_amount).as_('total_amount')
		)
		.where(conditions)
		.groupby(Function('MONTH', OrderDT.order_date))
		.orderby(Function('MONTH', OrderDT.order_date))
	)
	data = query.run(as_dict=True)

	month_totals = {row.month: float(row.total_amount or 0) for row in data}
	values = [month_totals.get(m, 0) for m in month_list]

	return {
		"data": {
			"labels": month_list,
			"datasets": [{"name": _("Sales"), "values": values}]
		},
		"type": "bar",
		"colors": ["#4CAF50"]
	}
