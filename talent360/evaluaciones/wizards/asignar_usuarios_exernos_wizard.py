import base64
import csv
from io import StringIO

from odoo import fields, models, api, exceptions, _


class AsignarUsuariosExternosWizard(models.TransientModel):
    _name = "asignar.usuario.externo.wizard"

    archivo = fields.Binary()

    nombre_archivo = fields.Char()


    @api.constrains("nombre_archivo")
    def _validar_nombre_archivo(self):
        """
        Método para validar que el archivo cargado sea un archivo CSV
        """
        if self.nombre_archivo and not self.nombre_archivo.lower().endswith(".csv"):
            raise exceptions.ValidationError(_("Solo se aceptan archivos CSV."))

    def procesar_csv(self):
        """
        Método para procesar el archivo CSV y crear los usuarios externos
        """
        evaluacion = self.env["evaluacion"].browse(self._context.get("active_id"))

        if not evaluacion:
            raise exceptions.ValidationError(
                _("No se encontró la evaluación en el contexto.")
            )

        # Procesa el archivo CSV y crea los usuarios externos
        usuarios_db = self.env["usuario.externo"].cargar_csv(self.archivo)
        usuario_ids = [(4, usuario.id) for usuario in usuarios_db]
        evaluacion.write({"usuario_externo_ids": usuario_ids})
        

    def descargar_template_usuarios(self):
        """
        Método para generar y descargar el template de usuarios externos
        """

        atributos = self.env["usuario.externo"].obtener_atributos()
        atributos_nombres = [atributo["nombre"] for atributo in atributos]

        datos = StringIO()

        escritor_csv = csv.writer(datos)

        escritor_csv.writerow(atributos_nombres)

        # "Nombre Completo", "Correo", "Puesto", "Departamento", "Genero", "Fecha de nacimiento"
        datos_prueba_base = ["Juan Perez", "juanperez@test.com", "Gerente", "Ventas", "Masculino", "01/01/1990"]

        idx = len(datos_prueba_base)

        for atributo in atributos[idx:]:
            if atributo["tipo"] == "char":
                datos_prueba_base.append("Texto")
            elif atributo["tipo"] == "boolean":
                datos_prueba_base.append("Si/No")
            elif atributo["tipo"] == "integer":
                datos_prueba_base.append("Número entero (1, 2, 3)")
            elif atributo["tipo"] == "float":
                datos_prueba_base.append("Número decimal separado por punto (1.2, 3.4)")
            elif atributo["tipo"] == "date":
                datos_prueba_base.append("Fecha (dd/mm/yyyy)")
            elif atributo["tipo"] == "datetime":
                datos_prueba_base.append("Fecha y hora (dd/mm/yyyy hh:mm:ss)")
            elif atributo["tipo"] == "selection":
                datos_prueba_base.append("Texto")
            else:
                datos_prueba_base.append("Datos de prueba (Texto)")

        escritor_csv.writerow(datos_prueba_base)

        datos = datos.getvalue()

        nombre_archivo = "template_usuarios_externos.csv"

        adjunto = self.env["ir.attachment"].search(
            [("name", "=", nombre_archivo), ("res_model", "=", self._name)], limit=1
        )

        if adjunto:
            adjunto.write({"datas": base64.b64encode(datos.encode("utf-8"))})
        else:
            adjunto = self.env["ir.attachment"].create(
                {
                    "name": nombre_archivo,
                    "type": "binary",
                    "datas": base64.b64encode(datos.encode("utf-8")),
                    "res_model": nombre_archivo,
                    "res_id": self.id,
                }
            )

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{str(adjunto.id)}?download=true",
            "target": "new",
        }
