frappe.query_reports["Vendor Performance"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date"
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date"
		},
		{
			fieldname: "vendor",
			label: __("Vendor"),
			fieldtype: "Link",
			options: "Business"
		}
	]
};
