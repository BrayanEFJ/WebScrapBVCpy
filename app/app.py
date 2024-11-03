from fastapi import FastAPI
from controllers.stock_data_controller import router as stock_data_router

app = FastAPI(title="Stock Data API")

# Incluir los routers
app.include_router(stock_data_router)

@app.get("/")
async def root():
    return {"message": "Stock Data API is running"}
