from fastapi import APIRouter
from app.services.invest_scraping_service import InvestScrapingService

router = APIRouter()
scraping_service = InvestScrapingService()

@router.get("/api/stocks/investdata")
async def obtener_datos_invest():
   return scraping_service.scrape_colombia_equities()
    
     