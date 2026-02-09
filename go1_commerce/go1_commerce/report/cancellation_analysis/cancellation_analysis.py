# Copyright (c) 2024, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count, Sum, Function

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(filters)
	summary = get_summary(filters)
	return columns, data, None, chart, summary

def get_columns():
	return [
		_("Cancel Reason") + ":Data:250",
		_("Count") + ":Int:100",
		_("Total Lost Revenue") + ":Currency:150",
		_("Avg Order Value") + ":Currency:130",
		_("Percentage") + ":Percent:100",
	]

def get_data(filters):
	OrderDT = DocType("Order")
	query = (
		frappe.qb.from_(OrderDT)
		.select(
			OrderDT.order_cancel_reason,
			Count("*").as_("count"),
			Sum(OrderDT.total_amount).as_("lost_revenue"),
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.status == "Cancelled")
		.groupby(OrderDT.order_cancel_reason)
		.orderby(Count("*"), order=frappe.qb.desc)
	)
	if filters.get("from_date"):
		query = query.where(OrderDT.order_date >= filters.get("from_date"))
	if filters.get("to_date"):
		query = query.where(OrderDT.order_date <= filters.get("to_date"))

	raw = query.run(as_dict=True)
	total_cancelled = sum(int(r.count or 0) for r in raw)

	result = []
	for r in raw:
		cnt = int(r.count or 0)
		revenue = float(r.lost_revenue or 0)
		avg = round(revenue / max(cnt, 1), 2)
		pct = round((cnt / max(total_cancelled, 1)) * 100, 2)
		result.append([r.order_cancel_reason or "Not Specified", cnt, revenue, avg, pct])
	return result

def get_chart_data(filters):
	OrderDT = DocType("Order")
	query = (
		frappe.qb.from_(OrderDT)
		.select(
			Function("DATE_FORMAT", OrderDT.order_date, "%Y-%m").as_("month"),
			Count("*").as_("cancelled"),
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.status == "Cancelled")
		.groupby(Function("DATE_FORMAT", OrderDT.order_date, "%Y-%m"))
		.orderby(Function("DATE_FORMAT", OrderDT.order_date, "%Y-%m"))
	)
	if filters.get("from_date"):
		query = query.where(OrderDT.order_date >= filters.get("from_date"))
	if filters.get("to_date"):
		query = query.where(OrderDT.order_date <= filters.get("to_date"))

	data = query.run(as_dict=True)
	if not data:
		return None

	return {
		"data": {
			"labels": [d.month for d in data],
			"datasets": [{"name": _("Cancellations"), "values": [int(d.cancelled) for d in data]}]
		},
		"type": "line",
		"colors": ["#E15759"]
	}

def get_summary(filters):
	OrderDT = DocType("Order")
	total_query = (
		frappe.qb.from_(OrderDT)
		.select(Count("*").as_("total"))
		.where(OrderDT.docstatus == 1)
	)
	cancelled_query = (
		frappe.qb.from_(OrderDT)
		.select(
			Count("*").as_("cancelled"),
			Sum(OrderDT.total_amount).as_("lost")
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.status == "Cancelled")
	)
	if filters.get("from_date"):
		total_query = total_query.where(OrderDT.order_date >= filters.get("from_date"))
		cancelled_query = cancelled_query.where(OrderDT.order_date >= filters.get("from_date"))
	if filters.get("to_date"):
		total_query = total_query.where(OrderDT.order_date <= filters.get("to_date"))
		cancelled_query = cancelled_query.where(OrderDT.order_date <= filters.get("to_date"))

	total = total_query.run(as_list=True)[0][0] or 0
	cancelled_data = cancelled_query.run(as_dict=True)[0]
	cancelled = int(cancelled_data.cancelled or 0)
	lost = float(cancelled_data.lost or 0)
	rate = round((cancelled / max(total, 1)) * 100, 2)

	return [
		{"value": cancelled, "label": _("Total Cancellations"), "datatype": "Int"},
		{"value": lost, "label": _("Lost Revenue"), "datatype": "Currency"},
		{"value": rate, "label": _("Cancellation Rate %"), "datatype": "Percent"},
	]
