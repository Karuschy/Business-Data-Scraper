import requests
from bs4 import BeautifulSoup
import re
from validate_email_address import validate_email
from MongoConnection import get_mongo_collection
from validators import validate_data, companies_schema
from datetime import datetime
import sys

# Set UTF-8 encoding for output to handle Unicode characters correctly
sys.stdout.reconfigure(encoding='utf-8')


def clean_email(email):
    email = re.split(r'[^\w\.-]+', email)[0].lower()
    return email

def validate_email(email):
    """Validate email using a more flexible regex pattern."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def extract_emails_from_text(text):
    """Extract all email addresses from the given text using regex."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)

def scrape_website(website):
    try:
        if website == 'N/A':
            raise ValueError('Invalid URL: N/A')

        response = requests.get(website, timeout=30, verify=False)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract emails from mailto links
        mailto_links = soup.select('a[href^=mailto]')
        emails = [clean_email(link.get('href').replace('mailto:', '')) for link in mailto_links]

        # Extract emails from text
        page_text = soup.get_text()
        emails += extract_emails_from_text(page_text)
        
        # Remove duplicates and invalid entries
        emails = list(set(emails))
        emails = [email for email in emails if '@' in email and validate_email(email)]

        return emails
    except requests.exceptions.Timeout:
        print(f"Timeout occurred while scraping {website}. Skipping this site.")
        return []
    except requests.exceptions.RequestException:
        return []
    except ValueError:
        return []
    except Exception:
        return []

def update_company_info():
    # Connect to the 'companies' collection in MongoDB
    companies_collection = get_mongo_collection('TestingDatabase', 'companies')
    
    # Fetch companies from MongoDB
    companies = companies_collection.find()  # Fetch all companies
    
    for company in companies:
        emails = scrape_website(company.get('website', 'N/A'))
        company_email = emails[0] if emails else 'N/A'
        other_emails = emails[1:] if len(emails) > 1 else []

        print(f"Scraped for {company.get('company_name', 'Unknown')}: Email={company_email}")
        
        if company_email != 'N/A':
            # Prepare updated company data
            updated_data = {
                'email': company_email,
                'other_emails': other_emails,
                'scrape_timestamp': datetime.now(),  # Overwrite with the latest scrape time
                'company_name': company.get('company_name', 'Unknown'),  # Ensure required fields are included
                'search_term_used': company.get('search_term_used', 'Unknown')  # Ensure required fields are included
            }
            
            # Validate the updated data
            try:
                validate_data(updated_data, companies_schema)

                # Update MongoDB document with $set to overwrite scrape_timestamp
                companies_collection.update_one(
                    {'_id': company['_id']}, 
                    {'$set': updated_data}
                )
                print(f"Updated {company.get('company_name', 'Unknown')}: Email={company_email}")
            except ValueError as e:
                print(f"Validation failed for {company.get('company_name', 'Unknown')}: {e}")
        else:
            print(f"No valid email found for {company.get('company_name', 'Unknown')}")

if __name__ == '__main__':
    print("Start scraping websites...")
    update_company_info()
    print("Finished updating company info.")