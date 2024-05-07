from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError
from ..models.evaluacion import Evaluacion


class EvaluacionesController(http.Controller):
    """Controlador para manejar las solicitudes relacionadas con las evaluaciones."""

    @http.route(
        "/evaluacion/reporte/<model('evaluacion'):evaluacion>", type="http", auth="user"
    )
    def reporte_controller(self, evaluacion: Evaluacion):
        """Método para generar y mostrar un reporte de evaluación.
        Este método verifica que el usuario tenga los permisos necesario, obtiene los datos
        del modelo de evaluaciones y renderiza el reporte con esos datos.

        :return: html renderizado del template con los datos del reporte
        """

        if not request.env.user.has_group(
            "evaluaciones.evaluaciones_cliente_cr_group_user"
        ):
            raise AccessError("No tienes permitido acceder a este recurso.")

        parametros = evaluacion.action_generar_datos_reporte_NOM_035()

        return request.render("evaluaciones.encuestas_reporte", parametros)
    
    def reporte_clima_controller(self, evaluacion: Evaluacion):
        """Método para generar y mostrar el reporte de clima laboral.
        :return: HTML renderizado del template con los datos del reporte.
        """
        
        #Verificar permisos de usuario
        if not request.env.user.has_group("evaluaciones.evaluaciones_cliente_cr_group_user"):
            raise AccessError("No tienes permitido acceder a este recurso.")
        
        #Generar parámetros para el reporte
        parametros = evaluacion.action_generar_datos_reporte_clima() 
        
        return request.render("evaluaciones.encuestas_reporte_clima", parametros)
