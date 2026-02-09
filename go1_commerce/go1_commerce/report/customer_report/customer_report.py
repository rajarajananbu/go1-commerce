# Copyright (c) 2013, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType, Field
from frappe.query_builder.functions import Cast, GroupConcat, Sum, IfNull

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	columns = [
		_("Id") + ":Link/Customers:120",
		_("Customer Name") + ":Data:200",
		_("Customer Email") + ":Data:200",
		_("Customer Phone") + ":Data:120",
	]
	if "loyalty" in frappe.get_installed_apps():
		columns.append(_("Loyalty Points") + ":Data:140")
	columns += [
		_("Creation Date") + ":Data:200",
		_("Social Media Source") + ":Data:150",
	]
	return columns

def get_data(filters):
	Customer = DocType('Customers')
	UserSocialLogin = DocType('User Social Login')

	select_fields = [
		Customer.name,
		Customer.full_name,
		Customer.email,
		Customer.phone,
	]

	query = frappe.qb.from_(Customer)

	if "loyalty" in frappe.get_installed_apps():
		LoyaltyPointEntry = DocType('Loyalty Point Entry')
		query = query.left_join(LoyaltyPointEntry).on(
			(LoyaltyPointEntry.customer == Customer.name) &
			(LoyaltyPointEntry.party_type == 'Customers')
		)
		select_fields.append(IfNull(Sum(LoyaltyPointEntry.loyalty_points), 0).as_('total_points'))

	select_fields += [
		Cast(Customer.creation, 'DATE').as_('creation_date'),
		GroupConcat(UserSocialLogin.provider).as_('social_logins'),
	]

	query = query.left_join(UserSocialLogin).on(
		(UserSocialLogin.parent == Customer.user_id) &
		(UserSocialLogin.provider != 'frappe')
	)

	query = query.select(*select_fields)

	if filters.get('from_date'):
		query = query.where(Cast(Customer.creation, 'DATE') >= filters.get('from_date'))
	if filters.get('to_date'):
		query = query.where(Cast(Customer.creation, 'DATE') <= filters.get('to_date'))
	query = query.where(Customer.name != '').where(Customer.naming_series != 'GC-')
	query = query.groupby(Customer.name)
	query = query.orderby(Customer.creation, order=frappe.qb.desc)
	return query.run(as_list=True)
