from odoo import models, fields

class Evaluacion(models.Model):
    _name = "evaluacion"
    _description = "Evaluacion de pesonal"

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
        # Creamos una lista para almacenar los nombres de los usuarios
        users = []

        # Enviamos un mensaje a cada usuario asignado
        for usuario in self.usuario_ids:
            self.message_post(
                body=f"Se te ha asignado la evaluación: {self.nombre}",
                partner_ids=[usuario.partner_id.id],
            )
            users.append(usuario.partner_id.name)
        
        self.estado = "publicado"

        # Mostrar una notificación con los usuarios a los que se les ha asignado la evaluación
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            'params': {
                'title': '¡Has enviado una evaluación!',
                'type': 'success',
                'message': f"Se ha asignado la evaluación {self.nombre} a {', '.join(users)}",
                'sticky': False,
            }
        }