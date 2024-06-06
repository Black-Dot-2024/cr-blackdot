from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
import base64
import csv
from io import StringIO


class UsuarioExterno(models.Model):
    """
    Modelo para representar a un usuario externo en Odoo.

    :param _name (str): Nombre del modelo en Odoo.
    :param _description (str): Descripción del modelo en Odoo.
    :param nombre (fields.Char): Nombre completo del usuario externo. Es un campo obligatorio.
    :param email (fields.Char): Correo electrónico del usuario externo. Es un campo obligatorio.
    :param puesto (fields.Char): Puesto del usuario externo.
    :param nivel_jerarquico (fields.Char): Nivel jerárquico del usuario externo.
    :param departamento (fields.Char): Departamento del usuario externo.
    :param gerencia (fields.Char): Gerencia del usuario externo.
    :param jefatura (fields.Char): Jefatura del usuario externo.
    :param genero (fields.Char): Género del usuario externo.
    :param fecha_ingreso (fields.Date): Fecha de ingreso del usuario externo.
    :param fecha_nacimiento (fields.Date): Fecha de nacimiento del usuario externo.
    :param region (fields.Char): Ubicación o región del usuario externo.
    :param evaluacion_ids (fields.Many2many): Relación de muchos a muchos con el modelo 'evaluacion' para asignar evaluaciones al usuario externo.
    """

    _name = "usuario.externo"
    _description = "Usuarios externos a la plataforma. Se utiliza para que puedan responer encuestas sin tener un usuario"
    _rec_name = "nombre"

    nombre = fields.Char(required=True)
    email = fields.Char(string="Correo electrónico", required=True)
    puesto = fields.Char()
    departamento = fields.Char(string="Departamento")
    genero = fields.Char(string="Género")
    fecha_nacimiento = fields.Date(string="Fecha de nacimiento")
    atributos_extra_ids = fields.One2many(
        "atributos.extra", "usuario_externo_id", string="Atributos Extra"
    )

    evaluacion_ids = fields.Many2many(
        "evaluacion",
        "usuario_evaluacion_rel",
        "usuario_externo_id",
        "evaluacion_id",
        string="Evaluaciones",
    )

    def ver_respuestas_usuario_externo(self):
        """
        Esta función busca las respuestas de un usuario externo para una evaluación específica. Si encuentra respuestas, muestra una ventana con las respuestas del usuario. Si no encuentra respuestas o si el usuario está asignado a la evaluación varias veces, lanza un error.
        """

        evaluacion_id = self._context.get("actual_evaluacion_id")

        usuario_evaluacion_rel = self.env["usuario.evaluacion.rel"].search(
            [
                ("evaluacion_id.id", "=", evaluacion_id),
                ("usuario_externo_id.id", "=", self.id),
            ]
        )

        if not usuario_evaluacion_rel:
            raise ValidationError(
                _("No se encontraron respuestas para el usuario seleccionado. test")
            )

        if len(usuario_evaluacion_rel) > 1:
            raise ValidationError(
                _(
                    "El usuario seleccionado está asognado a la evaluación multiples veces. Por favor contactar a un administrador."
                )
            )

        token = usuario_evaluacion_rel.token

        respuesta_ids = self.env["respuesta"].search(
            [
                ("evaluacion_id.id", "=", evaluacion_id),
                ("token", "=", token),
            ]
        )

        if respuesta_ids:
            return {
                "type": "ir.actions.act_window",
                "name": "Respuestas del usuario",
                "res_model": "respuesta",
                "view_mode": "tree",
                "domain": [
                    ("evaluacion_id", "=", evaluacion_id),
                    ("token", "=", token),
                ],
            }
        else:
            raise ValidationError(
                _("No se encontraron respuestas para el usuario seleccionado.")
            )

    def obtener_datos_demograficos(self):
        """
        Obtiene los datos demográficos de un usuario externo.

        :return: Un diccionario con los datos demográficos del usuario externo. Incluye nombre, género, puesto, año de nacimiento, generación y departamento.
        """

        datos = {}
        datos["nombre"] = self.nombre if self.nombre else "N/A"
        datos["genero"] = self.genero.capitalize() if self.genero else "N/A"
        datos["puesto"] = self.puesto if self.puesto else "N/A"
        datos["anio_nacimiento"] = (
            self.fecha_nacimiento.year if self.fecha_nacimiento else "N/A"
        )
        datos["generacion"] = (
            self.obtener_generacion(datos["anio_nacimiento"])
            if datos["anio_nacimiento"] != "N/A"
            else "N/A"
        )
        datos["departamento"] = self.departamento if self.departamento else "N/A"

        datos.update(self._obtener_atributos_extra())

        return datos

    def _obtener_atributos_extra(self):
        """
        Obtiene los atributos extra de un usuario externo.

        :return: Un diccionario con los atributos extra del usuario externo.
        """
        atributos = list(map(lambda atributo: atributo["nombre"], self.obtener_atributos()[6:]))
        atributos_extra = {}

        for atributo in self.atributos_extra_ids:
            if atributo.nombre in atributos:
                atributos_extra[atributo.nombre] = atributo.valor
                # Elimiar el atributo de la lista para no repetirlo
                atributos.remove(atributo.nombre)
        
        # Agregar los atributos faltantes con valor N/A
        for atributo in atributos:
            atributos_extra[atributo] = "N/A"

        return atributos_extra

    @api.model
    def obtener_generacion(self, anio_nacimiento):
        """
        Obtiene la generación a la que pertenece una persona de acuerdo al año de nacimiento.
        :param anio_nacimiento: El año de nacimiento de la persona.

        :return: La generación a la que pertenece la persona.
        """

        if 1946 <= anio_nacimiento <= 1964:
            return "Baby Boomers"
        elif 1965 <= anio_nacimiento <= 1980:
            return "Generación X"
        elif 1981 <= anio_nacimiento <= 1999:
            return "Millenials"
        elif 2000 <= anio_nacimiento <= 2015:
            return "Generacion Z"
        else:
            return "N/A"

    @api.model
    def obtener_atributos(self):
        """
        Obtiene los atributos de un usuario externo.

        :return: Un diccionario con los atributos del usuario externo.
        """

        atributos = [
            {"nombre": "Nombre Completo", "tipo": "char"},
            {"nombre": "Correo", "tipo": "char"},
            {"nombre": "Puesto", "tipo": "char"},
            {"nombre": "Departamento", "tipo": "char"},
            {"nombre": "Genero", "tipo": "char"},
            {"nombre": "Fecha de nacimiento", "tipo": "date"},
        ]

        atributos_extra = (
            self.env["res.company"]
            .browse(self.env.company.id)
            .employee_properties_definition
        )
        for atributo in atributos_extra:
            if atributo["type"] in ["separator", "many2one", "many2many", "tags"]:
                continue
            atributos.append({"nombre": atributo["string"], "tipo": atributo["type"]})

        return atributos

    def cargar_csv(self, archivo):
        """
        Procesa un archivo CSV y crea usuarios externos en Odoo.
        """
        lector_csv = None
        try:
            contenidos = base64.b64decode(archivo)
            archivo = StringIO(contenidos.decode("utf-8"))
            lector_csv = csv.DictReader(archivo)
            filas = list(lector_csv)

        except Exception as e:
            raise ValidationError(
                _(f"Error al procesar el archivo: {str(e)}. Verifica que el archivo sea un CSV válido.")
            )

        campos = self.env["usuario.externo"].obtener_atributos()
        campos_obligatorios = campos[:6]
        campos_opcionales = campos[6:]

        usuarios = []

        self._validar_columnas(
            lector_csv.fieldnames,
            [c["nombre"] for c in campos_obligatorios],
            [c["nombre"] for c in campos_opcionales],
        )

        if len(filas) >= 50000:
            raise ValidationError(
                _("Error: No se pueden cargar más de 50,000 usuarios.")
            )

        for fila in filas:
            usuario = self._construir_usuario(
                fila, campos_obligatorios, campos_opcionales
            )

            usuarios.append(usuario)

        return usuarios

    @api.model
    def _validar_columnas(
        self,
        columnas: list[str],
        campos_obligatorios,
        campos_opcionales,
    ):
        """
        Valida que las columnas del archivo CSV sean las correctas
        """

        columnas_faltantes = []
        columnas_duplicadas = []
        columnas_extra = []

        for columna in campos_obligatorios:
            if columna not in columnas:
                columnas_faltantes.append(columna)

            if columnas.count(columna) > 1:
                columnas_duplicadas.append(columna)

        for columna in columnas:
            if columna not in campos_obligatorios and columna not in campos_opcionales:
                columnas_extra.append(columna)

        mensaje = ""

        if columnas_faltantes:
            mensaje += f"Las siguientes columnas son requeridas: {', '.join(columnas_faltantes)}\n"

        if columnas_duplicadas:
            mensaje += f"Las siguientes columnas están duplicadas: {', '.join(columnas_duplicadas)}\n"

        if columnas_extra:
            mensaje += f"Las siguientes columnas no son soportadas: {', '.join(columnas_extra)}\n"

        if mensaje:
            raise ValidationError(_(mensaje))

    @api.model
    def _construir_usuario(self, fila: dict, campos_obligatorios, campos_opcionales):
        """
        Construye un usuario externo a partir de una fila de un archivo CSV.
        """

        for campo, valor in fila.items():
            cadena = valor.strip()
            if cadena and len(cadena) > 0:
                fila[campo] = cadena
            else:
                fila[campo] = "N/A"

        for campo in map(lambda c: c["nombre"], campos_obligatorios):
            if not fila.get(campo):
                raise ValidationError(
                    _(f"El campo {campo} es requerido. Por favor verifica que todos los campos obligatorios estén presentes.")
                )

        try:
            fecha_nacimiento = datetime.strptime(
                fila["Fecha de nacimiento"], "%d/%m/%Y"
            ).date()
        except ValueError:
            raise ValidationError(
                _("El formato de las fechas debe ser dd/mm/yyyy. Verifica las fechas.")
            )

        usuario = {
            "nombre": fila["Nombre Completo"],
            "email": fila["Correo"],
            "puesto": fila["Puesto"],
            "departamento": fila["Departamento"],
            "genero": fila["Genero"],
            "fecha_nacimiento": fecha_nacimiento,
        }

        atributos_extra = []
        for campo in campos_opcionales:
            nombre = campo["nombre"]
            tipo = campo["tipo"]
            valor = fila.get(nombre, "N/A")

            if tipo == "boolean":
                if valor != "N/A":
                    valor = "Si" if valor.lower() == "si" else "No"

            self._validar_campo(campo, valor)


            atributo = {
                "nombre": nombre,
                "tipo": tipo,
                "valor": valor,
            }

            atributos_extra.append(atributo)

        usuario_externo_id = self.env["usuario.externo"].create(usuario)
        atributos_extra_ids = self.env["atributos.extra"].create(atributos_extra)

        usuario_externo_id.write(
            {"atributos_extra_ids": [(6, 0, atributos_extra_ids.ids)]}
        )

        return usuario_externo_id

    def _validar_campo(self, campo, valor):
        """
        Valida que el valor de un campo sea correcto de acuerdo a su tipo.
        """
        
        if campo["tipo"] == "char":
            return
        elif campo["tipo"] == "boolean":
            if valor.lower() not in ["si", "no", "n/a"]:
                raise ValidationError(
                    _(f"El campo {campo['nombre']} debe ser 'Si' o 'No'.")
                )
        elif campo["tipo"] == "integer":
            try:
                if float(valor) % 1 != 0:
                    raise ValidationError(
                        _(f"El campo {campo['nombre']} debe ser un número entero.")
                    )
            except ValueError:
                raise ValidationError(
                _(f"El campo {campo['nombre']} debe ser un número entero.")
                )
        elif campo["tipo"] == "float":
            try:
                float(valor)
            except ValueError:
                raise ValidationError(
                    _(f"El campo {campo['nombre']} debe ser un número decimal separado con punto '.'")
                )
        elif campo["tipo"] == "date":
            try:
                datetime.strptime(valor, "%d/%m/%Y")
            except ValueError:
                raise ValidationError(
                    _(f"El campo {campo['nombre']} debe ser una fecha en formato dd/mm/yyyy.")
                )
        elif campo["tipo"] == "datetime":
            try:
                datetime.strptime(valor, "%d/%m/%Y %H:%M:%S")
            except ValueError:
                raise ValidationError(
                    _(f"El campo {campo['nombre']} debe ser una fecha en formato dd/mm/yyyy hh:mm:ss.")
                )
        elif campo["tipo"] == "selection":
            return
        


class AtributosExtra(models.Model):
    """
    Modelo para representar los atributos extra de un usuario externo en Odoo.

    :param _name (str): Nombre del modelo en Odoo.
    :param _description (str): Descripción del modelo en Odoo.
    :param nombre (fields.Char): Nombre del atributo extra. Es un campo obligatorio.
    :param tipo (fields.Selection): Tipo de atributo extra. Es un campo obligatorio.
    :param valor (fields.Char): Valor del atributo extra.
    :param usuario_externo_id (fields.Many2one): Relación de muchos a uno con el modelo 'usuario.externo' para asignar un atributo extra a un usuario externo.
    """

    _name = "atributos.extra"
    _description = "Atributos extra de los usuarios externos"
    _rec_name = "nombre"

    nombre = fields.Char(required=True)
    tipo = fields.Char(required=True)
    valor = fields.Char(required=True, default="N/A")
    usuario_externo_id = fields.Many2one("usuario.externo", string="Usuario Externo")
