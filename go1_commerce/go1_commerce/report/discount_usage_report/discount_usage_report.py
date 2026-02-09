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
		_("Discount") + ":Link/Discounts:200",
		_("Discount Title") + ":Data:200",
		_("Discount Type") + ":Data:120",
		_("Times Used") + ":Int:100",
		_("Total Discount Given") + ":Currency:150",
		_("Revenue from Orders") + ":Currency:150",
	]

def get_data(filters):
	OrderDT = DocType("Order")
	DiscountDT = DocType("Discounts")

	query = (
		frappe.qb.from_(OrderDT)
		.inner_join(DiscountDT).on(OrderDT.discount == DiscountDT.name)
		.select(
			DiscountDT.name.as_("discount_id"),
			DiscountDT.title.as_("discount_title"),
			DiscountDT.discount_type,
			Count("*").as_("times_used"),
			Sum(OrderDT.discount_amount).as_("total_discount"),
			Sum(OrderDT.total_amount).as_("total_revenue"),
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.discount.isnotnull())
		.where(OrderDT.discount != "")
		.groupby(DiscountDT.name)
		.orderby(Count("*"), order=frappe.qb.desc)
	)
	if filters.get("from_date"):
		query = query.where(OrderDT.order_date >= filters.get("from_date"))
	if filters.get("to_date"):
		query = query.where(OrderDT.order_date <= filters.get("to_date"))
	if filters.get("discount"):
		query = query.where(DiscountDT.name == filters.get("discount"))

	raw = query.run(as_dict=True)
	return [
		[r.discount_id, r.discount_title, r.discount_type,
		 int(r.times_used or 0), float(r.total_discount or 0), float(r.total_revenue or 0)]
		for r in raw
	]

def get_chart_data(data):
	if not data:
		return None
	labels = [row[1] or row[0] for row in data[:15]]
	usage = [row[3] for row in data[:15]]
	discount_amt = [float(row[4] or 0) for row in data[:15]]
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Times Used"), "type": "bar", "values": usage},
				{"name": _("Discount Amount"), "type": "line", "values": discount_amt},
			]
		},
		"type": "axis-mixed",
		"colors": ["#F28E2B", "#E15759"]
	}
