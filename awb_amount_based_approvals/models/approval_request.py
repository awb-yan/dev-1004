# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    has_department = fields.Selection(related='category_id.has_department')
    has_manager = fields.Selection(related='category_id.has_manager')
    department_id = fields.Many2one('hr.department', String='Department')
    manager_id = fields.Many2one('hr.employee', String='Manager')
    can_approve = fields.Boolean(string='Can Approve', default=False, compute='_check_can_approve')

    @api.onchange('request_owner_id')
    def _onchange_request_owner(self):
        for record in self:
            request_owner = record.request_owner_id.mapped('employee_ids').filtered(lambda x: x.company_id == record.company_id)
            department = False
            for owner in request_owner:
                department = owner.department_id
            record.department_id = department

    @api.onchange('department_id')
    def _onchange_department(self):
        for record in self:
            request_owner = record.request_owner_id.mapped('employee_ids').filtered(lambda x: x.company_id == record.company_id)
            manager = False
            if request_owner:
                for owner in request_owner:
                    if record.department_id == owner.department_id:
                        manager = owner.parent_id
                    else:
                        manager = record.department_id.manager_id
            else:
                manager = record.department_id.manager_id
            record.manager_id = manager

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount:
                if record.amount < 0 :
                    raise UserError(_('Amount must be greater than 0'))

    @api.depends('approver_ids.status','approver_ids.can_approve')
    def _check_can_approve(self):
        for approval in self:
            approval.can_approve = approval.approver_ids.filtered(lambda approver: approver.user_id == self.env.user).can_approve

    def _get_data_approvers(self, head_id, req_id, sequence, app_condition ,add_seq=0):
        data = {
            'user_id': head_id,
            'request_id': req_id,
            'approval_condition': app_condition,
            'sequence': sequence + add_seq ,
        }
        _logger.debug(f'Approvers: {data}')
        return data

    def _approval_checker(self, owner, *approvers_list):
        for approvers in approvers_list:
            for approver in approvers:
                if approver == owner:
                    raise UserError(_('Request owner must not be one of the approver'))
                if approvers.count(approver) > 1:
                    raise UserError(_('Duplicate User found in this approvers'))
        return True

    def action_confirm(self):
        data_approvers = []
        add_sequence = 1

        manager_id = self.mapped('manager_id').user_id.id
        head_id = self.mapped('department_id').operation_head.user_id.id
        users = [manager_id, head_id]

        approval_rule = False
        new_args = [
            ('category', '=', self.category_id.id)
        ]
        new_approval = self.sudo().env['approval.rule'].search(new_args)
        for rule in new_approval:
            if rule.approval_type == 'none':
                approval_rule = rule
            else:
                if rule.min_amount <= self.amount and rule.max_amount >= self.amount:
                    approval_rule = rule

        if not approval_rule:
            raise UserError(_('Approval Request cannot be proceed. Please Contact your System Administrator'))
        
        category = self.mapped('category_id')
        rule = category.rule_ids.filtered(lambda rule: rule.id == approval_rule.id)
        if not rule:
            raise UserError(_('Approval Request cannot be proceed. Please Contact your System Administrator'))

        if rule.manager_id:
            if manager_id:
                data = self._get_data_approvers(manager_id, self.id, add_sequence, 'and')
                data_approvers.append((0, 0, data))
                add_sequence += 1
            else:
                raise UserError(_('You need to set User Account to Manager to Proceed'))
        if rule.operation_head_id:
            if head_id:
                data = self._get_data_approvers(head_id, self.id, add_sequence, 'and')
                data_approvers.append((0, 0, data))
                add_sequence += 1
            else:
                raise UserError(_('You need to set User Account to Operations Head to Proceed'))
        if rule.approver_ids:
            for approval in rule.approver_ids:
                for approver in approval.approved_by:
                    if approver:
                        data = self._get_data_approvers(approver.id, self.id, approval.sequence, approval.approval_condition)
                        data_approvers.append((0, 0, data))
                        users.append(approver.id)

        checker = self._approval_checker(self.request_owner_id.id, users)
        if checker:
            self.sudo().update({'approver_ids': [(5,0,0)]})
            self.sudo().update({'approver_ids': data_approvers})

            for sequence in range(1,len(self.approver_ids)+1):
                _logger.debug(f'Sequence: {sequence}')
                _logger.debug(f'Length: {len(self.approver_ids)}')
                seq_approver = self.mapped('approver_ids').filtered(lambda seq: seq.sequence == sequence)
                if all(line.sequence == 1 for line in seq_approver):
                    seq_approver.write({'can_approve': True})
                    seq_approver._create_activity()
                if any(line.approval_condition == 'or' for line in seq_approver):
                    seq_approver.write({'approval_condition': 'or'})

        if len(self.approver_ids) < self.approval_minimum:
            raise UserError(_("You have to add at least %s approvers to confirm your request.") % self.approval_minimum)
        if self.requirer_document == 'required' and not self.attachment_number:
            raise UserError(_("You have to attach at lease one document."))
        approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new')
        # approvers._create_activity()
        approvers.write({'status': 'pending'})
        self.write({'date_confirmed': fields.Datetime.now()})
    
        res = super(ApprovalRequest, self).action_confirm()
        return res

    def action_approve(self):
        approver = self.mapped('approver_ids')

        current_approver = approver.filtered(lambda x: x.user_id == self.env.user)
        current_sequence = approver.filtered(lambda x: x.sequence == current_approver.sequence)

        if len(current_sequence) > 1:
            if any(line.approval_condition == 'or' for line in current_sequence):
                current_sequence.write({'status': 'approved'})

        pending_approvers = approver.filtered(lambda x: x.status == 'pending')  
        next_approver = next(iter(user for user in pending_approvers if not user.user_id == self.env.user), None)
        
        if next_approver is not None:
            approvers = approver.filtered(lambda x: x.sequence == next_approver.sequence)
            if len(approvers) > 1:
                approvers.write({'can_approve': True})
                approvers._create_activity()
            else: 
                next_approver.write({'can_approve': True})
                next_approver._create_activity()

        res = super(ApprovalRequest, self).action_approve()
        return res

    @api.depends('approver_ids.status')
    def _compute_request_status(self):
        for request in self:
            status_lst = request.mapped('approver_ids.status')
            # minimal_approver = request.approval_minimum if len(status_lst) >= request.approval_minimum else len(status_lst)
            if status_lst:
                if status_lst.count('cancel'):
                    status = 'cancel'
                elif status_lst.count('refused'):
                    status = 'refused'
                elif status_lst.count('new'):
                    status = 'new'
                elif all(line == 'approved' for line in status_lst):
                    status = 'approved'
                else:
                    status = 'pending'
            else:
                status = 'new'
            request.request_status = status

class ApprovalApprover(models.Model):
    _inherit = 'approval.approver'

    sequence = fields.Integer(string='Sequence', default=1, readonly=True)
    approval_condition = fields.Selection([('and', 'AND'), ('or', 'OR')], string='Condition', default='and')
    can_approve = fields.Boolean(string='Can Approve', default=False)
