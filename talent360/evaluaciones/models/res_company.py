from odoo import models, api, _
from odoo.exceptions import ValidationError

class ResCompany(models.Model):
    _inherit = 'res.company'

    # Avoid creation of properties with duplicated names
    @api.constrains('employee_properties_definition')
    def _check_employee_properties_definition(self):
        for company in self:
            if company.employee_properties_definition:
                nombres = list(map(lambda parameter: parameter["string"], company.employee_properties_definition))
                print(nombres)
                if len(nombres) != len(set(nombres)):
                    raise ValidationError(_("No se permiten propiedades con nombres duplicados"))