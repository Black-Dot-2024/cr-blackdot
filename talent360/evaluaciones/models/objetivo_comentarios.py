from odoo import fields, models, api, exceptions, _

class ObjetivoComentarios(models.Model):
    """
    Modelo para representar los comentarios por parte del evaluador de un objetivo en Odoo

    :param _name(str): Nombre del modelo en Odoo
    :param _description (str): Descripción del modelo en Odoo
    :param objetivo_id (fields.Many2One): Relación con el objetivo
    :param fecha (fields.Date): Fecha del comentario
    :param comentarios (fields.Text): Comentarios del evaluador
    """

    _name = "objetivo.comentarios"
    _description = "Objetivo Comentarios"

    objetivo_id = fields.Many2one("objetivo", string="Objetivo", required=True, ondelete="cascade")
    fecha = fields.Date(required=True)
    opcion = fields.Selection([
        ("aceptar", "Aceptado"),
        ("rechazar", "Rechazado"),
    ], string="Estatus")
    comentarios_evaluador = fields.Text(string="Comentarios")
