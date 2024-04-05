import time
from webdriver_service import WebDriverService  # Ensure this custom service correctly initializes Selenium WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
import pandas as pd
import os

def search_jobs(search_term):
    webdriver_service = WebDriverService()
    job_links = []
   
    try:
        driver = webdriver_service.get_driver()  # Ensure this method retrieves a correctly initialized WebDriver
        search_term = search_term.replace(" ", "+")
        base_url = "https://www.dice.com"
        search_url = f"{base_url}/jobs/q-{search_term}-jobs?page=1"
        driver.get(search_url)
        
        wait = WebDriverWait(driver, 30)
        print(search_url)
        while True:
            job_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "dhi-job-search-job-card")))
            
            for card in job_cards:
                try:
                    # Check for shadow DOM support and access
                    if hasattr(card, 'shadow_root') and card.shadow_root:
                        card_shadow_root = card.shadow_root
                        job_layout = WebDriverWait(card_shadow_root, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "dhi-job-search-job-card-layout-full")))
                        if hasattr(job_layout, 'shadow_root') and job_layout.shadow_root:
                            layout_shadow_root = job_layout.shadow_root
                            job_link_element = WebDriverWait(layout_shadow_root, 20).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='job-detail']")))
                            job_links.append(job_link_element.get_attribute('href'))
                        else:
                            print("No shadow root found for job layout.")
                    else:
                        print("No shadow root found for card.")
                except (TimeoutException, NoSuchElementException) as e:
                    print(f"Exception encountered: {e}")
                    continue

            try:
                # Simplify pagination by avoiding shadow DOM if possible or correct the XPath if it's necessary
                pagination = driver.find_element(By.CSS_SELECTOR, "dhi-seds-pagination")
                pagination_shadow_root = pagination.shadow_root
                next_page = pagination_shadow_root.find_element(By.CSS_SELECTOR, "a[aria-label='Next']") 
                print(next_page.get_attribute('href')) 
                if next_page:
                    next_page.click()
                    time.sleep(2)  # Consider replacing with a more robust wait condition
                else:
                    break
            except NoSuchElementException as e:
                print(f"General error during pagination: {e}")
                break
    except Exception as e:
        print(f"General error during job search: {e}")
    finally:
        webdriver_service.quit_driver()
    
    return job_links

def extract_skills(job_links):
    print(f"Starting to extract skills for {len(job_links)} jobs...")
    skills = []
    webdriver_service = WebDriverService()
    driver = webdriver_service.get_driver()
    wait = WebDriverWait(driver, 20)
    try:
        for index, job_link in enumerate(job_links):
            print(f"Processing job link {index + 1}/{len(job_links)}: {job_link}")

            try:
                driver.get(job_link)
                wait.until(EC.presence_of_element_located((By.XPATH, "//*[starts-with(@id,'skillChip:')]")))
                try:
                    skills_toggle_button = driver.find_element(By.XPATH, "//*[@id='skillsToggle']")
                    print("Skills toggle button found. Clicking to reveal hidden skills...")
                    skills_toggle_button.click()
                    time.sleep(1)  # Adjust sleep time based on the actual time it takes for the content to become visible
                except (TimeoutException, NoSuchElementException):
                    print("No skills toggle button found. Continuing without toggling.")
                
                job_skills = []
                skills_element = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[starts-with(@id,'skillChip:')]")))
                job_title_element = driver.find_element(By.XPATH, "//*[@id='jobdetails']/h1").text
                for skill in skills_element:
                    job_skills.append(skill.text)

                skills.append({
                    "Job Title": job_title_element,
                    "Skills": ', '.join(job_skills),
                })
                print(f"Extracted skills for job: {job_title_element}")
            except Exception as e:
                print(f"Error extracting details for job link {job_link}: {e}")
    
    except Exception as e:
        print(f"General Error: {e}")
    finally:
        driver.quit()
    print("Finished extracting skills.")
    return skills


def save_jobs(job_links, position):
    position = position.replace(" ", "_")
    filename = f"{position}_links"
    with open(position, 'w') as file:
        for link in job_links:
            file.write(link + "\n")  # Write each link on a new line

    print(f"Saved {len(job_links)} job links to {filename}")


def read_job_links(file_path):
    print(f"Reading job links from {file_path}...")
    with open(file_path, 'r') as file:
        job_links = [line.strip() for line in file.readlines()]
    print(f"Found {len(job_links)} job links.")
    return job_links


def process_job_links(directory, file_name, output_file_name):
    print(f"Starting process for {file_name}...")
    file_path = os.path.join(directory, file_name)
    output_path = os.path.join(directory, output_file_name)
    job_links = read_job_links(file_path)
    
    batch_size = 100
    for i in range(0, len(job_links), batch_size):
        print(f"Processing batch {i//batch_size + 1}...")
        batch_links = job_links[i:i+batch_size]
        skills_data = extract_skills(batch_links)
        skills_df = pd.DataFrame(skills_data)
        
        if i == 0:
            skills_df.to_csv(output_path, mode='w', index=False, header=True, encoding='utf-8')
        else:
            skills_df.to_csv(output_path, mode='a', index=False, header=False, encoding='utf-8')
        
        print(f"Saved batch {i//batch_size + 1} to '{output_path}'.")
    print(f"Completed processing for {file_name}.")


# Example usage
# java_developer = "Java Developer"
# data_analyst = "Data Analyst"
# python_developer = "Python Developer"
# automation_engineer = "Automation Engineer"

# job_links = search_jobs(java_developer)
# save_jobs(job_links, java_developer)

# job_links = search_jobs(data_analyst)
# save_jobs(job_links, data_analyst)

# job_links = search_jobs(python_developer)
# save_jobs(job_links, python_developer)

# job_links = search_jobs(automation_engineer)
# save_jobs(job_links, automation_engineer)

# List of job files and their corresponding output files
# job_files = [
#     ('Java_Developer.txt', 'Java_Developer_skills.csv'),
#     ('Data_Analyst.txt', 'Data_Analyst_skills.csv'),
#     ('Python_Developer.txt', 'Python_Developer_skills.csv'),
#     ('Automation_Engineer.txt', 'Automation_Engineer_skills.csv'),
# ]
    
# directory = r'C:\Users\rani\OneDrive\Documents\GitLab\howgoodismycv-dev'

# # Loop through the files and process each one
# for job_file, output_file in job_files:
#     process_job_links(directory, job_file, output_file)
