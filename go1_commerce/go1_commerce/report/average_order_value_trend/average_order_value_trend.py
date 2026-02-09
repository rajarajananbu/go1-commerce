# Copyright (c) 2024, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Count, Function

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart

def get_columns():
	return [
		_("Month") + ":Data:120",
		_("Total Orders") + ":Int:120",
		_("Total Revenue") + ":Currency:150",
		_("Avg Order Value") + ":Currency:150",
	]

def get_data(filters):
	OrderDT = DocType("Order")
	year = int(filters.get("year")) if filters.get("year") else frappe.utils.getdate().year

	month_list = ["January", "February", "March", "April", "May", "June",
				  "July", "August", "September", "October", "November", "December"]

	query = (
		frappe.qb.from_(OrderDT)
		.select(
			Function("MONTHNAME", OrderDT.order_date).as_("month"),
			Function("MONTH", OrderDT.order_date).as_("month_num"),
			Count("*").as_("total_orders"),
			Sum(OrderDT.total_amount).as_("total_revenue"),
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.payment_status == "Paid")
		.where(Function("YEAR", OrderDT.order_date) == year)
		.groupby(Function("MONTH", OrderDT.order_date))
		.orderby(Function("MONTH", OrderDT.order_date))
	)
	raw = query.run(as_dict=True)
	month_data = {r.month: r for r in raw}

	result = []
	for m in month_list:
		r = month_data.get(m)
		if r:
			orders = int(r.total_orders or 0)
			revenue = float(r.total_revenue or 0)
			avg = round(revenue / max(orders, 1), 2)
			result.append([m, orders, revenue, avg])
		else:
			result.append([m, 0, 0, 0])
	return result

def get_chart_data(data):
	if not data:
		return None
	labels = [row[0] for row in data]
	orders = [row[1] for row in data]
	aov = [float(row[3] or 0) for row in data]
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Orders"), "type": "bar", "values": orders},
				{"name": _("Avg Order Value"), "type": "line", "values": aov},
			]
		},
		"type": "axis-mixed",
		"colors": ["#4E79A7", "#E15759"]
	}
