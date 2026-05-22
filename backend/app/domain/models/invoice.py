from typing import Optional

from pydantic import BaseModel, Field


class ComponentesCU(BaseModel):
    generacion: float = Field(description="Valor numérico de G (Generación).")
    transmision: float = Field(description="Valor numérico de T (Transmisión).")
    perdidas: float = Field(description="Valor numérico de P (Pérdidas).")
    restricciones: float = Field(description="Valor numérico de R (Restricciones).")
    distribucion: float = Field(description="Valor numérico de D (Distribución).")
    comercializacion: float = Field(description="Valor numérico de C (Comercialización).")
    cu_aplicado: float = Field(description="Valor numérico exacto del CU Aplicado final.")


class FacturaEnergiaData(BaseModel):
    nic: str = Field(description="NIC o CUENTA sin letras ni espacios.")
    documento_equivalente: Optional[str] = Field(
        default=None, description="Número de documento equivalente digital o electrónico."
    )
    fecha_emision: str = Field(description="Fecha de emisión (DD/MM/AAAA).")
    titular_pago: str = Field(description="Nombre completo del titular en MAYÚSCULAS.")
    estrato_clasificacion: str = Field(description="Estrato o clasificación del usuario.")
    propiedad_activo: str = Field(description="Propiedad del activo (Particular, Compartido, etc.).")
    total_a_pagar: float = Field(
        description="Total en millones de pesos como float puro (ej. 33613960.00)."
    )
    energia_mes_valor: float = Field(
        description="Energía del mes en millones de pesos como float puro."
    )
    factor_multiplicador: float = Field(description="Factor multiplicador del medidor.")
    consumo_actual_kwh: float = Field(description="Consumo actual en kWh.")
    tipo_consumo_calculado: str = Field(description="'REAL' o 'ESTIMADO' en mayúsculas.")
    fecha_lectura_anterior: str = Field(description="Fecha lectura anterior (DD/MM/AAAA).")
    fecha_lectura_actual: str = Field(description="Fecha lectura actual (DD/MM/AAAA).")
    dias_consumo: int = Field(description="Días facturados.")
    consumo_diario: float = Field(description="Consumo diario promedio (kWh/día).")
    tarifa_cu: ComponentesCU = Field(description="Desglose del costo unitario.")
