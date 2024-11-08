import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup


class InvestScrapingService:

    def __init__(self):
        self.driver = None
        self.wait = None

    def _configure_driver(self):
        """ Configura el navegador con las opciones necesarias """
        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-cache")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-insecure-localhost")
        options.add_argument("--disable-web-security")
        options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/91.0")

        service = Service(GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def _close_popup(self):
        """Intenta cerrar el anuncio emergente si aparece."""
        try:
            # Esperar hasta que el botón de cierre del anuncio esté presente
            close_button = self.driver.find_element(By.CSS_SELECTOR, "svg[data-test='sign-up-dialog-close-button']")
            if close_button.is_displayed():
                close_button.click()
                print("Anuncio emergente cerrado.")
        except NoSuchElementException:
            # Si el anuncio no está presente, continuar
            print("No se encontró ningún anuncio emergente.")   

    def scrape_colombia_equities(self):
        """ Función principal para hacer el scraping de datos """
        self._configure_driver()

        try:
            self.driver.get("https://es.investing.com/equities/colombia")
            # print("Esperando 3 segundos para que la página cargue completamente...")
            # time.sleep(3)

            # Recoger la tabla por defecto
            table_default = self._get_table_data("datatable-v2_body__8TXQk")
            # Recoger las tablas de Ejecución, Técnico y Fundamental
            table_ejecucion = self._get_table_data("datatable-v2_body__8TXQk", button_text="Ejecución")
            table_tecnico = self._get_table_data("datatable-v2_body__8TXQk", button_text="Técnico")
            table_fundamental = self._get_table_data("datatable-v2_body__8TXQk", button_text="Fundamental")

            # Crear un directorio para los archivos si no existe
            if not os.path.exists("stock_data"):
                os.makedirs("stock_data")

            # Procesar cada acción individualmente
            self._process_actions(table_default, table_ejecucion, table_tecnico, table_fundamental)

        except Exception as e:
            print(f"Ocurrió un error: {e}")
        finally:
            # Cerrar el navegador
            self.driver.quit()

    def _get_table_data(self, table_class, button_text=None):
        """ Obtiene los datos de la tabla de acuerdo al nombre de la clase o el texto del botón """
        if button_text:
            button = self.wait.until(EC.presence_of_element_located((By.XPATH, f"//button[text()='{button_text}']")))
            print(f"Botón {button_text} encontrado y listo para hacer clic.")
            actions = ActionChains(self.driver)
            actions.move_to_element(button).click().perform()
            time.sleep(3)  # Esperar para que se vean los cambios en la página

        table_content = self.driver.find_element(By.CLASS_NAME, table_class).get_attribute("innerHTML")
        print("Nombre de clase que está tomando: " + table_class)
        soup = BeautifulSoup(table_content, "html.parser")
        return soup.find_all("tr", class_="datatable-v2_row__hkEus")

    def _process_actions(self, table_default, table_ejecucion, table_tecnico, table_fundamental):
        """ Procesa los datos de cada acción y crea un archivo para cada una """
        # Procesar cada fila de la tabla por defecto
        actions_data = self._combine_data(table_default, table_ejecucion, table_tecnico, table_fundamental)

        for action_data in actions_data:
            name = action_data["name"]
            file_name = f"stock_data/{name}.txt"

            with open(file_name, "w") as file:
                # Guardar información de la tabla por defecto
                file.write(f"Nombre: {action_data['name']}\n")
                file.write(f"Último: {action_data['last']}\n")
                file.write(f"Máximo: {action_data['high']}\n")
                file.write(f"Mínimo: {action_data['low']}\n")
                file.write(f"Var.: {action_data['change']}\n")
                file.write(f"% Var.: {action_data['change_percent']}\n")
                file.write(f"Vol.: {action_data['volume']}\n")
                file.write(f"Hora: {action_data['time']}\n\n")

                # Guardar información de la tabla de Ejecución
                file.write(f"Ejecución:\nNombre: {action_data['name']}\n")
                file.write(f"Diario: {action_data['ejecucion']['diario']}\n")
                file.write(f"Semanal: {action_data['ejecucion']['semanal']}\n")
                file.write(f"Mensual: {action_data['ejecucion']['mensual']}\n")
                file.write(f"Anual: {action_data['ejecucion']['anual']}\n")
                file.write(f"1 año: {action_data['ejecucion']['1año']}\n")
                file.write(f"3 años: {action_data['ejecucion']['3años']}\n\n")

                # Guardar información de la tabla de Técnico
                file.write(f"Técnico:\nNombre: {action_data['name']}\n")
                file.write(f"1 hora: {action_data['tecnico']['1hora']}\n")
                file.write(f"Diario: {action_data['tecnico']['diario']}\n")
                file.write(f"Semanal: {action_data['tecnico']['semanal']}\n")
                file.write(f"Mensual: {action_data['tecnico']['mensual']}\n\n")

                # Guardar información de la tabla de Fundamental
                file.write(f"Fundamental:\nNombre: {action_data['name']}\n")
                file.write(f"Vol. promedio (3m): {action_data['fundamental']['vol_promedio']}\n")
                file.write(f"Cap. mercado: {action_data['fundamental']['cap_mercado']}\n")
                file.write(f"Ingresos: {action_data['fundamental']['ingresos']}\n")
                file.write(f"PER: {action_data['fundamental']['per']}\n")
                file.write(f"Beta: {action_data['fundamental']['beta']}\n")

            print(f"Datos de {name} guardados en {file_name}")

    def _combine_data(self, table_default, table_ejecucion, table_tecnico, table_fundamental):
        """ Combina los datos de todas las tablas para cada acción """
        actions_data = []

        for row in table_default:
            columns = row.find_all("td")
            if columns:
                name = columns[1].find("a").text.strip()
                last = columns[2].text.strip()
                high = columns[3].text.strip()
                low = columns[4].text.strip()
                change = columns[5].text.strip()
                change_percent = columns[6].text.strip()
                volume = columns[7].text.strip()
                time = columns[8].find("time").text.strip()

                ejecucion = self._get_table_for_action(name, table_ejecucion, ["diario", "semanal", "mensual", "anual", "1año", "3años"])
                tecnico = self._get_table_for_action(name, table_tecnico, ["1hora", "diario", "semanal", "mensual"])
                fundamental = self._get_table_for_action(name, table_fundamental, ["vol_promedio", "cap_mercado", "ingresos", "per", "beta"])

                actions_data.append({
                    "name": name,
                    "last": last,
                    "high": high,
                    "low": low,
                    "change": change,
                    "change_percent": change_percent,
                    "volume": volume,
                    "time": time,
                    "ejecucion": ejecucion,
                    "tecnico": tecnico,
                    "fundamental": fundamental
                })

        return actions_data

    def _get_table_for_action(self, action_name, table_data, field_names):
        """ Extrae los datos específicos de la acción para cada tabla """
        for row in table_data:
            columns = row.find_all("td")
            if columns:
                table_name = columns[1].text.strip()
                if table_name == action_name:
                    return {field: col.text.strip() for field, col in zip(field_names, columns[2:])}
        return {field: f"No se encontró información {table_name +" - " +action_name}" for field in field_names}


# Ejecutar el servicio
if __name__ == "__main__":
    scraper = InvestScrapingService()
    scraper.scrape_colombia_equities()
