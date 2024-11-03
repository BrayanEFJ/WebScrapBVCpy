from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import date
import time
from typing import List
from app.models.stock_data_model import StockDataModel
from fastapi import HTTPException
from selenium.webdriver.common.keys import Keys



class WebScrapingService:
    def scrape_stock_data(self, parametro: str, fecha: date) -> List[StockDataModel]:
        url = f"https://www.bvc.com.co/mercado-local-en-linea?tab=renta-variable_mercado-{parametro}"
        data_list = []
        seen_nemotecnicos = set()

        try:
            driver = self._configure_driver()
            driver.get(url)
            self._set_date_fields(driver, fecha)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            if self._is_no_bursatil_day(soup):
                raise HTTPException(status_code=400, detail="No se pudo obtener información bursátil, ya que hoy es un día no bursátil.")

            table = soup.select_one("table.Tablestyled__StyledTable-sc-1ie6ajo-2")
            if table:
                rows = table.select("tbody tr")
                for row in rows:
                    cells = row.select("td")
                    if cells:
                        stock_data = self._extract_stock_data(cells, parametro)
                        if stock_data:
                            nemotecnico = stock_data.nemotecnico
                            if nemotecnico in seen_nemotecnicos:
                                continue
                            seen_nemotecnicos.add(nemotecnico)
                            data_list.append(stock_data)

        except RuntimeError as e:
            if str(e) == "No se pudo obtener información bursátil, ya que hoy es un día no bursátil.":
                return {"mensaje": str(e)}
            else:
                print(f"Error detallado: {str(e)}")
                raise RuntimeError(f"Error al realizar web scraping: {str(e)}")
        finally:
            driver.quit()

        return data_list

    def _configure_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-cache")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def _set_date_fields(self, driver, fecha: date):
        try:
            year_input = driver.find_element(By.CSS_SELECTOR, "input.react-date-picker__inputGroup__year")
            month_input = driver.find_element(By.CSS_SELECTOR, "input.react-date-picker__inputGroup__month")
            day_input = driver.find_element(By.CSS_SELECTOR, "input.react-date-picker__inputGroup__day")

            year_input.clear()
            year_input.send_keys(str(fecha.year))

        # Establecer mes
            month_input.clear()
            for char in str(fecha.month):
                month_input.send_keys(char)
                time.sleep(0.1)  # Esperar 0.1 segundos entre cada carácter

        # Establecer día
            day_input.clear()
            for char in str(fecha.day):
                day_input.send_keys(char)
                time.sleep(0.1)  # Esperar 0.1 segundos entre cada carácter

            time.sleep(3)

            driver.save_screenshot(f"screenshot_{fecha.year}-{fecha.month}-{fecha.day}.png")

        except Exception as e:
            raise RuntimeError(f"Error al establecer la fecha: {str(e)}")

    def _is_no_bursatil_day(self, soup):
        no_bursatil_day_element = soup.select_one("p.Typographystyled__StyledParagraph1-sc-1j6t8c8-8 eXixob typography")
        return no_bursatil_day_element is not None and no_bursatil_day_element.text.strip() == "No hay cifras para mostrarte porque no hay movimientos en el mercado."

    def _extract_stock_data(self, cells, parametro):
        if parametro == "local":
            columns = [
            "nemotecnico",
            "ultimo_precio",
            "variacion_porcentual",
            "volumenes",
            "cantidad",
            "variacion_absoluta",
            "precio_apertura",
            "precio_maximo",
            "precio_minimo",
            "precio_promedio",
            "emisor_nombre"
            ]
        elif parametro == "global-colombiano":
            columns = [
            "nemotecnico",
            "ultimo_precio",
            "variacion_porcentual",
            "volumenes",
            "cantidad",
            "variacion_absoluta",
            "emisor_nombre"
            ]

        if len(cells) < len(columns):
            raise RuntimeError(f"No se pudo obtener información bursátil, la estructura de la tabla ha cambiado.")

        stock_data = {}
        for i, column in enumerate(columns):
            cell = cells[i]
            if cell:
                value = cell.select_one("p").text.strip()
                stock_data[column] = value

        if stock_data:
            return StockDataModel(**stock_data)
        return None