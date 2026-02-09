# Copyright (c) 2013, sivaranjani and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate
from datetime import datetime, timedelta
from frappe.query_builder import DocType, Field
from frappe.query_builder.functions import Function, Count

def execute(filters=None):
	columns, data = [], []
	if not filters: filters = {}
	columns = get_columns()
	data = get_values(filters)
	chart = get_chart_data(filters)
	return columns, data, None, chart

def get_columns():
	return [
		_("Order Number") + ":Link/Order:120",
		_("Order Date") + ":Date:120",
		_("Order Status") + ":Data:120",
		_("Payment Status") + ":Data:120",
		_("Customer Name") + ":Data:180",
		_("Sub Total") + ":Currency:120",
		_("Shipping Charge") + ":Currency:120",
		_("Tax Amount") + ":Currency:120",
		_("Total Amount") + ":Currency:120",
	]

def get_values(filters):
	OrderDT = DocType('Order')
	query = (
		frappe.qb.from_(OrderDT)
		.select(
			OrderDT.name,
			OrderDT.order_date,
			OrderDT.status,
			OrderDT.payment_status,
			OrderDT.customer_name,
			OrderDT.order_subtotal,
			OrderDT.shipping_charges,
			OrderDT.total_tax_amount,
			OrderDT.total_amount
		)
		.where(OrderDT.naming_series != "SUB-ORD-")
		.where(OrderDT.docstatus == 1)
	)
	if filters.get('from_date'):
		query = query.where(OrderDT.order_date >= filters.get('from_date'))
	if filters.get('to_date'):
		query = query.where(OrderDT.order_date <= filters.get('to_date'))
	if filters.get('restaurant'):
		query = query.where(OrderDT.business == filters.get('restaurant'))
	if filters.get('status'):
		query = query.where(OrderDT.status == filters.get('status'))
	if filters.get('payment_status'):
		query = query.where(OrderDT.payment_status == filters.get('payment_status'))
	return query.run(as_list=True)

def get_chart_data(filters):
	status = filters.get('status') if filters.get('status') else None
	months = ['January','February','March','April','May','June','July','August','September','October','November','December']
	year = int(filters.get('year')) if filters.get('year') else getdate().year
	month = filters.get('month') if filters.get('month') else None

	if month:
		month_num = datetime.strptime(month, '%B').month
		import calendar
		num_days = calendar.monthrange(year, month_num)[1]
		labels = [str(d) for d in range(1, num_days + 1)]
	else:
		labels = months

	datasets = []
	if status:
		datasets.append({
			"name": status,
			"values": get_order_counts(status, year, month, labels)
		})
	else:
		for s in ['Completed', 'Placed', 'Processing', 'Cancelled']:
			datasets.append({
				"name": s,
				"values": get_order_counts(s, year, month, labels)
			})

	return {
		"data": {
			'labels': labels,
			'datasets': datasets
		},
		"type": "line"
	}

def get_order_counts(status, year, month, labels):
	OrderDT = DocType('Order')
	values = []

	if month:
		month_num = datetime.strptime(month, '%B').month
		for day_str in labels:
			day_date = datetime(year=year, month=month_num, day=int(day_str)).date()
			query = (
				frappe.qb.from_(OrderDT)
				.select(Count("*").as_("count"))
				.where(OrderDT.naming_series != "SUB-ORD-")
				.where(OrderDT.status == status)
				.where(OrderDT.docstatus == 1)
				.where(OrderDT.order_date == day_date)
			)
			data = query.run(as_list=True)
			values.append(data[0][0] if data else 0)
	else:
		for month_name in labels:
			month_num = datetime.strptime(month_name, '%B').month
			import calendar
			num_days = calendar.monthrange(year, month_num)[1]
			st_date = datetime(year=year, month=month_num, day=1).date()
			ed_date = datetime(year=year, month=month_num, day=num_days).date()

			query = (
				frappe.qb.from_(OrderDT)
				.select(Count("*").as_("count"))
				.where(OrderDT.naming_series != "SUB-ORD-")
				.where(OrderDT.status == status)
				.where(OrderDT.docstatus == 1)
				.where(OrderDT.order_date >= st_date)
				.where(OrderDT.order_date <= ed_date)
			)
			data = query.run(as_list=True)
			values.append(data[0][0] if data else 0)

	return values

@frappe.whitelist()
def get_years():
	OrderDT = DocType('Order')
	query = (
		frappe.qb.from_(OrderDT)
		.select(Function('YEAR', OrderDT.order_date).as_('years'))
		.distinct()
		.where(OrderDT.naming_series != "SUB-ORD-")
	)
	year_list = query.run(as_list=True)
	if not year_list:
		year_list = [[getdate().year]]
	return "\n".join(str(y[0]) for y in year_list)
