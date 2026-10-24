# Mis libros
Web estática (docs/) con fichas y mapas de subrayados.
Añadir un libro: crea `libros/<id>/libro.json` (+ portada y PNG/PDF; para subrayados, `citas.txt` con líneas `N. cita`) y ejecuta `python3 build.py`. El build falla si alguna cita no aparece literal.
Prueba en navegador: `python3 herramientas/probar.py`.
