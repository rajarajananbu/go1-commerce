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
		_("Category") + ":Link/Product Category:200",
		_("Category Name") + ":Data:200",
		_("Products") + ":Int:100",
		_("Total Qty Sold") + ":Int:120",
		_("Total Revenue") + ":Currency:150",
		_("Avg Price") + ":Currency:120",
	]

def get_data(filters):
	ProductCategory = DocType("Product Category")
	Product = DocType("Product")
	ProductCategoryMapping = DocType("Product Category Mapping")
	OrderItem = DocType("Order Item")
	OrderDT = DocType("Order")

	query = (
		frappe.qb.from_(ProductCategory)
		.left_join(ProductCategoryMapping).on(
			ProductCategoryMapping.category == ProductCategory.name
		)
		.left_join(Product).on(
			Product.name == ProductCategoryMapping.parent
		)
		.left_join(OrderItem).on(
			(OrderItem.item == Product.name) &
			(OrderItem.parenttype == "Order")
		)
		.left_join(OrderDT).on(
			(OrderDT.name == OrderItem.parent) &
			(OrderDT.docstatus == 1)
		)
		.select(
			ProductCategory.name.as_("cat_id"),
			ProductCategory.category_name,
			Count(Product.name).as_("products"),
			Sum(OrderItem.quantity).as_("qty_sold"),
			Sum(OrderItem.amount).as_("revenue"),
		)
		.where(ProductCategory.is_active == 1)
		.groupby(ProductCategory.name)
		.orderby(Sum(OrderItem.amount), order=frappe.qb.desc)
	)
	if filters.get("from_date"):
		query = query.where(OrderDT.order_date >= filters.get("from_date"))
	if filters.get("to_date"):
		query = query.where(OrderDT.order_date <= filters.get("to_date"))

	raw = query.run(as_dict=True)
	result = []
	for r in raw:
		qty = int(r.qty_sold or 0)
		revenue = float(r.revenue or 0)
		avg = round(revenue / max(qty, 1), 2)
		result.append([
			r.cat_id, r.category_name,
			int(r.products or 0), qty, revenue, avg
		])
	return result

def get_chart_data(data):
	if not data:
		return None
	filtered = [row for row in data if row[4] > 0][:15]
	if not filtered:
		return None
	labels = [row[1] or row[0] for row in filtered]
	revenue = [float(row[4] or 0) for row in filtered]
	qty = [row[3] for row in filtered]
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Revenue"), "type": "bar", "values": revenue},
				{"name": _("Qty Sold"), "type": "line", "values": qty},
			]
		},
		"type": "axis-mixed",
		"colors": ["#59A14F", "#E15759"]
	}
