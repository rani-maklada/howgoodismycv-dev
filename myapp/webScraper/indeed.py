import time
from webdriver_service import WebDriverService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


def search_jobs(search_term, location="israel"):
    webdriver_service = WebDriverService()
    base_url = "https://il.indeed.com/jobs"
    search_url = f"{base_url}?q={search_term}&l={location}"
    webdriver_service.driver.get(search_url)

    job_links = []
    try:
        while len(job_links)<10:
            WebDriverWait(webdriver_service.driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[starts-with(@id,'job_')]"))
            )
            job_elements = webdriver_service.driver.find_elements(By.XPATH, "//a[starts-with(@id,'job_')]")
            for job_element in job_elements:
                job_links.append(job_element.get_attribute('href'))

            # Attempt to find and click the "Next Page" button
            try:
                next_page_button = webdriver_service.driver.find_element(By.XPATH, "//*[@aria-label='Next Page']")
                webdriver_service.driver.execute_script("arguments[0].click();", next_page_button)
                time.sleep(2)  # Wait for page to load
            except NoSuchElementException:
                # If "Next Page" button not found, break from the loop
                break
    except Exception as e:
        print(f"Error during job search: {e}")
    finally:
        webdriver_service.driver.quit()
    print("len(job_links):",len(job_links))
    return job_links


def extract_job_details(job_links):
    job_details = []
    webdriver_service = WebDriverService()
    for job_link in job_links:
        
        webdriver_service.driver.get(job_link)
        try:
            job_title = WebDriverWait(webdriver_service.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".jobsearch-JobInfoHeader-title > span"))
            ).text
            company_name = webdriver_service.driver.find_element(By.XPATH, "//a[contains(@href, 'cmp/')]").text
            location = webdriver_service.driver.find_element(By.CSS_SELECTOR, "[data-testid='jobsearch-JobInfoHeader-companyLocation'] > span").text
            job_description = webdriver_service.driver.find_element(By.ID, "jobDescriptionText").text
            
            job_details.append({
                "Job Title": job_title,
                "Company Name": company_name,
                "Location": location,
                "Job Description": job_description
            })
        except Exception as e:
            print(f"Error extracting details for job link {job_link}: {e}")
    webdriver_service.driver.quit()
    return job_details

job_links = search_jobs("software engineer")
print(job_links)
# job_details = extract_job_details(job_links)
# print(job_details)

# job_links = search_jobs("data analyst")
# print(job_links)
# job_details = extract_job_details(job_links)
# print(job_details)