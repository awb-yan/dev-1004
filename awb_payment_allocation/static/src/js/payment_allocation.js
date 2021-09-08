odoo.define('awb_payment_allocation.AccountPaymentOdoo', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ReconciliationModel = require('account.ReconciliationModel');
var ReconciliationRenderer = require('account.ReconciliationRenderer');

var Widget = require('web.Widget');
var FieldManagerMixin = require('web.FieldManagerMixin');
var relational_fields = require('web.relational_fields');
var basic_fields = require('web.basic_fields');
var core = require('web.core');
var time = require('web.time');
var rpc = require('web.rpc');
var session = require('web.session');
var qweb = core.qweb;
var _t = core._t;

	var AccountPayment = require('account.ReconciliationRenderer');
	console.log("TEST 2222", AccountPayment)
		var self = this;

	var PaymentAlloc = require('account.ReconciliationClientAction');
	console.log("TEST 1111", PaymentAlloc)
	// this.onload = function(){myScript};
		
	AccountPayment.LineRenderer.include({
		// /**
		//  * @override
		//  * @param {jQueryElement} $el
		//  */
		// start: function () {
		// 	var self = this;
		// 	var def1 = this._makePartnerRecord(this._initialState.st_line.partner_id, this._initialState.st_line.partner_name).then(function (recordID) {
		// 		self.fields = {
		// 			partner_id : new relational_fields.FieldMany2One(self,
		// 				'partner_id',
		// 				self.model.get(recordID), {
		// 					mode: 'edit',
		// 					attrs: {
		// 						placeholder: self._initialState.st_line.communication_partner_name || _t('Select Partner'),
		// 					}
		// 				}
		// 			)
		// 		};
		// 		self.fields.partner_id.insertAfter(self.$('.accounting_view caption .o_buttons'));
		// 	});
		// 	$('<span class="line_info_button fa fa-info-circle"/>')
		// 		.appendTo(this.$('thead .cell_info_popover'))
		// 		.attr("data-content", qweb.render('reconciliation.line.statement_line.details', {'state': this._initialState}));
		// 	this.$el.popover({
		// 		'selector': '.line_info_button',
		// 		'placement': 'left',
		// 		'container': this.$el,
		// 		'html': true,
		// 		// disable bootstrap sanitizer because we use a table that has been
		// 		// rendered using qweb.render so it is safe and also because sanitizer escape table by default.
		// 		'sanitize': false,
		// 		'trigger': 'hover',
		// 		'animation': false,
		// 		'toggle': 'popover'
		// 	});

		// 	// var moveLineId = $el.closest('.mv_line').data('line-id');
		// 	// self._onSelectMoveLine()
		// 	// console.log("TEST 4444", moveLineId)
		// 	alert("EXAMPLE ALERT ");

		// 	var def2 = this._super.apply(this, arguments);
		// 	console.log("TEST 3333", def2)
		// 	return Promise.all([def1, def2]);
		// },

		// /**
		//  * @private
		//  * @param {MouseEvent} event
		//  */
		// _onSelectMoveLine: function (event) {
		// 	var $el = $(event.target);
		// 	$el.prop('disabled', true);
		// 	this._destroyPopover($el);
		// 	var moveLineId = $el.closest('.mv_line').data('line-id');
		// 	console.log("TEST 4444", moveLineId);
		// 	this.trigger_up('add_proposition', {'data': moveLineId});
		// },

	/**
	 * update the statement line rendering
	 *
	 * @param {object} state - statement line
	 */
	update: function (state) {
		var self = this;
		// isValid
		var to_check_checked = !!(state.to_check);
		this.$('caption .o_buttons button.o_validate').toggleClass('d-none', !!state.balance.type && !to_check_checked);
		this.$('caption .o_buttons button.o_reconcile').toggleClass('d-none', state.balance.type <= 0 || to_check_checked);
		this.$('caption .o_buttons .o_no_valid').toggleClass('d-none', state.balance.type >= 0);
		self.$('caption .o_buttons button.o_validate').toggleClass('text-warning', to_check_checked);

		// partner_id
		this._makePartnerRecord(state.st_line.partner_id, state.st_line.partner_name).then(function (recordID) {
			self.fields.partner_id.reset(self.model.get(recordID));
			self.$el.attr('data-partner', state.st_line.partner_id);
		});

		// mode
		this.$el.data('mode', state.mode).attr('data-mode', state.mode);
		this.$('.o_notebook li a').attr('aria-selected', false);
		this.$('.o_notebook li a').removeClass('active');
		this.$('.o_notebook .tab-content .tab-pane').removeClass('active');
		this.$('.o_notebook li a[href*="notebook_page_' + state.mode + '"]').attr('aria-selected', true);
		this.$('.o_notebook li a[href*="notebook_page_' + state.mode + '"]').addClass('active');
		this.$('.o_notebook .tab-content .tab-pane[id*="notebook_page_' + state.mode + '"]').addClass('active');
		this.$('.create, .match').each(function () {
			$(this).removeAttr('style');
		});

		// reconciliation_proposition
		var $props = this.$('.accounting_view tbody').empty();

		// Search propositions that could be a partial credit/debit.
		var props = [];
		var balance = state.balance.amount_currency;
		_.each(state.reconciliation_proposition, function (prop) {
			if (prop.display) {
				props.push(prop);
			}
		});

		_.each(props, function (line) {
			var $line = $(qweb.render("reconciliation.line.mv_line", {'line': line, 'state': state, 'proposition': true}));
			if (!isNaN(line.id)) {
				$('<span class="line_info_button fa fa-info-circle"/>')
					.appendTo($line.find('.cell_info_popover'))
					.attr("data-content", qweb.render('reconciliation.line.mv_line.details', {'line': line}));
			}
			$props.append($line);
		});

		// mv_lines
		var matching_modes = self.model.modes.filter(x => x.startsWith('match'));
		for (let i = 0; i < matching_modes.length; i++) {
			var stateMvLines = state['mv_lines_'+matching_modes[i]] || [];
			var recs_count = stateMvLines.length > 0 ? stateMvLines[0].recs_count : 0;
			var remaining = recs_count - stateMvLines.length;
			var $mv_lines = this.$('div[id*="notebook_page_' + matching_modes[i] + '"] .match table tbody').empty();
			this.$('.o_notebook li a[href*="notebook_page_' + matching_modes[i] + '"]').parent().toggleClass('d-none', stateMvLines.length === 0 && !state['filter_'+matching_modes[i]]);

			_.each(stateMvLines, function (line) {
				var $line = $(qweb.render("reconciliation.line.mv_line", {'line': line, 'state': state}));
				if (!isNaN(line.id)) {
					$('<span class="line_info_button fa fa-info-circle"/>')
					.appendTo($line.find('.cell_info_popover'))
					.attr("data-content", qweb.render('reconciliation.line.mv_line.details', {'line': line}));
				}
				$mv_lines.append($line);
			});

			this.$('div[id*="notebook_page_' + matching_modes[i] + '"] .match div.load-more').toggle(remaining > 0);
			this.$('div[id*="notebook_page_' + matching_modes[i] + '"] .match div.load-more span').text(remaining);
		}

		// Automatic Payment matching
		var payment_id = self.model.context.active_id;
		var allocation_mode = self.get_payment_allocation_mode(payment_id);
		var payment_alloc = Promise.all([allocation_mode]).then((paresults) => {
			var pr = paresults[0]
			// Oldest Invoice first
			if (pr == 'old_invoice' && stateMvLines.length != 0){
				// var date_sort = stateMvLines.slice().sort((a, b) => b.id - a.id);
				var date_sort = stateMvLines.slice().sort(function(a,b) {
					var a = a.date_maturity
					var b = b.date_maturity
					a = a.split('/').reverse().join('');
					b = b.split('/').reverse().join('');
					return a > b ? 1 : a < b ? -1 : 0;
					// return a.localeCompare(b); // <-- alternative 
					});
				var mv_line_id = date_sort[0].id;
				// console.log("TESTEST", date_sort[0].name, payment_id)
				var account_move_line_id = self.get_payment_allocation_account_move_id(payment_id);
				var account_move_line = Promise.all([account_move_line_id]).then((amresults) =>{
					var am_id = amresults[0];
					// var find_id = date_sort.find(date_sort[0].id == am_id);
					// console.log("PAYMENT ID", mv_line_id, am_id)
					for (var x = 0; x < recs_count; x++) {
						if (date_sort[0].amount > 0){
							// console.log("DATE SORT", date_sort.length)
							this.trigger_up('add_proposition', {'data': mv_line_id});
							break;
						}else if (date_sort[0].amount < 0){
							// console.log("TEST OLD INVOICE FIRST", date_sort)
							this.trigger_up('add_proposition', {'data': mv_line_id});
							break;
						}else {
							// console.log("ELSE STATEMENT")
							// this.trigger_up('add_proposition', {'data': mv_line_id});
							continue;
						}
					}
					// console.log("ACCOUNT MOVE", account_move_line, am_id)
				});

			// High Amount first
			}else if (pr == 'high_amount' && stateMvLines.length != 0){
				var high_amount_sort_debit = stateMvLines.slice().sort((a, b) => b.debit - a.debit);
				var high_amount_sort_credit = stateMvLines.slice().sort((a, b) => b.credit - a.credit);
				// console.log("TEST HIGH AMOUNT FIRST", high_amount_sort_debit)
				if (high_amount_sort_debit[i].credit <= 0) {
					// console.log("PAYMENT")
					var mv_line_id2 = high_amount_sort_debit[i].id;
					this.trigger_up('add_proposition', {'data': mv_line_id2});
				} else if (high_amount_sort_credit[i].debit <= 0) {
					// console.log("INVOICE")
					var mv_line_id3 = high_amount_sort_credit[i].id;
					this.trigger_up('add_proposition', {'data': mv_line_id3});
				}
			// Low amount first
			}else if (pr == 'low_amount' && stateMvLines.length != 0) {
				var low_amount_sort_debit = stateMvLines.slice().sort((a, b) => a.debit - b.debit);
				var low_amount_sort_credit = stateMvLines.slice().sort((a, b) => a.credit - b.credit);
				// console.log("TEST LOW AMOUNT FIRST", low_amount_sort_debit)
				if (low_amount_sort_debit[i].amount < 0) {
					// console.log("INVOICE")
					var mv_line_id4 = low_amount_sort_debit[i].id;
					this.trigger_up('add_proposition', {'data': mv_line_id4});
				} else if (low_amount_sort_credit[i].amount > 0) {
					// console.log("PAYMENT")
					var mv_line_id5 = low_amount_sort_credit[i].id;
					this.trigger_up('add_proposition', {'data': mv_line_id5});
				}
			// Manual
			}else if (pr == 'manual' && stateMvLines.length != 0) {
				var invoice_lines = self.get_payment_allocation_invoice_lines(payment_id);
				var invoice_lines_ids = Promise.all([invoice_lines]).then((ilidresults) =>{
					var il_id = ilidresults[0];
					// console.log("MANUAL1111", il_id)
					var payment_invoice = self.get_payment_allocation_invoice_ids(il_id);
					var pa_invoice = Promise.all([payment_invoice]).then((paidresults) =>{
						var pail_id = paidresults[0];
						// console.log("MANUAL2222", pail_id)
						var account_move_line = self.get_invoices_account_move_lines(pail_id);
						var aml = Promise.all([account_move_line]).then((amlidresults) =>{
							var aml_id = amlidresults[0];
							console.log("MANUAL3333", aml_id)
							// for (let x = 0; x < recs_count; x++) {
							// console.log("MANUAL4444", stateMvLines[0].id)
							var manual_sort = aml_id.slice().sort((a, b) => a.index - b.index);
							if (stateMvLines[0].amount < 0){
								for (let i = 0; i < manual_sort.length; i++) {
									if (manual_sort[i].id){
										console.log("MANUAL4444", manual_sort[i].id)
										console.log("MANUAL4444222", stateMvLines[0].id)
										// console.log("INVOICE", aml_id[i], stateMvLines[0].amount)
										this.trigger_up('add_proposition', {'data': manual_sort[i].id});
									}
								}
							}else if (stateMvLines[0].amount > 0) {
								// console.log("PAYMENT", stateMvLines[0].amount)
								this.trigger_up('add_proposition', {'data': stateMvLines[0].id});
							}
							// }
						}
					)});
				});
			}
		});


		// balance
		this.$('.popover').remove();
		this.$('table tfoot').html(qweb.render("reconciliation.line.balance", {'state': state}));

		// create form
		if (state.createForm) {
			var createPromise;
			if (!this.fields.account_id) {
				createPromise = this._renderCreate(state);
			}
			Promise.resolve(createPromise).then(function(){
				var data = self.model.get(self.handleCreateRecord).data;
				return self.model.notifyChanges(self.handleCreateRecord, state.createForm)
					.then(function () {
					// FIXME can't it directly written REPLACE_WITH ids=state.createForm.analytic_tag_ids
						return self.model.notifyChanges(self.handleCreateRecord, {analytic_tag_ids: {operation: 'REPLACE_WITH', ids: []}})
					})
					.then(function (){
						var defs = [];
						_.each(state.createForm.analytic_tag_ids, function (tag) {
							defs.push(self.model.notifyChanges(self.handleCreateRecord, {analytic_tag_ids: {operation: 'ADD_M2M', ids: tag}}));
						});
						return Promise.all(defs);
					})
					.then(function () {
						return self.model.notifyChanges(self.handleCreateRecord, {tax_ids: {operation: 'REPLACE_WITH', ids: []}})
					})
					.then(function (){
						var defs = [];
						_.each(state.createForm.tax_ids, function (tag) {
							defs.push(self.model.notifyChanges(self.handleCreateRecord, {tax_ids: {operation: 'ADD_M2M', ids: tag}}));
						});
						return Promise.all(defs);
					})
					.then(function () {
						var record = self.model.get(self.handleCreateRecord);
						_.each(self.fields, function (field, fieldName) {
							if (self._avoidFieldUpdate[fieldName]) return;
							if (fieldName === "partner_id") return;
							if ((data[fieldName] || state.createForm[fieldName]) && !_.isEqual(state.createForm[fieldName], data[fieldName])) {
								field.reset(record);
							}
							if (fieldName === 'tax_ids') {
								if (!state.createForm[fieldName].length || state.createForm[fieldName].length > 1) {
									$('.create_force_tax_included').addClass('d-none');
								}
								else {
									$('.create_force_tax_included').removeClass('d-none');
									var price_include = state.createForm[fieldName][0].price_include;
									var force_tax_included = state.createForm[fieldName][0].force_tax_included;
									self.$('.create_force_tax_included input').prop('checked', force_tax_included);
									self.$('.create_force_tax_included input').prop('disabled', price_include);
								}
							}
						});
						if (state.to_check) {
							// Set the to_check field to true if global to_check is set
							self.$('.create_to_check input').prop('checked', state.to_check).change();
						}
						return true;
					});
			});
		}
		this.$('.create .add_line').toggle(!!state.balance.amount_currency);
		},

		// Get the payment allocation mode of active payment form
		get_payment_allocation_mode: function(payment_id){
			var model = 'account.payment';
			var domain = [];
			var fields = ['id','allocation_mode'];
			var allocation_mode = '';

			return rpc.query({
				model: model,
				method: 'search_read',
				args: [domain, fields],
			}).then(function(data){
				for(var i in data){
					// console.log("ALLOCATION MODE FUNCTION")
					if(data[i].id == payment_id){
						allocation_mode = data[i].allocation_mode;
						// break;
					};
				};
				return allocation_mode;
			});

		},
		// Get the account move line id of active payment form
		get_payment_allocation_account_move_id: function(payment_id){
			var model = 'account.move.line';
			var domain = [];
			var fields = ['id','payment_id','credit'];
			var account_move_line_id = '';

			return rpc.query({
				model: model,
				method: 'search_read',
				args: [domain, fields],
			}).then(function(data){
				for(var i in data){
					// console.log("ACCOUNT MOVE LINE FUNCTION 1111", data[i].payment_id, data[i].credit)
					if(data[i].payment_id[0] == payment_id && data[i].credit > 0){
						// console.log("ACCOUNT MOVE LINE FUNCTION 2222", data[i].payment_id[0], data[i].credit, data[i].id)
						account_move_line_id = data[i].id;
						// break;
					};
				};
				return account_move_line_id;
			});

		},

		get_payment_allocation_invoice_lines: function(payment_id){
			var model = 'account.payment';
			var domain = [];
			var fields = ['id','invoice_line'];
			var invoice_line_id = '';

			return rpc.query({
				model: model,
				method: 'search_read',
				args: [domain, fields],
			}).then(function(data){
				for(var i in data){
					if(data[i].id == payment_id){
						invoice_line_id = data[i].invoice_line;
						// break;
					};
				};
				return invoice_line_id;
			});

		},

		get_payment_allocation_invoice_ids: function(il_id){
			var model = 'payment.allocation.line';
			var domain = [];
			var fields = ['id','invoice'];
			var invoice_line_id = [];

			return rpc.query({
				model: model,
				method: 'search_read',
				args: [domain, fields],
			}).then(function(data){
				for(var i in data){
					// console.log("PAL", data[i].id)
					for (let y = 0; y < il_id.length; y++) {
						if(data[i].id === il_id[y]){
							// console.log("PAL222", invoice_line_id)
							invoice_line_id.push(data[i].invoice[0]);
							// break;
					};
					}
				};
				return invoice_line_id;
			});

		},

		get_invoices_account_move_lines: function(pail_id){
			var model = 'account.move.line';
			var domain = [];
			var fields = ['id','move_id','debit'];
			var account_move_line_id = [];

			return rpc.query({
				model: model,
				method: 'search_read',
				args: [domain, fields],
			}).then(function(data){
				for(var i in data){
					for (let z = 0; z < pail_id.length; z++){
						if(data[i].move_id[0] === pail_id[z] && data[i].debit > 0){
							// console.log("PAIL ID2222", account_move_line_id, z, pail_id[z], data[i].move_id[0])
							account_move_line_id.push({id: data[i].id, index: z});
							// break;
						}
					};
				};
				return account_move_line_id;
			});

		},

	})
		

})
	


