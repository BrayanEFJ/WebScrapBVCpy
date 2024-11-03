from fastapi import APIRouter, Query
from typing import List
from datetime import date
from app.models.stock_data_model import StockDataModel
from app.services.web_scraping_service import WebScrapingService
from app.services.excel_export_service import ExcelExportService

router = APIRouter()
scraping_service = WebScrapingService()
export_service = ExcelExportService()

@router.get("/api/stocks/generateexcel", response_model=List[StockDataModel])
async def obtener_y_exportar_datos(
    parametro: str = Query(default="local", description="Parámetro de búsqueda"),
    fecha: date | None = Query(default=None, description="Fecha de búsqueda")
):
    # Si no se proporciona fecha, usar la fecha actual
    if fecha is None:
        fecha = date.today()
    
    # Obtener datos
    stock_data_list = scraping_service.scrape_stock_data(parametro, fecha)
    
    return stock_data_list