from odoo import fields, models, api, exceptions, _

class ModificarProgreso(models.TransientModel):
    """
    Modelo para registrar un avance de un objetivo de desempeño

    :param _name(str): Nombre del modelo en Odoo
    :param _description (str): Descripción del modelo en Odoo
    :param fecha (fields.Date): Fecha en la que se registra un progreso
    :param progreso (fields.Float): Progreso del objetivo
    :param comentarios (fields.Text): Comentarios del progreso
    """

    _name = "modificar.progreso.wizard"
    _description = "Modificar Progreso Wizard"

    fecha = fields.Date(default=fields.Date.today())
    progreso = fields.Float(
        required=True,
        help="Progreso del objetivo de desempeño. Debe ser un número positivo que represente el avance"
    )

    comentarios = fields.Text(
        required=True,
        help="Comentarios de retroalimentación del progreso registrado."
    )

    @api.constrains("progreso")
    def _validar_progreso(self):
        """
        Método para validar que el progreso no sea negativo

        Si el progreso es negativo, se levanta una excepción
        """

        for registro in self:
            if registro.progreso < 0:
                raise exceptions.ValidationError(_("El progreso no puede ser menor a 0"))
    
    @api.constrains("comentarios")
    def _validar_comentarios(self):
        """
        Método para validar que los comentarios no excedan las 500 palabras 

        o los 1500 caracteres. Si los comentarios exceden las 500 palabras, 
        
        se levanta una excepción.
        """

        for registro in self:
            if registro.comentarios:
                palabras = len(registro.comentarios.split())
                if palabras > 500:
                    raise exceptions.ValidationError(_("Los comentarios no deben exceder las 500 palabras"))
                if len(registro.comentarios) > 1500:
                    raise exceptions.ValidationError(_("Los comentarios no deben exceder los 1500 caracteres"))  
                
    def guardar_action(self):
        """
        Método para registrar las modificaciones al progreso de un objetivo de desempeño
        
        Se crea un registro en el modelo objetivo.progreso con los datos del progreso

        Se actualiza el campo resultado del objetivo con la suma del valor del avance
        """

        progreso = self.progreso
        comentarios = self.comentarios
        fecha = self.fecha
        objetivo_id = self.env.context.get("objetivo_id")
        usuario_objetivo = self.env["objetivo"].browse(objetivo_id)
        
        self.env["objetivo.progreso"].create({
            "objetivo_id": usuario_objetivo.id,
            "fecha": fecha,
            "progreso": progreso,
            "comentarios": comentarios,
        })
