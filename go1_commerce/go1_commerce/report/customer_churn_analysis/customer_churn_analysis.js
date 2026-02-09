// Copyright (c) 2024, Tridots Tech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Churn Analysis"] = {
	"filters": [
		{
			"fieldname": "inactive_days",
			"fieldtype": "Int",
			"label": __("Inactive Days"),
			"default": 90,
			"reqd": 1
		}
	]
}
