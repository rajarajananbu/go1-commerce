import frappe
from frappe import _
from frappe.query_builder import DocType, Field
from frappe.query_builder.functions import IfNull, Count, Function
from go1_commerce.utils.setup import get_settings_from_domain

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_data(filters):
	try:
		birthday_club_settings = get_settings_from_domain('BirthDay Club Setting')
	except Exception:
		return []

	birthday_club_member = DocType("BirthDay Club Member")
	customers = DocType("Customers")

	if birthday_club_settings.beneficiary_method == "Discount":
		discount_usage_history = DocType("Discount Usage History")
		subquery = (
			frappe.qb.from_(discount_usage_history)
			.select(discount_usage_history.order_id)
			.where(discount_usage_history.parent == birthday_club_settings.discount_id)
			.where(discount_usage_history.customer == customers.name)
			.orderby(discount_usage_history.creation, order=frappe.qb.desc)
			.limit(1)
		)
		query = (
			frappe.qb.from_(birthday_club_member)
			.inner_join(customers).on(birthday_club_member.email == customers.email)
			.select(
				birthday_club_member.email,
				birthday_club_member.day,
				birthday_club_member.month,
				Function("DATE", birthday_club_member.creation).as_("creation_date"),
				subquery.as_("order_id")
			)
			.orderby(birthday_club_member.creation, order=frappe.qb.desc)
		)
		return query.run(as_list=True)

	elif birthday_club_settings.beneficiary_method == "Wallet":
		wallet_txn = DocType("Wallet Transaction")
		subquery = (
			frappe.qb.from_(wallet_txn)
			.select(Function("DATE", wallet_txn.creation))
			.where(wallet_txn.customer == customers.name)
			.where(wallet_txn.type == "Birthday Credit")
			.orderby(wallet_txn.creation, order=frappe.qb.desc)
			.limit(1)
		)
		query = (
			frappe.qb.from_(birthday_club_member)
			.inner_join(customers).on(birthday_club_member.email == customers.email)
			.select(
				birthday_club_member.email,
				birthday_club_member.day,
				birthday_club_member.month,
				Function("DATE", birthday_club_member.creation).as_("creation_date"),
				subquery.as_("wallet_credited_on")
			)
			.orderby(birthday_club_member.creation, order=frappe.qb.desc)
		)
		return query.run(as_list=True)

	elif birthday_club_settings.beneficiary_method == "Points":
		query = (
			frappe.qb.from_(birthday_club_member)
			.inner_join(customers).on(birthday_club_member.email == customers.email)
			.select(
				birthday_club_member.email,
				birthday_club_member.day,
				birthday_club_member.month,
				Function("DATE", birthday_club_member.creation).as_("creation_date"),
			)
			.orderby(birthday_club_member.creation, order=frappe.qb.desc)
		)
		return query.run(as_list=True)

	return []

def get_columns():
	try:
		birthday_club_settings = get_settings_from_domain('BirthDay Club Setting')
	except Exception:
		return [
			_("Email") + ":Data:200",
			_("Birth Day") + ":Data:100",
			_("Birth Month") + ":Data:100",
			_("Registered On") + ":Date:120",
		]

	columns = [
		_("Email") + ":Data:200",
		_("Birth Day") + ":Data:100",
		_("Birth Month") + ":Data:100",
		_("Registered On") + ":Date:120",
	]

	if birthday_club_settings.beneficiary_method == "Discount":
		columns.append(_("Redeem For Order") + ":Link/Order:180")
	elif birthday_club_settings.beneficiary_method == "Wallet":
		columns.append(_("Wallet Amount Credited On") + ":Date:180")
	elif birthday_club_settings.beneficiary_method == "Points":
		columns.append(_("Points Credited On") + ":Date:180")

	return columns
