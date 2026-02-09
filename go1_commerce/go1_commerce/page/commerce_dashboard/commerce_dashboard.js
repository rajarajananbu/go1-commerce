frappe.pages['commerce-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Commerce Dashboard',
		single_column: true
	});

	page.main.addClass('frappe-card');
	$(page.body).html('<div class="commerce-dashboard-container" style="padding: 15px;"></div>');
	new CommerceDashboard(page);
};

class CommerceDashboard {
	constructor(page) {
		this.page = page;
		this.container = $(page.body).find('.commerce-dashboard-container');
		this.render_loading();
		this.fetch_data();
	}

	render_loading() {
		this.container.html(`
			<div style="text-align: center; padding: 60px 0;">
				<div class="text-muted">${__("Loading dashboard...")}</div>
			</div>
		`);
	}

	fetch_data() {
		frappe.call({
			method: 'go1_commerce.go1_commerce.page.commerce_dashboard.commerce_dashboard.get_dashboard_data',
			callback: (r) => {
				if (r.message) {
					this.data = r.message;
					this.render();
				}
			}
		});
	}

	render() {
		let d = this.data;
		let nc = d.number_cards;
		let mc = d.monthly_comparison;

		let order_change = mc.previous_orders > 0
			? (((mc.current_orders - mc.previous_orders) / mc.previous_orders) * 100).toFixed(1)
			: 0;
		let revenue_change = mc.previous_revenue > 0
			? (((mc.current_revenue - mc.previous_revenue) / mc.previous_revenue) * 100).toFixed(1)
			: 0;

		this.container.html(`
			<!-- Number Cards Row -->
			<div class="row" style="margin-bottom: 20px;">
				${this.number_card("Total Orders", format_number(nc.total_orders), "blue", "shopping-cart")}
				${this.number_card("Total Revenue", format_currency(nc.total_revenue), "green", "dollar-sign")}
				${this.number_card("This Month Orders", format_number(nc.monthly_orders),
					parseFloat(order_change) >= 0 ? "green" : "red",
					"trending-up",
					order_change + "% vs last month"
				)}
				${this.number_card("This Month Revenue", format_currency(nc.monthly_revenue),
					parseFloat(revenue_change) >= 0 ? "green" : "red",
					"bar-chart-2",
					revenue_change + "% vs last month"
				)}
			</div>
			<div class="row" style="margin-bottom: 20px;">
				${this.number_card("Pending Orders", format_number(nc.pending_orders), "orange", "clock")}
				${this.number_card("Total Customers", format_number(nc.total_customers), "purple", "users")}
				${this.number_card("Avg Order Value", format_currency(nc.avg_order_value), "cyan", "activity")}
				<div class="col-sm-3">
					<div style="background: var(--card-bg); border-radius: 8px; padding: 20px; border: 1px solid var(--border-color); height: 100%;">
						<div style="font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">Quick Links</div>
						<div style="margin-top: 10px;">
							<a href="/app/order" class="btn btn-xs btn-default" style="margin: 2px;">Orders</a>
							<a href="/app/product" class="btn btn-xs btn-default" style="margin: 2px;">Products</a>
							<a href="/app/customers" class="btn btn-xs btn-default" style="margin: 2px;">Customers</a>
						</div>
					</div>
				</div>
			</div>

			<!-- Charts Row 1: Sales Trend + Order Status -->
			<div class="row" style="margin-bottom: 20px;">
				<div class="col-sm-8">
					<div class="dashboard-chart-container" style="background: var(--card-bg); border-radius: 8px; padding: 20px; border: 1px solid var(--border-color);">
						<h6 style="margin-bottom: 15px; font-weight: 600;">Sales Trend (Last 12 Months)</h6>
						<div id="sales-trend-chart"></div>
					</div>
				</div>
				<div class="col-sm-4">
					<div class="dashboard-chart-container" style="background: var(--card-bg); border-radius: 8px; padding: 20px; border: 1px solid var(--border-color);">
						<h6 style="margin-bottom: 15px; font-weight: 600;">Order Status</h6>
						<div id="order-status-chart"></div>
					</div>
				</div>
			</div>

			<!-- Charts Row 2: Top Products + Payment Status -->
			<div class="row" style="margin-bottom: 20px;">
				<div class="col-sm-8">
					<div class="dashboard-chart-container" style="background: var(--card-bg); border-radius: 8px; padding: 20px; border: 1px solid var(--border-color);">
						<h6 style="margin-bottom: 15px; font-weight: 600;">Top Selling Products</h6>
						<div id="top-products-chart"></div>
					</div>
				</div>
				<div class="col-sm-4">
					<div class="dashboard-chart-container" style="background: var(--card-bg); border-radius: 8px; padding: 20px; border: 1px solid var(--border-color);">
						<h6 style="margin-bottom: 15px; font-weight: 600;">Payment Status</h6>
						<div id="payment-status-chart"></div>
					</div>
				</div>
			</div>

			<!-- Charts Row 3: Top Customers -->
			<div class="row" style="margin-bottom: 20px;">
				<div class="col-sm-6">
					<div class="dashboard-chart-container" style="background: var(--card-bg); border-radius: 8px; padding: 20px; border: 1px solid var(--border-color);">
						<h6 style="margin-bottom: 15px; font-weight: 600;">Top Customers by Revenue</h6>
						<div id="top-customers-chart"></div>
					</div>
				</div>
				<div class="col-sm-6">
					<div class="dashboard-chart-container" style="background: var(--card-bg); border-radius: 8px; padding: 20px; border: 1px solid var(--border-color);">
						<h6 style="margin-bottom: 15px; font-weight: 600;">Recent Orders</h6>
						<div id="recent-orders-table">${this.render_recent_orders(d.recent_orders)}</div>
					</div>
				</div>
			</div>
		`);

		this.render_charts();
	}

	number_card(title, value, color, icon, subtitle) {
		let color_map = {
			blue: "#4E79A7", green: "#59A14F", orange: "#F28E2B",
			red: "#E15759", purple: "#B07AA1", cyan: "#76B7B2"
		};
		let bg = color_map[color] || "#4E79A7";
		return `
			<div class="col-sm-3" style="margin-bottom: 10px;">
				<div style="background: ${bg}; border-radius: 8px; padding: 20px; color: #fff; min-height: 100px;">
					<div style="font-size: 12px; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px;">${title}</div>
					<div style="font-size: 24px; font-weight: 700; margin-top: 8px;">${value}</div>
					${subtitle ? `<div style="font-size: 11px; opacity: 0.75; margin-top: 4px;">${subtitle}</div>` : ''}
				</div>
			</div>
		`;
	}

	render_recent_orders(orders) {
		if (!orders || !orders.length) return '<div class="text-muted text-center" style="padding: 30px;">No recent orders</div>';
		let rows = orders.map(o => {
			let status_color = {Placed: "blue", Processing: "orange", Completed: "green", Cancelled: "red", Delivered: "green"}[o.status] || "grey";
			return `<tr>
				<td><a href="/app/order/${o.name}">${o.name}</a></td>
				<td>${o.customer_name || ''}</td>
				<td><span class="indicator-pill ${status_color}">${o.status}</span></td>
				<td style="text-align:right;">${format_currency(o.total_amount)}</td>
			</tr>`;
		}).join('');
		return `<table class="table table-sm" style="font-size: 12px; margin: 0;">
			<thead><tr><th>Order</th><th>Customer</th><th>Status</th><th style="text-align:right;">Amount</th></tr></thead>
			<tbody>${rows}</tbody>
		</table>`;
	}

	render_charts() {
		let d = this.data;

		// Sales Trend - Line Chart
		if (d.sales_trend.labels.length) {
			new frappe.Chart("#sales-trend-chart", {
				type: "axis-mixed",
				height: 280,
				colors: ["#4E79A7", "#59A14F"],
				data: {
					labels: d.sales_trend.labels,
					datasets: [
						{name: "Orders", type: "bar", values: d.sales_trend.orders},
						{name: "Revenue", type: "line", values: d.sales_trend.revenue}
					]
				},
				tooltipOptions: {
					formatTooltipY: (v) => format_currency(v)
				}
			});
		}

		// Order Status - Pie Chart
		if (d.order_status.labels.length) {
			new frappe.Chart("#order-status-chart", {
				type: "pie",
				height: 280,
				colors: ["#4E79A7", "#F28E2B", "#59A14F", "#E15759", "#76B7B2", "#EDC948", "#B07AA1"],
				data: {
					labels: d.order_status.labels,
					datasets: [{values: d.order_status.values}]
				}
			});
		}

		// Top Products - Bar Chart
		if (d.top_products.labels.length) {
			new frappe.Chart("#top-products-chart", {
				type: "bar",
				height: 280,
				colors: ["#FF6F61"],
				data: {
					labels: d.top_products.labels,
					datasets: [{name: "Qty Sold", values: d.top_products.qty}]
				},
				barOptions: {spaceRatio: 0.4}
			});
		}

		// Payment Status - Pie Chart
		if (d.payment_status.labels.length) {
			new frappe.Chart("#payment-status-chart", {
				type: "percentage",
				height: 280,
				colors: ["#59A14F", "#F28E2B", "#E15759", "#76B7B2"],
				data: {
					labels: d.payment_status.labels,
					datasets: [{values: d.payment_status.values}]
				}
			});
		}

		// Top Customers - Bar Chart
		if (d.top_customers.labels.length) {
			new frappe.Chart("#top-customers-chart", {
				type: "bar",
				height: 280,
				colors: ["#36A2EB"],
				data: {
					labels: d.top_customers.labels,
					datasets: [{name: "Revenue", values: d.top_customers.spent}]
				},
				tooltipOptions: {
					formatTooltipY: (v) => format_currency(v)
				},
				barOptions: {spaceRatio: 0.4}
			});
		}
	}
}
