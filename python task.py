import requests
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://hprera.nic.in/PublicDashboard"
detail_base_url = "https://hprera.nic.in/"

def get_soup(url):
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def get_project_details(detail_url):
    soup = get_soup(detail_url)
    if not soup:
        return {}
    details = {}
    labels = soup.find_all('label', class_='col-md-3 control-label')
    values = soup.find_all('div', class_='col-md-9')

    for label, value in zip(labels, values):
        label_text = label.get_text(strip=True)
        value_text = value.get_text(strip=True)
        if "GSTIN No" in label_text:
            details['GSTIN No'] = value_text
        if "PAN No" in label_text:
            details['PAN No'] = value_text
        if "Name" in label_text:
            details['Name'] = value_text
        if "Permanent Address" in label_text:
            details['Permanent Address'] = value_text

    return details

soup = get_soup(base_url)
if not soup:
    print("Failed to retrieve the main page.")
    exit()

registered_projects_heading = soup.find('h3', string="Registered Projects")
if not registered_projects_heading:
    print("Failed to find the Registered Projects heading.")
    exit()

registered_projects_section = registered_projects_heading.find_next('table')
if not registered_projects_section:
    print("Failed to find the Registered Projects table.")
    exit()

project_links = registered_projects_section.find_all('a', href=True)[:6]
if not project_links:
    print("No project links found.")
    exit()

project_details_list = []

for project_link in project_links:
    project_detail_url = detail_base_url + project_link['href']
    project_details = get_project_details(project_detail_url)
    if project_details:
        project_details_list.append(project_details)

df = pd.DataFrame(project_details_list)
df.to_csv('registered_projects.csv', index=False)

print("Data scraped and saved to 'registered_projects.csv'")
print(df)
