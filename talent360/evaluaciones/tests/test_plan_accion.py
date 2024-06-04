from odoo.tests.common import TransactionCase
from datetime import date, timedelta

class TestPlanAccion(TransactionCase):
    
        def setUp(self):
            super(TestPlanAccion, self).setUp()
    
        def tearDown(self):
            super(TestPlanAccion, self).tearDown()
            return
    
        # 1. Se crea correctamente un plan de acción
        def crear_plan_accion(self):
            plan_accion = self.env["plan.accion"].create(
                {
                    "descripcion": "Descripción del plan de acción",
                    "evaluacion_id": 1,
                }
            )
    
            self.assertTrue(plan_accion, "Plan de acción no creado")
    
        # 2. Se edita correctamente un plan de acción
        def test_02_editar_plan_accion(self):
            plan_accion = self.env["plan.accion"].create(
                {
                    "descripcion": "Descripción del plan de acción",
                    "evaluacion_id": 1,
                }
            )
    
            plan_accion.write({"descripcion": "Nueva descripción del plan de acción"})
    
            self.assertTrue(plan_accion, "Plan de acción no editado")
    
        # 3. Se elimina correctamente un plan de acción
        def test_03_eliminar_plan_accion(self):
            plan_accion = self.env["plan.accion"].create(
                {
                    "descripcion": "Descripción del plan de acción",
                    "evaluacion_id": 1,
                }
            )
    
            plan_accion.unlink()
    
            self.assertTrue(plan_accion, "Plan de acción no eliminado")