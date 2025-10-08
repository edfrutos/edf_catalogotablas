from flask import Blueprint, render_template


# Crear el blueprint para pruebas de modales unificados
modal_test_bp = Blueprint(
    "modal_test",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/modal_test"
)


@modal_test_bp.route("/", methods=["GET"])
def test_unified_modal():
    """
    Muestra la página de prueba para modales unificados.
    Permite probar diferentes tipos de modales (documento, imagen, multimedia)
    con el nuevo enfoque unificado.
    """
    return render_template("modal_test/test_unified_modal.html")
