# Copyright (c) 2024, Tridots Tech and contributors
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
		_("Channel") + ":Data:200",
		_("Total Orders") + ":Int:120",
		_("Total Revenue") + ":Currency:150",
		_("Avg Order Value") + ":Currency:150",
		_("Percentage") + ":Percent:100",
	]

def get_data(filters):
	OrderDT = DocType("Order")
	query = (
		frappe.qb.from_(OrderDT)
		.select(
			OrderDT.order_from,
			Count("*").as_("total_orders"),
			Sum(OrderDT.total_amount).as_("total_revenue"),
		)
		.where(OrderDT.docstatus == 1)
		.groupby(OrderDT.order_from)
		.orderby(Sum(OrderDT.total_amount), order=frappe.qb.desc)
	)
	if filters.get("from_date"):
		query = query.where(OrderDT.order_date >= filters.get("from_date"))
	if filters.get("to_date"):
		query = query.where(OrderDT.order_date <= filters.get("to_date"))

	raw = query.run(as_dict=True)
	grand_total = sum(float(r.total_revenue or 0) for r in raw)

	result = []
	for r in raw:
		revenue = float(r.total_revenue or 0)
		orders = int(r.total_orders or 0)
		avg = round(revenue / max(orders, 1), 2)
		pct = round((revenue / grand_total * 100), 2) if grand_total else 0
		result.append([r.order_from or "Direct", orders, revenue, avg, pct])
	return result

def get_chart_data(data):
	if not data:
		return None
	labels = [row[0] for row in data]
	orders = [row[1] for row in data]
	revenue = [float(row[2] or 0) for row in data]
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Orders"), "values": orders},
				{"name": _("Revenue"), "values": revenue},
			]
		},
		"type": "bar",
		"colors": ["#4E79A7", "#59A14F"]
	}
