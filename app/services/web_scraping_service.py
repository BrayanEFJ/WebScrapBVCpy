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
from ..models.stock_data_model import StockData

class WebScrapingService:
    def scrape_stock_data(self, parametro: str, fecha: date) -> List[StockData]:
        URL = f"https://www.bvc.com.co/mercado-local-en-linea?tab=renta-variable_mercado-{parametro}"
        data_list = []
        seen_nemotecnicos = set()

        try:
            # Configurar Chrome
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            wait = WebDriverWait(driver, 15)

            try:
                driver.get(URL)

                # Esperar a que los campos de fecha estén presentes
                wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".react-date-picker__inputGroup")))

                # Establecer los valores de fecha
                self._set_date_fields(driver, fecha)

                # Esperar a que la tabla se actualice
                time.sleep(2)

                # Esperar a que la tabla esté visible
                wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "table.Tablestyled__StyledTable-sc-1ie6ajo-2")))

                # Obtener el HTML actualizado
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                # Encontrar la tabla
                table = soup.select_one("table.Tablestyled__StyledTable-sc-1ie6ajo-2")
                if table:
                    rows = table.select("tbody tr")

                    for row in rows:
                        cells = row.select("td")
                        if cells:
                            nemotecnico = cells[0].select_one("p").text.strip()

                            if nemotecnico in seen_nemotecnicos:
                                continue
                            seen_nemotecnicos.add(nemotecnico)

                            stock_data = StockData(
                                nemotecnico=nemotecnico,
                                ultimo_precio=cells[1].select_one("p").text.strip(),
                                variacion_porcentual=cells[2].select_one("p").text.strip(),
                                volumenes=cells[3].select_one("p").text.strip(),
                                cantidad=cells[4].select_one("p").text.strip(),
                                variacion_absoluta=cells[5].select_one("p").text.strip(),
                                precio_apertura=cells[6].select_one("p").text.strip(),
                                precio_maximo=cells[7].select_one("p").text.strip(),
                                precio_minimo=cells[8].select_one("p").text.strip(),
                                precio_promedio=cells[9].select_one("p").text.strip(),
                                emisor_nombre=cells[10].select_one("p").text.strip()
                            )

                            data_list.append(stock_data)

            finally:
                driver.quit()

        except Exception as e:
            raise RuntimeError(f"Error al realizar web scraping: {str(e)}")

        return data_list

    def _set_date_fields(self, driver, fecha: date):
        try:
            year_input = driver.find_element(
                By.CSS_SELECTOR, "input.react-date-picker__inputGroup__year")
            month_input = driver.find_element(
                By.CSS_SELECTOR, "input.react-date-picker__inputGroup__month")
            day_input = driver.find_element(
                By.CSS_SELECTOR, "input.react-date-picker__inputGroup__day")

            # Limpiar y establecer el año
            year_input.clear()
            year_input.send_keys(str(fecha.year))

            # Limpiar y establecer el mes
            month_input.clear()
            month_input.send_keys(str(fecha.month))

            # Limpiar y establecer el día
            day_input.clear()
            day_input.send_keys(str(fecha.day))

            time.sleep(1)

        except Exception as e:
            raise RuntimeError(f"Error al establecer la fecha: {str(e)}")