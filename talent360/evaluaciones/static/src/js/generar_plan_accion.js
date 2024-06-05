function generarPlanAccion() {
    console.log("generando plan")

    var evaluacion_id = document.querySelector('input[name="evaluacion_id"]').value;

    // Envía los valores a la base de datos
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/plan_accion/reporte/' + evaluacion_id, true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    var textarea = document.querySelector('#plan_accion_textarea');
    var guardarBtn = document.querySelector('button[onclick="guardarPlanAccion()"]');
    var generarBtn = document.querySelector('button[onclick="generarPlanAccion()"]');

    // Deshabilitar los botones
    guardarBtn.disabled = true;
    generarBtn.disabled = true;
    textarea.disabled = true;
    textarea.value = "Generando plan de accion...";
    
    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 400) {

            var response = xhr.responseText;
            
            guardarBtn.disabled = false;
            generarBtn.disabled = false;
            textarea.disabled = false;

            if (textarea) {
                textarea.value = response;
            } else {
                console.error("No se encontró el textarea con id 'plan_accion_textarea'");
            }
        } else {

            // Errores del request
            console.error("Error en la solicitud: " + xhr.status);
        }
    };

    xhr.onerror = function() {
        // Aquí manejas los errores de la conexión
        console.error("Error de conexión");
    };

    xhr.send();


}

function Alturatextarea(textarea) {
    // Reset the height so that the scrollHeight is correctly calculated
    textarea.style.height = 'auto';
    // Set the height to match the scrollHeight
    textarea.style.height = textarea.scrollHeight + 'px';
}

//Guardar plan de accion modificado

function guardarPlanAccion() {
    console.log("guardando plan")

    var evaluacion_id = document.querySelector('input[name="evaluacion_id"]').value;
    var plan_accion = document.querySelector('#plan_accion_textarea').value;

    var data = {
        plan_accion: plan_accion
    };

    // Envía los valores a la base de datos
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/plan_accion/guardar/' + evaluacion_id, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(data));

    var guardarBtn = document.querySelector('button[onclick="guardarPlanAccion()"]');
    var generarBtn = document.querySelector('button[onclick="generarPlanAccion()"]');
    var textarea = document.querySelector('#plan_accion_textarea');

    // Deshabilitar los botones
    guardarBtn.disabled = true;
    generarBtn.disabled = true;
    textarea.disabled = true;


    // al obtener respuesta del servidor 200, habilitar de nuevo los botones
    
    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 400) {
            guardarBtn.disabled = false;
            generarBtn.disabled = false;
            textarea.disabled = false;
        } else {
            console.error("Error en la solicitud: " + xhr.status);
        }
    };
}

