from odoo import fields, models, api, exceptions, _

class ObjetivoAvance(models.Model):
    """
    Modelo para representar un avance de un objetivo en Odoo

    :param _name(str): Nombre del modelo en Odoo
    :param _description (str): Descripción del modelo en Odoo
    :param objetivo_id (fields.Many2One): Relación con el objetivo
    :param fecha (fields.Date): Fecha del avance
    :param avance (fields.Integer): Avance del objetivo
    :param comentarios (fields.Text): Comentarios del avance
    :param archivos (fields.Many2Many): Archivos adjuntos al avance
    """
    
    _name = "objetivo.avances"
    _description = "Objetivo Avance"

    objetivo_id = fields.Many2one("objetivo", string="Objetivo", required=True, ondelete="cascade")
    fecha = fields.Date(string="Fecha", required=True)
    avance = fields.Integer(string="Avance", required=True)
    comentarios = fields.Text(string="Comentarios")
    archivos = fields.Many2many(comodel_name="ir.attachment", string="Archivos")
    comentarios_evaluador = fields.Text(string="Retroalimentación")
    estatus = fields.Selection(
        [
            ("aceptado", "Aceptado"),
            ("rechazado", "Rechazado")
        ],
        default="aceptado"
    )
    
    @api.depends('avance')
    def _compute_resultado(self):
        for objetivo in self:
            avances = self.search([('objetivo_id', '=', objetivo.objetivo_id.id)])
            objetivo.objetivo_id.resultado = sum(avance.avance for avance in avances)
