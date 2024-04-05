from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class WebDriverService:
    def __init__(self, executable_path=None, binary_location=None):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Ensures Chrome runs in headless mode
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        chrome_options.add_argument('window-size=1920x1080')  # Screen size
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        
        if binary_location == None:
            binary_location = '/Users/rani/Documents/chrome/chrome123/chrome.exe'
        if executable_path == None:
            executable_path = "/Users/rani/Documents/chromedriver/chromedriver123"
        chrome_options.binary_location = binary_location
        self.service = Service(executable_path)
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
    def get_driver(self):
        return self.driver
    
    def close_driver(self):
        self.driver.close()

    def quit_driver(self):
        self.driver.quit()
