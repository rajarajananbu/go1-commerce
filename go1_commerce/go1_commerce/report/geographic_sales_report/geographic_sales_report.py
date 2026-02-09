# Copyright (c) 2024, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Count

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	chart = get_chart_data(data, filters)
	return columns, data, None, chart

def get_columns(filters):
	group_by = filters.get("group_by") or "City"
	return [
		_(group_by) + ":Data:200",
		_("Total Orders") + ":Int:120",
		_("Total Revenue") + ":Currency:150",
		_("Avg Order Value") + ":Currency:130",
		_("Unique Customers") + ":Int:130",
	]

def get_data(filters):
	OrderDT = DocType("Order")
	CustomerDT = DocType("Customers")
	group_by = filters.get("group_by") or "City"

	field_map = {
		"City": CustomerDT.city,
		"State": CustomerDT.state,
		"Country": CustomerDT.country,
	}
	group_field = field_map.get(group_by, CustomerDT.city)

	query = (
		frappe.qb.from_(OrderDT)
		.inner_join(CustomerDT).on(OrderDT.customer == CustomerDT.name)
		.select(
			group_field.as_("location"),
			Count("*").as_("total_orders"),
			Sum(OrderDT.total_amount).as_("total_revenue"),
			Count(CustomerDT.name).as_("unique_customers"),
		)
		.where(OrderDT.docstatus == 1)
		.where(group_field.isnotnull())
		.where(group_field != "")
		.groupby(group_field)
		.orderby(Sum(OrderDT.total_amount), order=frappe.qb.desc)
	)
	if filters.get("from_date"):
		query = query.where(OrderDT.order_date >= filters.get("from_date"))
	if filters.get("to_date"):
		query = query.where(OrderDT.order_date <= filters.get("to_date"))

	raw = query.run(as_dict=True)
	result = []
	for r in raw:
		orders = int(r.total_orders or 0)
		revenue = float(r.total_revenue or 0)
		avg = round(revenue / max(orders, 1), 2)
		result.append([
			r.location or "Unknown", orders, revenue, avg,
			int(r.unique_customers or 0)
		])
	return result

def get_chart_data(data, filters):
	if not data:
		return None
	group_by = filters.get("group_by") or "City"
	labels = [row[0] for row in data[:20]]
	revenue = [float(row[2] or 0) for row in data[:20]]
	orders = [row[1] for row in data[:20]]
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Revenue"), "type": "bar", "values": revenue},
				{"name": _("Orders"), "type": "line", "values": orders},
			]
		},
		"type": "axis-mixed",
		"colors": ["#4E79A7", "#F28E2B"]
	}
