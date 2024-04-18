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

    # do something on new usuario assigned

    def write(self, vals):
        res = super(Evaluacion, self).write(vals)
        if "usuario_ids" in vals:
            for user_change in vals["usuario_ids"]:
                action, user_id = user_change
                user = self.env["res.users"].browse(user_id)
                partner_id = user.partner_id.id
                if action == 4:
                    print(f"Se ha asignado la evaluación {self.nombre} a {partner_id}")
                    # Send email to assigned user
                    self.message_post(
                        body=f"Se te ha asignado la evaluación {self.nombre}",
                        partner_ids=[partner_id],
                    )
        return res
    
    
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