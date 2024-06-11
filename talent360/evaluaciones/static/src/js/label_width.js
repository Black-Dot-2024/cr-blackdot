// Función para medir el ancho del texto
function obtener_ancho_texto(texto, fuente) {
    var canvas = obtener_ancho_texto.canvas || (obtener_ancho_texto.canvas = document.createElement("canvas"));
    var contexto = canvas.getContext("2d");
    contexto.font = fuente;
    var metricas = contexto.measureText(texto);
    return metricas.width;
}

// Ajustar el tamaño del canvas basado en las etiquetas
function ajustar_tamanio_canvas(instancia_grafico) {
    var etiquetas = instancia_grafico.data.labels;
    var canvas = instancia_grafico.canvas;
    var ancho_maximo = Math.max(...etiquetas.map(etiqueta => obtener_ancho_texto(etiqueta, "16px Arial")));
    var altura_requerida = etiquetas.length * (ancho_maximo + 10); // Ajuste de margen

    canvas.style.height = `${altura_requerida}px`;
    canvas.height = altura_requerida;
    instancia_grafico.update();
}

// Configuración inicial del gráfico
function crear_grafico(datos, etiquetas) {
    var contexto = document.getElementById('miGrafico').getContext('2d');
    var miGrafico = new Chart(contexto, {
        type: 'bar',
        data: {
            labels: etiquetas,
            datasets: [{
                label: 'Conjunto de datos',
                data: datos,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    ticks: {
                        autoSkip: false,
                        callback: function(valor) {
                            return valor;
                        }
                    }
                },
                y: {
                    beginAtZero: true
                }
            },
            animation: {
                onComplete: function() {
                    ajustar_tamanio_canvas(this);
                }
            }
        }
    });
}

// Datos de ejemplo
var etiquetas = ["Etiqueta muy larga 1", "Etiqueta aún más larga 2", "Etiqueta 3"];
var datos = [10, 20, 30];
crear_grafico(datos, etiquetas);
