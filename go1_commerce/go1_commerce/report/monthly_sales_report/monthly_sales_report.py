# Copyright (c) 2013, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Function, Count, Sum

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(filters)
	return columns, data, None, chart

def get_columns():
	return [
		_("Date") + ":Date:120",
		_("Total Orders") + ":Int:120",
		_("Total Sales") + ":Currency:120",
		_("Payment Method") + ":Data:120",
	]

def get_data(filters):
	OrderDT = DocType('Order')
	query = (
		frappe.qb.from_(OrderDT)
		.select(
			OrderDT.order_date,
			Count(OrderDT.name).as_('count'),
			Sum(OrderDT.total_amount).as_('total_amount'),
			OrderDT.payment_method_name
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.payment_status == 'Paid')
		.where(Function('YEAR', OrderDT.order_date) == int(filters.get('year')))
		.where(Function('MONTHNAME', OrderDT.order_date) == filters.get('month'))
	)
	if filters.get('from_date'):
		query = query.where(OrderDT.order_date >= filters.get('from_date'))
	if filters.get('to_date'):
		query = query.where(OrderDT.order_date <= filters.get('to_date'))
	return query.groupby(OrderDT.order_date).run(as_list=True)

def get_chart_data(filters):
	OrderDT = DocType('Order')
	query = (
		frappe.qb.from_(OrderDT)
		.select(
			OrderDT.order_date,
			Sum(OrderDT.total_amount).as_('total_amount')
		)
		.where(OrderDT.docstatus == 1)
		.where(Function('YEAR', OrderDT.order_date) == int(filters.get('year')))
		.where(Function('MONTHNAME', OrderDT.order_date) == filters.get('month'))
		.groupby(OrderDT.order_date)
		.orderby(OrderDT.order_date)
	)
	data = query.run(as_dict=True)

	labels = [str(row.order_date) for row in data]
	values = [float(row.total_amount or 0) for row in data]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Sales"), "values": values}]
		},
		"type": "bar",
		"colors": ['#428b46']
	}
