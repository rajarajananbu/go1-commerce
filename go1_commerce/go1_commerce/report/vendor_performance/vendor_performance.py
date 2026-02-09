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
		_("Vendor") + ":Link/Business:150",
		_("Vendor Name") + ":Data:200",
		_("Total Products") + ":Int:100",
		_("Total Orders") + ":Int:100",
		_("Total Revenue") + ":Currency:150",
		_("Avg Rating") + ":Float:100",
		_("Items Sold") + ":Int:100",
	]

def get_data(filters):
	BusinessDT = DocType("Business")
	Product = DocType("Product")
	OrderItem = DocType("Order Item")
	OrderDT = DocType("Order")
	ProductReview = DocType("Product Review")

	product_count = {}
	for p in frappe.get_all("Product", fields=["restaurant", "name"], filters={"is_active": 1}):
		if p.restaurant:
			product_count[p.restaurant] = product_count.get(p.restaurant, 0) + 1

	sales_query = (
		frappe.qb.from_(OrderItem)
		.inner_join(OrderDT).on(OrderDT.name == OrderItem.parent)
		.inner_join(Product).on(Product.name == OrderItem.item)
		.select(
			Product.restaurant.as_("vendor"),
			Count("*").as_("total_orders"),
			Sum(OrderItem.amount).as_("total_revenue"),
			Sum(OrderItem.quantity).as_("items_sold"),
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.payment_status == "Paid")
		.where(Product.restaurant.isnotnull())
		.where(Product.restaurant != "")
		.groupby(Product.restaurant)
		.orderby(Sum(OrderItem.amount), order=frappe.qb.desc)
	)
	if filters.get("from_date"):
		sales_query = sales_query.where(OrderDT.order_date >= filters.get("from_date"))
	if filters.get("to_date"):
		sales_query = sales_query.where(OrderDT.order_date <= filters.get("to_date"))
	if filters.get("vendor"):
		sales_query = sales_query.where(Product.restaurant == filters.get("vendor"))

	sales_data = {r.vendor: r for r in sales_query.run(as_dict=True)}

	review_query = (
		frappe.qb.from_(ProductReview)
		.inner_join(Product).on(Product.name == ProductReview.product)
		.select(
			Product.restaurant.as_("vendor"),
			Function("AVG", ProductReview.rating).as_("avg_rating"),
		)
		.where(Product.restaurant.isnotnull())
		.groupby(Product.restaurant)
	)
	try:
		rating_data = {r.vendor: round(float(r.avg_rating or 0), 1) for r in review_query.run(as_dict=True)}
	except Exception:
		rating_data = {}

	vendor_names = {b.name: b.restaurant_name for b in frappe.get_all("Business", fields=["name", "restaurant_name"])}

	all_vendors = set(list(sales_data.keys()) + list(product_count.keys()))
	if filters.get("vendor"):
		all_vendors = {filters.get("vendor")}

	result = []
	for vendor in all_vendors:
		s = sales_data.get(vendor)
		result.append([
			vendor,
			vendor_names.get(vendor, vendor),
			product_count.get(vendor, 0),
			int(s.total_orders or 0) if s else 0,
			float(s.total_revenue or 0) if s else 0,
			rating_data.get(vendor, 0),
			int(s.items_sold or 0) if s else 0,
		])

	result.sort(key=lambda x: x[4], reverse=True)
	return result

def get_chart_data(data):
	if not data:
		return None
	filtered = [row for row in data if row[4] > 0][:15]
	if not filtered:
		return None
	labels = [row[1] or row[0] for row in filtered]
	revenue = [float(row[4] or 0) for row in filtered]
	orders = [row[3] for row in filtered]
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
