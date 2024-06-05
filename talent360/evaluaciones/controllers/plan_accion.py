from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError
import requests
import json

class PlanAccion(http.Controller):
    """Controlador para manejar las solicitudes relacionadas con los planes de acción."""
    
    @http.route("/plan_accion/guardar/<int:evaluacion_id>", type="json", auth="user", methods=['POST'], website=True)
    def guardar_plan_accion(self, evaluacion_id, **post):
        """
        Método para actualizar el plan de acción en la base de datos.
        
        :param evaluacion_id: ID de la evaluación para la cual se actualiza el plan.
        :return: Mensaje de confirmación o error.
        """
        data = json.loads(request.httprequest.data)
        plan = data.get("plan_accion")
        plan_accion_modelo = request.env['plan.accion']
        
        plan_accion_modelo.sudo().guardar_plan_accion_action(evaluacion_id, plan)


    @http.route("/plan_accion/reporte/<model('evaluacion'):evaluacion>", type="http", auth="user")
    def generar_plan_action(self, evaluacion):
        """
        Método para obtener texto de prueba.
        Este método obtiene texto de prueba de la API corporatelorem.kovah.de.
        
        :param paragraphs: cantidad de párrafos a obtener
        
        :return: texto de prueba obtenido de la API
        """
        
        plan_accion_modelo = request.env["plan.accion"]
        url = "https://corporatelorem.kovah.de/api/3"
        evaluacion_id = evaluacion.id
        prompt = self.generar_prompt(evaluacion)
        
        respuesta = requests.get(str(url))

        if respuesta.status_code == 200:
            data = respuesta.json()
            
            titulo = data["source"]
            
            parrafos = "".join(data["paragraphs"])
            
            parrafos = parrafos.replace("<p>", "").replace("</p>", "")
            
            plan = titulo + "\n\n" + parrafos
            
            plan_accion_modelo.sudo().guardar_plan_accion_action(int(evaluacion_id), plan)
            
            return plan
        else :
            raise ValidationError(_("Error al obtener el plan de acción"))


    def generar_prompt(self, evaluacion):
        """
        Método para generar y un plan de acción.
        Este método genera un mensaje con las preguntas y respuestas de la evaluación para luego
        enviarlo a la IA que generará un plan de acción.
        
        :param evaluacion: objeto de la evaluación a generar el plan de acción

        :return: texto con el plan de acción generado por la IA
        """

        if not request.env.user.has_group(
            "evaluaciones.evaluaciones_cliente_cr_group_user"
        ):
            raise AccessError(_("No tienes permitido acceder a este recurso."))

        parametros = evaluacion.generar_datos_reporte_generico_action()
        
        mensaje = "[CONTENIDO DEL MENSAJE A LA IA]. Usar el siguiente CSV: Pregunta,Respuesta"
        
        for pregunta in parametros["preguntas"]:
            mensaje += "\n" + str(pregunta["pregunta"].pregunta_texto) + ","
            for respuesta in pregunta["respuestas"]:
                mensaje += str(respuesta) + ","
                
        return mensaje

