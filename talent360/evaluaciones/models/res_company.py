import json
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    # Avoid creation of properties with duplicated names
    @api.constrains("employee_properties_definition")
    def _check_employee_properties_definition(self):
        """
        Función para verificar que no existan propiedades con nombres duplicados
        """

        for company in self:
            if company.employee_properties_definition:
                nombres = list(
                    map(
                        lambda parameter: parameter["string"],
                        company.employee_properties_definition,
                    )
                )
                if len(nombres) != len(set(nombres)):
                    raise ValidationError(
                        _("No se permiten propiedades con nombres duplicados")
                    )

    @api.model
    def configurar_datos_demograficos(self):
        """
        Función para configurar los datos demográficos de la empresa
        """
        atributos_nuevos = [
            {
                "name": "parametro1",
                "type": "char",
                "string": "Jefatura",
                "default": False,
            },
            {
                "name": "parametro2",
                "type": "selection",
                "string": "Area",
                "default": False,
                "selection": [
                    ["parametro2a", "1"],
                    ["parametro2b", "2"],
                    ["parametro2c", "3"],
                ],
            },
        ]
        for company in self.search([]):
            atributos_base = company.employee_properties_definition

            atributos_base_nombres = list(
                map(lambda parameter: parameter["string"], atributos_base)
            )

            atributos_base_ids = list(
                map(lambda parameter: parameter["name"], atributos_base)
            )

            for atributo_nuevo in atributos_nuevos:
                if (
                    atributo_nuevo["string"] not in atributos_base_nombres
                    and atributo_nuevo["name"] not in atributos_base_ids
                ):
                    atributos_base.append(atributo_nuevo)
            texto = json.dumps(atributos_base)
            company.write({'employee_properties_definition': texto})
