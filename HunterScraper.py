import requests
from datetime import datetime, timezone
from MongoConnection import get_mongo_collection
from validators import validate_data, companies_schema, people_schema
from WebsiteScraper import clean_email, validate_email
from dotenv import load_dotenv
import os

load_dotenv()

# Set Hunter.io API key
HUNTER_API_KEY =  os.getenv('HUNTER_API_KEY')

def scrape_hunter_data(domain):
    """Scrape company data and employee information from Hunter.io using the domain."""
    headers = {
        'Authorization': f'Bearer {HUNTER_API_KEY}'
    }
    try:
        response = requests.get(f'https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_API_KEY}')
        response.raise_for_status()
        data = response.json()
        return data['data']
    except requests.exceptions.RequestException as e:
        print(f"Error accessing Hunter.io API: {e}")
        return None


def get_company_name_by_email_domain(email_domain):
    """Retrieve the company name from the companies collection based on the email domain."""
    companies_collection = get_mongo_collection('TestingDatabase', 'companies')
    company = companies_collection.find_one({'website': {'$regex': email_domain, '$options': 'i'}})
    return company

def update_company_emails(company, email):
    """Add email to the company's 'other_emails' list if it doesn't already exist."""
    companies_collection = get_mongo_collection('TestingDatabase', 'companies')
    if 'other_emails' not in company:
        company['other_emails'] = []

    if email not in company['other_emails']:
        company['other_emails'].append(email)
        companies_collection.update_one(
            {'_id': company['_id']},
            {'$set': {'other_emails': company['other_emails'], 'scrape_timestamp': datetime.now(timezone.utc)}}
        )
        print(f"Added email {email} to company {company.get('company_name', 'Unknown')}.")


def update_company_info(company_data, domain):
    """Update company information in the database with data from Hunter.io."""
    companies_collection = get_mongo_collection('TestingDatabase', 'companies')
    company = companies_collection.find_one({'website': {'$regex': domain, '$options': 'i'}})
    
    if not company:
        print(f"No matching company found for domain: {domain}")
        return
    
    # Ensure required fields are included
    company_name = company_data.get('organization', company.get('company_name', 'Unknown Company'))
    search_term_used = company.get('search_term_used', 'Unknown Search Term')
    
    updated_data = {
        'company_name': company_name,  # Required field
        'search_term_used': search_term_used,  # Required field
        'linkedin_url': company_data.get('linkedin', company.get('linkedin_url', '')),
        'linkedin_description': company_data.get('description', company.get('linkedin_description', '')),
        'other_emails': [email['value'] for email in company_data.get('emails', []) if email['type'] == 'generic'],
        'scrape_timestamp': datetime.now(timezone.utc),
        'has_been_hunted': True  # Set to True after processing
    }
    
    try:
        validate_data(updated_data, companies_schema)
        companies_collection.update_one(
            {'_id': company['_id']},
            {'$set': updated_data}
        )
        print(f"Updated company information for {domain}.")
    except ValueError as e:
        print(f"Validation failed for {domain}: {e}")

def update_people_info(employees):
    """Add or update people information in the database with data from Hunter.io."""
    people_collection = get_mongo_collection('TestingDatabase', 'people')
    
    for employee in employees:
        email = employee.get('value', '').lower()

        # Validate the email
        if not validate_email(email):
            print(f"Skipping invalid email: {email}")
            continue
        
        email_domain = email.split('@')[-1]
        company = get_company_name_by_email_domain(email_domain)
        company_name = company.get('company_name') if company else 'Unknown Company'
        
        # Process valid personal emails with first name
        first_name = employee.get('first_name')
        last_name = employee.get('last_name')
        if employee.get('type') == 'personal' and first_name:
            person_data = {
                'first_name': first_name,
                'last_name': last_name or '',  # Use an empty string if last_name is not provided
                'email': email,
                'position': employee.get('position', ''),
                'linkedin_profile': employee.get('linkedin', ''),
                'company_name': company_name,
                'scrape_timestamp': datetime.now(timezone.utc),
                'has_been_hunted': True
            }
            
            try:
                validate_data(person_data, people_schema)
                people_collection.update_one(
                    {'email': person_data['email']},
                    {'$set': person_data},
                    upsert=True  # Insert if not found, update if found
                )
                print(f"Updated person information for {person_data['first_name']} {person_data['last_name']}.")
            except ValueError as e:
                print(f"Validation failed for person {person_data.get('first_name', '')}: {e}")
        else:
            # If the email is valid but lacks a name, add it to the company's other_emails
            if company and validate_email(email):
                update_company_emails(company, email)

def hunter_scraper(domain):
    """Main function to perform scraping from Hunter.io and update databases."""
    print(f"Scraping data for domain: {domain}")
    hunter_data = scrape_hunter_data(domain)
    
    if not hunter_data:
        print(f"Failed to retrieve data for {domain}.")
        return
    
    update_company_info(hunter_data, domain)
    update_people_info(hunter_data.get('emails', []))

# Example usage
if __name__ == '__main__':
    domain = 'lawnsofdallas.com'  # Replace with the actual domain you want to scrape
    hunter_scraper(domain)