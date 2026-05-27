"""Esquemas Pydantic con anclajes visuales específicos de facturas Afinia."""

from typing import Optional

from pydantic import BaseModel, Field


class ComponentesCUAfinia(BaseModel):
    generacion: float = Field(
        description="Valor decimal en la celda de la sigla G o G:. Coma → punto."
    )
    transmision: float = Field(
        description="Valor decimal en la celda de la sigla T o T:. Coma → punto."
    )
    perdidas: float = Field(
        description="Valor decimal en PR o PR (Pérdidas). Coma → punto."
    )
    restricciones: float = Field(
        description="Valor decimal en la celda R o R:. Coma → punto."
    )
    distribucion: float = Field(
        description="Valor decimal en D, D: o D . Coma → punto."
    )
    comercializacion: float = Field(
        description="Valor decimal en C o C:. Coma → punto."
    )
    cu_aplicado: float = Field(
        description="Valor decimal de CU o CU: (costo unitario aplicado). Coma → punto."
    )


class FacturaAfinia2024Data(BaseModel):
    nic: str = Field(
        description=(
            "Número de 7 dígitos ubicado bajo el recuadro gris "
            "'USE ESTE NUMERO PARA CONSULTAS NIC'."
        )
    )
    documento_equivalente: Optional[str] = Field(
        default=None,
        description=(
            "Número de factura ubicado en la barra gris bajo 'DATOS DE FACTURA No.'."
        ),
    )
    fecha_emision: str = Field(
        description="Fecha de emisión del recuadro de fechas (DD/MM/AAAA)."
    )
    titular_pago: str = Field(
        description="Nombre del cliente bajo la etiqueta 'TITULAR DE PAGO'. En MAYÚSCULAS."
    )
    estrato_clasificacion: str = Field(
        description=(
            "Texto exacto de la clasificación técnica del suministro que aparece en el "
            "bloque de Datos del Cliente. Su anclaje visual es el título 'CLASIFICACIÓN' y "
            "el valor está escrito inmediatamente en la línea de abajo (ejemplo real: "
            "'Com (Sencilla Niv, 1) Carib'). Es obligatorio transcribir este valor literal "
            "de la imagen. No se permite devolver una cadena vacía, un solo dígito ni un "
            "número de estrato aislado; debe ser la clasificación técnica completa."
        )
    )
    propiedad_activo: str = Field(
        default="",
        description="DEBE ser devuelto estrictamente como una cadena vacía: ''.",
    )
    total_a_pagar: float = Field(
        description=(
            "Valor numérico monetario al lado derecho de 'TOTAL A PAGAR MES:'. "
            "Remover puntos de miles."
        )
    )
    energia_mes_valor: float = Field(
        description=(
            "Valor monetario del consumo puro de energía del mes (cantidad facturada de "
            "energía activa). PROHIBIDO 'SUBTOTAL ENERGIA:'. Remover puntos de miles."
        )
    )
    factor_multiplicador: float = Field(
        description="Valor numérico de la fila 'Factor' en el bloque 'DATOS DEL CONSUMO'."
    )
    consumo_actual_kwh: float = Field(
        description=(
            "Cifra en la punta de la ÚLTIMA BARRA de la derecha del gráfico histórico."
        )
    )
    tipo_consumo_calculado: Optional[str] = Field(
        default=None,
        description=(
            "Texto al lado de 'CÁLCULO DEL CONSUMO:' (ej: 'MEDICION'). En MAYÚSCULAS."
        ),
    )
    fecha_lectura_anterior: str = Field(
        description="Fila 'Lectura Anterior' en 'DATOS DEL CONSUMO' (DD/MM/AAAA)."
    )
    fecha_lectura_actual: str = Field(
        description="Fila 'Lectura Actual' en 'DATOS DEL CONSUMO' (DD/MM/AAAA)."
    )
    dias_consumo: int = Field(
        description="Entero de la fila 'Días' o 'Días facturados'."
    )
    consumo_diario: float = Field(
        description="Valor al lado derecho de 'PROMEDIO DIARIO CONSUMO:'."
    )
    tarifa_cu: ComponentesCUAfinia = Field(
        description="Tabla horizontal 'Tarifa de energía Costo Unitario $/kWh'."
    )


class ComponentesCUAfinia2025_2026(BaseModel):
    generacion: float = Field(
        description="Valor decimal en la fila/celda de la sigla G o G:. Coma → punto."
    )
    transmision: float = Field(
        description="Valor decimal en la fila/celda de la sigla T o T:. Coma → punto."
    )
    perdidas: float = Field(
        description="Valor decimal de PR o PR (Pérdidas). Coma → punto."
    )
    restricciones: float = Field(
        description="Valor decimal en la fila/celda de la sigla R o R:. Coma → punto."
    )
    distribucion: float = Field(
        description="Valor decimal de D, D: o D . Coma → punto."
    )
    comercializacion: float = Field(
        description="Valor decimal en la fila/celda de la sigla C o C:. Coma → punto."
    )
    cu_aplicado: float = Field(
        description="Valor decimal de CU o CU: (Costo Unitario final). Coma → punto."
    )


class FacturaAfinia2025_2026Data(BaseModel):
    nic: str = Field(
        description=(
            "7 dígitos rotulados como 'NIC.:' en cabecera superior derecha de la Hoja 1. "
            "Ignora el NIU de 8 dígitos."
        )
    )
    documento_equivalente: Optional[str] = Field(
        default=None,
        description=(
            "Número de 'Factura de Venta No.' o 'Documento Equivalente No.' "
            "en cabecera derecha de la Hoja 1."
        ),
    )
    fecha_emision: str = Field(
        description="Fecha de emisión en cabecera derecha de la Hoja 1 (DD/MM/AAAA)."
    )
    titular_pago: str = Field(
        description=(
            "Nombre bajo 'Titular de Pago' en columna izquierda de la Hoja 1. MAYÚSCULAS."
        )
    )
    estrato_clasificacion: str = Field(
        description=(
            "Texto exacto del campo 'Estrato/Clasificación' en Datos del Usuario "
            "de la Hoja 1. Obligatorio; prohibido vacío."
        )
    )
    propiedad_activo: str = Field(
        description=(
            "Palabra que define la propiedad en la Hoja 2 (Particular, Cliente, Empresa). "
            "Omite 'Medición'."
        )
    )
    total_a_pagar: float = Field(
        description=(
            "Valor de 'Total mes' bajo 'Total a Pagar:' en Hoja 1. "
            "Cobro del periodo sin deudas. Remover puntos de miles."
        )
    )
    energia_mes_valor: float = Field(
        description=(
            "En Hoja 1, 'Resumen facturación mes', valor al lado de 'Energía'. "
            "Remover puntos de miles."
        )
    )
    factor_multiplicador: float = Field(
        description="Campo 'Factor' o multiplicador en bloque 'Datos de lectura' de la Hoja 2."
    )
    consumo_actual_kwh: float = Field(
        description=(
            "Cifra en la base de la ÚLTIMA BARRA del gráfico "
            "'Consumo de los últimos 6 meses kWh' en la Hoja 1."
        )
    )
    tipo_consumo_calculado: Optional[str] = Field(
        default=None,
        description=(
            "Texto al lado de Propiedad del Activo en la Hoja 2 (ej: 'MEDICIÓN'). MAYÚSCULAS."
        ),
    )
    fecha_lectura_anterior: str = Field(
        description="Fila 'Lectura Anterior' en Datos de Lectura de la Hoja 2 (DD/MM/AAAA)."
    )
    fecha_lectura_actual: str = Field(
        description="Fila 'Lectura Actual' en Datos de Lectura de la Hoja 2 (DD/MM/AAAA)."
    )
    dias_consumo: int = Field(
        description="Entero bajo 'Días facturados' o 'Días' en la Hoja 2."
    )
    consumo_diario: float = Field(
        description="'Promedio día' bajo el gráfico de barras en la Hoja 1."
    )
    tarifa_cu: ComponentesCUAfinia2025_2026 = Field(
        description="Tabla 'Costo unitario $/kWh' en la Hoja 2."
    )
