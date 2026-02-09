# Copyright (c) 2024, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Count, Function

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	chart = get_chart_data(data, filters)
	return columns, data, None, chart

def get_columns(filters):
	group_by = filters.get("group_by") or "Month"
	if group_by == "Tax Category":
		return [
			_("Tax Category") + ":Link/Tax Category:200",
			_("Tax Rate") + ":Percent:100",
			_("Taxable Amount") + ":Currency:150",
			_("Tax Collected") + ":Currency:150",
			_("Total with Tax") + ":Currency:150",
		]
	return [
		_("Period") + ":Data:150",
		_("Total Orders") + ":Int:100",
		_("Taxable Amount") + ":Currency:150",
		_("Tax Collected") + ":Currency:150",
		_("Total Revenue") + ":Currency:150",
	]

def get_data(filters):
	group_by = filters.get("group_by") or "Month"
	OrderDT = DocType("Order")

	if group_by == "Tax Category":
		return get_data_by_tax_category(filters)

	query = (
		frappe.qb.from_(OrderDT)
		.select(
			Function("DATE_FORMAT", OrderDT.order_date, "%Y-%m").as_("period"),
			Count("*").as_("total_orders"),
			Sum(OrderDT.order_subtotal).as_("taxable_amount"),
			Sum(OrderDT.total_tax_amount).as_("tax_collected"),
			Sum(OrderDT.total_amount).as_("total_revenue"),
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.order_date >= filters.get("from_date"))
		.where(OrderDT.order_date <= filters.get("to_date"))
		.groupby(Function("DATE_FORMAT", OrderDT.order_date, "%Y-%m"))
		.orderby(Function("DATE_FORMAT", OrderDT.order_date, "%Y-%m"))
	)
	raw = query.run(as_dict=True)
	return [
		[r.period, int(r.total_orders or 0), float(r.taxable_amount or 0),
		 float(r.tax_collected or 0), float(r.total_revenue or 0)]
		for r in raw
	]

def get_data_by_tax_category(filters):
	OrderDT = DocType("Order")
	OrderItem = DocType("Order Item")

	query = (
		frappe.qb.from_(OrderItem)
		.inner_join(OrderDT).on(OrderDT.name == OrderItem.parent)
		.select(
			OrderItem.tax_category,
			OrderItem.tax_rate,
			Sum(OrderItem.price * OrderItem.quantity).as_("taxable_amount"),
			Sum(OrderItem.tax).as_("tax_collected"),
			Sum(OrderItem.amount).as_("total_with_tax"),
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.order_date >= filters.get("from_date"))
		.where(OrderDT.order_date <= filters.get("to_date"))
		.where(OrderItem.tax_category.isnotnull())
		.where(OrderItem.tax_category != "")
		.groupby(OrderItem.tax_category)
		.orderby(Sum(OrderItem.tax), order=frappe.qb.desc)
	)

	try:
		raw = query.run(as_dict=True)
	except Exception:
		return []

	return [
		[r.tax_category, float(r.tax_rate or 0), float(r.taxable_amount or 0),
		 float(r.tax_collected or 0), float(r.total_with_tax or 0)]
		for r in raw
	]

def get_chart_data(data, filters):
	if not data:
		return None
	group_by = filters.get("group_by") or "Month"

	if group_by == "Tax Category":
		labels = [row[0] for row in data]
		values = [float(row[3] or 0) for row in data]
		return {
			"data": {
				"labels": labels,
				"datasets": [{"name": _("Tax Collected"), "values": values}]
			},
			"type": "pie",
			"colors": ["#4E79A7", "#F28E2B", "#59A14F", "#E15759", "#76B7B2", "#EDC948"]
		}

	labels = [row[0] for row in data]
	taxable = [float(row[2] or 0) for row in data]
	tax = [float(row[3] or 0) for row in data]
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Taxable Amount"), "type": "bar", "values": taxable},
				{"name": _("Tax Collected"), "type": "line", "values": tax},
			]
		},
		"type": "axis-mixed",
		"colors": ["#4E79A7", "#E15759"]
	}
