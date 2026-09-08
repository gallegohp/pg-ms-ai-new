from typing import Dict, Any

def generar_plan_simulado(contexto: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera un plan nutricional de ejemplo (sin IA real).
    """
    nombre = contexto.get("nombre", "Socio")
    objetivo = contexto.get("objetivoEspecifico", "Mantener peso")

    return {
        "calorias_diarias": 2200,
        "proteinas_g": 150.0,
        "carbohidratos_g": 250.0,
        "grasas_g": 70.0,
        "restricciones_dieteticas": [],
        "sugerencias_comidas": {
            "desayuno": [
                {
                    "nombre": "Avena con frutas",
                    "descripcion": "Desayuno energético",
                    "ingredientes": "Avena, leche, plátano",
                    "preparacion": "Cocinar la avena con leche y añadir frutas",
                    "calorias": 350,
                    "proteinas": 10.0,
                    "carbohidratos": 50.0,
                    "grasas": 8.0
                }
            ],
            "almuerzo": [
                {
                    "nombre": "Pollo con verduras",
                    "descripcion": "Almuerzo completo",
                    "ingredientes": "Pechuga de pollo, brócoli, zanahoria",
                    "preparacion": "Cocinar a la plancha",
                    "calorias": 600,
                    "proteinas": 40.0,
                    "carbohidratos": 60.0,
                    "grasas": 15.0
                }
            ],
            "cena": [
                {
                    "nombre": "Pescado con espárragos",
                    "descripcion": "Cena ligera",
                    "ingredientes": "Salmón, espárragos, limón",
                    "preparacion": "Hornear a 180°C",
                    "calorias": 450,
                    "proteinas": 35.0,
                    "carbohidratos": 10.0,
                    "grasas": 20.0
                }
            ],
            "colaciones": [
                {
                    "nombre": "Batido de proteínas",
                    "descripcion": "Recuperación muscular",
                    "ingredientes": "Leche, proteína, plátano",
                    "preparacion": "Licuar",
                    "calorias": 200,
                    "proteinas": 20.0,
                    "carbohidratos": 25.0,
                    "grasas": 5.0
                }
            ]
        },
        "explicacion_ia": f"Plan nutricional simulado para {nombre} (objetivo: {objetivo})."
    }