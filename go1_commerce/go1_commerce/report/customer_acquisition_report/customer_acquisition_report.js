// Copyright (c) 2024, Tridots Tech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Acquisition Report"] = {
	"filters": [
		{
			"fieldname": "year",
			"fieldtype": "Select",
			"label": __("Year"),
			"reqd": 1
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": ""
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": ""
		}
	],
	"onload": function() {
		return frappe.call({
			method: "go1_commerce.go1_commerce.report.total_orders.total_orders.get_years",
			callback: function(r) {
				var year_filter = frappe.query_report_filters_by_name.year;
				year_filter.df.options = r.message;
				year_filter.df.default = r.message.split("\n")[0];
				year_filter.refresh();
				year_filter.set_input(year_filter.df.default);
			}
		});
	}
}
