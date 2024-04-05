from myapp.webScraper.webdriver_service import WebDriverService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

my_webdriver_service = WebDriverService()
# Open the website
my_webdriver_service.driver.get('https://www.chatpdf.com/')

# Wait for the file input to be present in the DOM
wait = WebDriverWait(my_webdriver_service.driver, 10) # Adjust the timeout as needed
file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))


try:
    # Assuming this script is saved in a file that's being executed directly
    script_directory = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Fallback if __file__ is not defined, you might need to set script_directory manually
    script_directory = os.getcwd()  # This gets the current working directory as a fallback

parent_directory = os.path.dirname(script_directory)
pdf_directory = os.path.join(parent_directory, "NLP_resume", "remusesexample", "Resume_Rani_Maklada.pdf")


# Specify the full path to your file
file_path = pdf_directory

# Use send_keys() to upload the file
file_input.send_keys(file_path)

# Wait for the textarea to be clickable
wait = WebDriverWait(my_webdriver_service.driver, 10) # Adjust the timeout as needed
textarea = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ant-input")))

# Once the textarea is located, you can send keys to it
question_text = "This is the question I want to ask."
textarea.send_keys(question_text)

# Locate the button using CSS selector with multiple classes
send_button = WebDriverWait(my_webdriver_service.driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-btn.ant-btn-primary.ant-btn-compact-item.ant-btn-compact-last-item"))
)

# Click the send button
send_button.click()