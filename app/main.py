from fastapi import FastAPI
from app.controllers.stock_data_controller import router as stock_data_router
from app.controllers.invest_data_controller import router as invest_data_router


app = FastAPI(title="Stock Data API")

# Incluir los routers
app.include_router(stock_data_router)
app.include_router(invest_data_router)


@app.get("/")
async def root():
    return {"message": "Stock Data API is running"}
