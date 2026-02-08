app_name = "go1_commerce"
app_title = "Go1 Commerce"
app_publisher = "Tridotstech PVT LTD"
app_description = "Go1 Commerce is an Open Source eCommerce portal built on frappe framework."
app_email = "info@tridotstech.com"
app_license = "mit"
required_apps = ['builder']

app_logo_url = "/assets/go1_commerce/images/go1_commerce_logo.svg"

website_context = {
	"favicon": "/assets/go1_commerce/images/go1favicon.svg",
	"splash_image": "/assets/go1_commerce/images/go1_commerce_logo.svg",
}

boot_session = "go1_commerce.go1_commerce.v2.common.boot_session"

after_install = "go1_commerce.go1_commerce.after_install.after_install"
on_session_creation = "go1_commerce.go1_commerce.v2.common.login_customer"
on_logout = "go1_commerce.go1_commerce.v2.common.logout_customer"

app_include_css = [
	"/assets/go1_commerce/css/console.css",
	"/assets/go1_commerce/css/ui/uploader.css",
]
app_include_js = [
    "/assets/go1_commerce/js/ui/dialog_popup.js",
     "/assets/go1_commerce/js/default_methods.js",
     "/assets/go1_commerce/js/option.js",
	"/assets/go1_commerce/js/console.js",
	"/assets/go1_commerce/js/getting_started.js",
	"assets/go1_commerce/js/ui/product_func_class.js",
	"assets/go1_commerce/js/quick_entry/return_quick_entry.js",
]
doctype_js = {
    "Web Form" : "public/js/ui/editor/web_form.js"
    }

page_js = {
	"products-bulk-update": [
		"public/plugins/datatable/sortable.min.js",
		"public/plugins/datatable/clusterize.min.js",
		"public/plugins/datatable/frappe-datatable.min.js",
		"public/js/uppy.min.js",
		"public/js/lightgallery.js"
	]
}


has_website_permission = {
	"Customers": "go1_commerce.go1_commerce.doctype.customers.customers.has_website_permission"
}

override_doctype_class = {
	'File': 'go1_commerce.go1_commerce.override.CustomFile',
	'Builder Page':'go1_commerce.go1_commerce.doctype.override_doctype.builder_page.BuilderPage'
}


doc_events = {
	"User": {
		"after_insert": "go1_commerce.go1_commerce.doctype.customers.customers.generate_keys"
	},
	"Newsletter": {
		"autoname": "go1_commerce.utils.setup.autoname_newsletter"
	},
	
	"Order": {
		"on_submit": "go1_commerce.go1_commerce.v2.whoosh.update_order_item"
	},
	"Google Settings": {
		"validate": "go1_commerce.utils.setup.validate_google_settings"
	},
	"Help Article": {
		"validate": "go1_commerce.go1_commerce.v2.common.create_help_article_json"
	},
	"Order Settings": {
		"on_update": "go1_commerce.go1_commerce.v2.common.generate_all_website_settings_json_doc"
	},
	"Catalog Settings": {
		"on_update": "go1_commerce.go1_commerce.v2.common.generate_all_website_settings_json_doc"
	},
	"Market Place Settings": {
		"on_update": "go1_commerce.go1_commerce.v2.common.generate_all_website_settings_json_doc"
	},
	"Shopping Cart Settings": {
		"on_update": "go1_commerce.go1_commerce.v2.common.generate_all_website_settings_json_doc"
	},
	"Product Category": {
		"on_update": "go1_commerce.go1_commerce.v2.common.generate_all_website_settings_json_doc"
	},
	"Media Settings": {
		"on_update": "go1_commerce.go1_commerce.v2.common.generate_all_website_settings_json_doc"
	},
	"Header Component": {
		"on_update": "go1_commerce.go1_commerce.v2.common.generate_all_website_settings_json_doc"
	},
	"Footer Component": {
		"on_update": "go1_commerce.go1_commerce.v2.common.generate_all_website_settings_json_doc"
	},
	"Menu": {
		"on_update": "go1_commerce.go1_commerce.v2.common.generate_all_website_settings_json_doc"
	},
	"Version":{
		"after_insert":"go1_commerce.go1_commerce.v2.orders.update_stoke"
	},
	"Builder Page":{
		"on_update":"go1_commerce.go1_commerce.v2.builder_page.update_global_script"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"all": [
		"go1_commerce.accounts.api.release_lockedin_amount"
	],
	"monthly": [
		"go1_commerce.utils.setup.clear_logs"	
	],
	"cron": {
		"0 9 * * *": [
			"go1_commerce.go1_commerce.doctype.email_campaign.email_campaign.send_email_to_campaigns"			
		],
		"0 1 * * *": [
			"go1_commerce.go1_commerce.doctype.email_campaign.email_campaign.set_email_campaign_status",
			"go1_commerce.go1_commerce.doctype.customers.customers.delete_guest_customers",
		],
		"30 12 1 * *":[
			"go1_commerce.utils.setup.clear_api_log"
		]
	}
}

fixtures = [
	{
		"doctype": "Client Script",
		"filters": [
			["name", "in", (
				"Newsletter-Client"
			)]
		]
	},
	{
		"doctype": "Custom Field",
		"filters": [
			["name", "in", (
				"Country-enabled",
				"Country-phone_number_code",
				"Country-validate_zipcode",
				"Country-zipcode_validation_policy",
				"Country-min_zipcode_length",
				"Country-max_zipcode_length",
				"Notification-allow_user_modify",
				"Google Settings-restrict_to_countries",
				"Google Settings-countries",
				"Google Settings-default_address",
				"Google Settings-latitude",
				"Google Settings-longitude",
				"Google Settings-marker_icon",
				"Help Article-doctype_name",
				"Help Article-domain_name",
				"Builder Settings-custom_server_script",

			)]
		]
	}
]

default_roles = [
	{'role': 'Customer', 'doctype':'Customers'},
]
override_whitelisted_methods = {
    "frappe.client.validate_link": "go1_commerce.utils.utils.validate_link",
    "frappe.desk.form.linked_with.cancel_all_linked_docs": "go1_commerce.utils.utils.cancel_all_linked_docs"
    
}

auto_cancel_exempted_doctypes = ["Order"]

