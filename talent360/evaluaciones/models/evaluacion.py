from odoo import models, fields


class Evaluacion(models.Model):
    """ 
    Modelo para representar una evaluación de personal en Odoo.

    :param _name (str): Nombre del modelo en Odoo.
    :param _description (str): Descripción del modelo en Odoo.
    :param nombre (fields.Char): Nombre de la evaluación. Es un campo obligatorio.
    :param estado (fields.Selection): Estado de la evaluación con opciones 'borrador', 'publicado' y 'finalizado'. Por defecto, es 'borrador'.
    :param pregunta_ids (fields.Many2many): Relación de muchos a muchos con el modelo 'pregunta' para almacenar las preguntas asociadas a la evaluación.
    :param competencia_ids (fields.Many2many): Relación de muchos a muchos con el modelo 'competencia' para almacenar las competencias asociadas a la evaluación.
    :param usuario_ids (fields.Many2many): Relación de muchos a muchos con el modelo 'res.users' para asignar usuarios a la evaluación.
    """

    _name = "evaluacion"
    _description = "Evaluacion de pesonal"
    _inherit = "mail.thread"

    nombre = fields.Char(required=True)
    estado = fields.Selection(
        [
            ("borrador", "Borrador"),
            ("publicado", "Publicado"),
            ("finalizado", "Finalizado"),
        ],
        default="borrador",
        required=True,
    )

    pregunta_ids = fields.Many2many(
        "pregunta",
        "pregunta_evaluacion_rel",
        "evaluacion_id",
        "pregunta_id",
        string="Preguntas",
    )

    competencia_ids = fields.Many2many(
        "competencia",
        "competencia_evaluacion_rel",
        "evaluacion_id",
        "competencia_id",
        string="Competencias",
    )

    usuario_ids = fields.Many2many(
        "res.users",
        "usuario_evaluacion_rel",
        "evaluacion_id",
        "usuario_id",
        string="Asignados",
    )
    
    def enviar_evaluacion(self):
        """
        Envía la evaluación a los usuarios asignados y cambia el estado de la evaluación a 'publicado'.

        Este método se encarga de iterar por el campo 'usuario_ids' y enviar un mensaje a cada usuario asignado con la evaluación que se ha asignado. Además, cambia el estado de la evaluación a 'publicado'. El mensaje enviado contiene los detalles de la evaluación asignada y los usuarios que fueron asignados.
        """
        usuarios = []

        for usuario in self.usuario_ids:
            self.message_post(
                body=f"Se te ha asignado la evaluación: {self.nombre}",
                partner_ids=[usuario.partner_id.id],
            )
            usuarios.append(usuario.partner_id.name)
        
        self.estado = "publicado"

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "¡Has enviado una evaluación!",
                "type": "success",
                "message": f"Se ha asignado la evaluación {self.nombre} a {', '.join(usuarios)}",
                "sticky": False,
            }
        }