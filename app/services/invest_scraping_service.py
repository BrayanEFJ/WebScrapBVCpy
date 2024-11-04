import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class InvestScrapingService:

    def _configure_driver(self):
        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-cache")
        options.add_argument("--ignore-certificate-errors")  # Ignorar errores de certificado
        options.add_argument("--allow-insecure-localhost")    # Permitir localhost inseguro
        options.add_argument("--disable-web-security")        # Desactivar la seguridad web
        options.add_argument("--allow-running-insecure-localhost")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def scrape_colombia_equities(self):
        # Configurar el navegador Selenium
        driver = self._configure_driver()
        driver.get("https://es.investing.com/equities/colombia")

        # Esperar a que la página cargue completamente
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#tabs"))
        )

        # Esperar 5 segundos después de cargar la página
        print("Esperando 5 segundos para que la página cargue completamente...")
        time.sleep(5)

        # Hacer clic en las coordenadas (297, 325)
        try:
            # Usar ActionChains para mover el mouse a las coordenadas y hacer clic
            action = ActionChains(driver)
            action.move_by_offset(297, 325).click().perform()
            print("Hice clic en las coordenadas (297, 325).")
        except Exception as e:
            print(f"Ocurrió un error al hacer clic en las coordenadas: {e}")
        finally:
            # Cerrar el navegador al final
            driver.quit()

# Ejecutar el servicio
if __name__ == "__main__":
    scraper = InvestScrapingService()
    scraper.scrape_colombia_equities()
