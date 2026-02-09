import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count, Sum, Function
from frappe.utils import getdate, add_months, nowdate


@frappe.whitelist()
def get_dashboard_data():
	"""Get all dashboard data in a single call."""
	return {
		"number_cards": get_number_cards(),
		"sales_trend": get_sales_trend(),
		"order_status": get_order_status_distribution(),
		"payment_status": get_payment_status_distribution(),
		"top_products": get_top_products(),
		"top_customers": get_top_customers(),
		"recent_orders": get_recent_orders(),
		"monthly_comparison": get_monthly_comparison(),
	}


def get_number_cards():
	"""Get key metrics for number cards."""
	OrderDT = DocType("Order")
	today = getdate(nowdate())
	month_start = today.replace(day=1)

	total_orders = (
		frappe.qb.from_(OrderDT)
		.select(Count("*").as_("count"))
		.where(OrderDT.docstatus == 1)
		.run(as_list=True)
	)[0][0] or 0

	total_revenue = (
		frappe.qb.from_(OrderDT)
		.select(Sum(OrderDT.total_amount).as_("total"))
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.payment_status == "Paid")
		.run(as_list=True)
	)[0][0] or 0

	monthly_orders = (
		frappe.qb.from_(OrderDT)
		.select(Count("*").as_("count"))
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.order_date >= month_start)
		.run(as_list=True)
	)[0][0] or 0

	monthly_revenue = (
		frappe.qb.from_(OrderDT)
		.select(Sum(OrderDT.total_amount).as_("total"))
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.payment_status == "Paid")
		.where(OrderDT.order_date >= month_start)
		.run(as_list=True)
	)[0][0] or 0

	pending_orders = (
		frappe.qb.from_(OrderDT)
		.select(Count("*").as_("count"))
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.status.isin(["Placed", "Processing"]))
		.run(as_list=True)
	)[0][0] or 0

	CustomerDT = DocType("Customers")
	total_customers = (
		frappe.qb.from_(CustomerDT)
		.select(Count("*").as_("count"))
		.where(CustomerDT.customer_status == "Approved")
		.run(as_list=True)
	)[0][0] or 0

	avg_order_value = round(float(total_revenue) / max(total_orders, 1), 2)

	return {
		"total_orders": int(total_orders),
		"total_revenue": float(total_revenue),
		"monthly_orders": int(monthly_orders),
		"monthly_revenue": float(monthly_revenue),
		"pending_orders": int(pending_orders),
		"total_customers": int(total_customers),
		"avg_order_value": avg_order_value,
	}


def get_sales_trend():
	"""Get last 12 months sales trend."""
	OrderDT = DocType("Order")
	query = (
		frappe.qb.from_(OrderDT)
		.select(
			Function("DATE_FORMAT", OrderDT.order_date, "%Y-%m").as_("month"),
			Count("*").as_("orders"),
			Sum(OrderDT.total_amount).as_("revenue")
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.order_date >= add_months(nowdate(), -12))
		.groupby(Function("DATE_FORMAT", OrderDT.order_date, "%Y-%m"))
		.orderby(Function("DATE_FORMAT", OrderDT.order_date, "%Y-%m"))
	)
	data = query.run(as_dict=True)
	return {
		"labels": [d.month for d in data],
		"orders": [int(d.orders or 0) for d in data],
		"revenue": [float(d.revenue or 0) for d in data],
	}


def get_order_status_distribution():
	"""Get order count by status."""
	OrderDT = DocType("Order")
	query = (
		frappe.qb.from_(OrderDT)
		.select(OrderDT.status, Count("*").as_("count"))
		.where(OrderDT.docstatus == 1)
		.groupby(OrderDT.status)
		.orderby(Count("*"), order=frappe.qb.desc)
	)
	data = query.run(as_dict=True)
	return {
		"labels": [d.status for d in data],
		"values": [int(d.count) for d in data],
	}


def get_payment_status_distribution():
	"""Get order count by payment status."""
	OrderDT = DocType("Order")
	query = (
		frappe.qb.from_(OrderDT)
		.select(OrderDT.payment_status, Count("*").as_("count"))
		.where(OrderDT.docstatus == 1)
		.groupby(OrderDT.payment_status)
		.orderby(Count("*"), order=frappe.qb.desc)
	)
	data = query.run(as_dict=True)
	return {
		"labels": [d.payment_status for d in data],
		"values": [int(d.count) for d in data],
	}


def get_top_products():
	"""Get top 10 selling products."""
	Product = DocType("Product")
	OrderItem = DocType("Order Item")
	OrderDT = DocType("Order")
	query = (
		frappe.qb.from_(OrderItem)
		.inner_join(OrderDT).on(OrderDT.name == OrderItem.parent)
		.inner_join(Product).on(Product.name == OrderItem.item)
		.select(
			Product.item.as_("product_name"),
			Sum(OrderItem.quantity).as_("qty"),
			Sum(OrderItem.amount).as_("revenue")
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.payment_status == "Paid")
		.groupby(Product.name)
		.orderby(Sum(OrderItem.quantity), order=frappe.qb.desc)
		.limit(10)
	)
	data = query.run(as_dict=True)
	return {
		"labels": [d.product_name for d in data],
		"qty": [int(d.qty or 0) for d in data],
		"revenue": [float(d.revenue or 0) for d in data],
	}


def get_top_customers():
	"""Get top 10 customers by spend."""
	OrderDT = DocType("Order")
	query = (
		frappe.qb.from_(OrderDT)
		.select(
			OrderDT.customer_name,
			Count("*").as_("orders"),
			Sum(OrderDT.total_amount).as_("total_spent")
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.payment_status == "Paid")
		.groupby(OrderDT.customer_name)
		.orderby(Sum(OrderDT.total_amount), order=frappe.qb.desc)
		.limit(10)
	)
	data = query.run(as_dict=True)
	return {
		"labels": [d.customer_name for d in data],
		"orders": [int(d.orders or 0) for d in data],
		"spent": [float(d.total_spent or 0) for d in data],
	}


def get_recent_orders():
	"""Get 10 most recent orders."""
	OrderDT = DocType("Order")
	query = (
		frappe.qb.from_(OrderDT)
		.select(
			OrderDT.name,
			OrderDT.order_date,
			OrderDT.customer_name,
			OrderDT.status,
			OrderDT.payment_status,
			OrderDT.total_amount
		)
		.where(OrderDT.docstatus == 1)
		.orderby(OrderDT.creation, order=frappe.qb.desc)
		.limit(10)
	)
	return query.run(as_dict=True)


def get_monthly_comparison():
	"""Compare current month vs previous month."""
	OrderDT = DocType("Order")
	today = getdate(nowdate())
	current_month_start = today.replace(day=1)
	prev_month_start = add_months(current_month_start, -1)

	current = (
		frappe.qb.from_(OrderDT)
		.select(
			Count("*").as_("orders"),
			Sum(OrderDT.total_amount).as_("revenue")
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.order_date >= current_month_start)
		.run(as_dict=True)
	)[0]

	previous = (
		frappe.qb.from_(OrderDT)
		.select(
			Count("*").as_("orders"),
			Sum(OrderDT.total_amount).as_("revenue")
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.order_date >= prev_month_start)
		.where(OrderDT.order_date < current_month_start)
		.run(as_dict=True)
	)[0]

	return {
		"current_orders": int(current.orders or 0),
		"current_revenue": float(current.revenue or 0),
		"previous_orders": int(previous.orders or 0),
		"previous_revenue": float(previous.revenue or 0),
	}
