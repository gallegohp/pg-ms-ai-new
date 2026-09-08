import json
from typing import Dict, Any

def generar_rutina_simulada(contexto: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera una rutina de ejemplo (sin IA real).
    El contexto puede contener datos del socio.
    """
    nombre = contexto.get("nombre", "Socio")
    objetivo = contexto.get("objetivoPrincipal", "mejorar condición física")
    dias = contexto.get("diasPorSemana", 3)

    # Ejercicios de ejemplo
    ejercicios = [
        {"nombre": "Sentadillas", "grupo": "Piernas"},
        {"nombre": "Flexiones", "grupo": "Pecho"},
        {"nombre": "Dominadas", "grupo": "Espalda"},
        {"nombre": "Plancha", "grupo": "Core"},
        {"nombre": "Press hombros", "grupo": "Hombros"},
        {"nombre": "Curl bíceps", "grupo": "Brazos"},
    ]

    dias_rutina = []
    for i in range(dias):
        ejercicios_dia = []
        for j in range(3):
            idx = (i * 3 + j) % len(ejercicios)
            ej = ejercicios[idx]
            ejercicios_dia.append({
                "diaSemana": i + 1,
                "orden": j + 1,
                "nombreEjercicio": ej["nombre"],
                "series": 3,
                "repeticionesMin": 8,
                "repeticionesMax": 12,
                "pesoSugerido": 0.0,
                "descansoSegundos": 60,
                "notas": f"Ejercicio para {ej['grupo']}",
                "equipoRequerido": "Sin equipo"
            })
        dias_rutina.extend(ejercicios_dia)

    return {
        "nombre": f"Rutina de {objetivo} para {nombre}",
        "descripcion": f"Rutina simulada de {dias} días",
        "explicacionIA": "Esta es una rutina generada por simulación (sin IA real).",
        "detalles": dias_rutina
    }