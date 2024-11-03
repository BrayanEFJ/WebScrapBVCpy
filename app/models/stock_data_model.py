from pydantic import BaseModel

class StockDataModel(BaseModel):  # También cambié el nombre de la clase para ser más específico
    nemotecnico: str | None = None
    ultimo_precio: str | None = None
    variacion_porcentual: str | None = None
    volumenes: str | None = None
    cantidad: str | None = None
    variacion_absoluta: str | None = None
    precio_apertura: str | None = None
    precio_maximo: str | None = None
    precio_minimo: str | None = None
    precio_promedio: str | None = None
    emisor_nombre: str | None = None