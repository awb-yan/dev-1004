# TODO Helper Functions for Products


    def _compute_plan_type(self):
        for rec in self:
            plan_type_id = []
            for lines in rec.recurring_invoice_line_ids:
                if lines.product_id.product_tmpl_id.product_segmentation == 'month_service':
                    plan_type_id = lines.product_id.product_tmpl_id.sf_plan_type
                    # plan_type_result = self.env['product.plan.type'].search([('id','=',plan_type_id)])

            rec.plan_type = plan_type_id

    def _get_mainplan(self, record):
        _logger.info('function: get_mainplan')

        main_plan = ''

        for line_id in record.recurring_invoice_line_ids:
            if line_id.product_id.product_tmpl_id.product_segmentation == 'month_service':
                main_plan = line_id.product_id.product_tmpl_id
        
        if main_plan == '':
            raise Exception

        return main_plan  