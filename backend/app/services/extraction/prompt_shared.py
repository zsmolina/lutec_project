"""Fragmentos de prompt compartidos entre extractores por año."""

AUDITOR_ROLE = (
    "Actúas como un perito auditor senior de facturación eléctrica. Tu objetivo es transcribir "
    "con precisión matemática absoluta los datos de las imágenes provistas.\n\n"
)

NUMERIC_RULES = (
    "REGLAS DE TRADUCCIÓN NUMÉRICA DIFERENCIADAS (ESTRICTO):\n"
    "1. PARA VALORES DE MONEDA (Total a Pagar y Energía Mes):\n"
    "   - Son valores en MILLONES de pesos. Los puntos que ves son separadores de miles y millones.\n"
    "   - DEBES remover todos los puntos por completo para formar el número entero de millones.\n"
    "   - EJEMPLO: Si en el papel lees '30.838.495', debes entregarlo obligatoriamente como 30838495.00.\n\n"
    "2. PARA CONSUMO DIARIO, CONSUMO ACTUAL Y FACTOR MULTIPLICADOR:\n"
    "   - Si usan formato latinoamericano con punto de miles y coma decimal, "
    "DEBES remover el punto de miles y reemplazar la coma por un punto decimal internacional.\n"
    "   - EJEMPLO: Si el consumo actual en la barra de la gráfica dice '42.120', "
    "transcríbelo exactamente como la cifra completa 42120.0.\n"
    "   - EJEMPLO: Si en Promedio Día lees '2.457,93', debes transformarlo matemáticamente a 2457.93.\n\n"
)
