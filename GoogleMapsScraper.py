import googlemaps
import time
from MongoConnection import get_mongo_collection
from validators import validate_data, companies_schema
from datetime import datetime
import sys
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to the 'companies' collection
companies_collection = get_mongo_collection('TestingDatabase', 'companies')

# Initialize the Google Maps client
gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))

# Set UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')


def clean_website(website):
    # Check if the website is not None and is a string before processing
    if isinstance(website, str) and '?' in website:
        website = website.split('?')[0]
    return website

def get_businesses(industry, location):
    businesses = []
    next_page_token = None
    
    while True:
        if next_page_token:
            places_result = gmaps.places(query=f'{industry} in {location}', page_token=next_page_token)
        else:
            places_result = gmaps.places(query=f'{industry} in {location}')
        
        for place in places_result['results']:
            business_info = {
                'company_name': place.get('name', 'N/A'),
                'address': place.get('formatted_address', 'N/A')
            }

            place_id = place['place_id']
            details = gmaps.place(place_id=place_id, fields=['name', 'formatted_address', 'formatted_phone_number', 'website'])
            result = details.get('result', {})

            business_info['phone_number'] = result.get('formatted_phone_number')
            business_info['website'] = clean_website(result.get('website', None))
            business_info['scrape_timestamp'] = datetime.now()
            business_info['search_term_used'] = f'{industry} in {location}'
            
            # Add to list of businesses
            businesses.append(business_info)
    
        next_page_token = places_result.get('next_page_token')
        
        if not next_page_token:
            break
        else:
            # Wait a few seconds before using the next_page_token
            time.sleep(2)
    
    return businesses

def collect_and_save_data(industry, location):
    """Collect data from Google Maps and save it to the database, avoiding duplicates."""
    companies_collection = get_mongo_collection('TestingDatabase', 'companies')
    
    # Fetch data from Google Maps
    businesses = get_businesses(industry, location)

    for business in businesses:
        # Explicitly check for None to handle missing or empty company names correctly
        company_name = business.get('company_name')
        website = clean_website(business.get('website'))

        # Correct the check to ensure valid company names are processed
        if company_name is None or company_name.strip() == '':
            print(f"Skipping entry due to missing company_name: {business}")
            continue  # Skip to the next business if company_name is missing

        # Check if the company already exists in the database
        existing_company = companies_collection.find_one({
            '$or': [
                {'company_name': company_name},
                {'website': website}
            ]
        })
        
        if existing_company:
            print(f"Skipping duplicate company: {company_name}")
            continue  # Skip to the next business if this one already exists

        # Prepare the business data to be inserted
        business_data = {
            'company_name': company_name,
            'website': website,
            'address': business.get('address'),
            'phone_number': business.get('phone_number'),
            'search_term_used': f"{industry} in {location}",
            'scrape_timestamp': datetime.now(),
            'has_been_hunted': False,  # Default value
        }

        # Validate the business data
        try:
            validate_data(business_data, companies_schema)
            # Insert the new company into the database
            companies_collection.insert_one(business_data)
            print(f"Added new company: {company_name}")
        except ValueError as e:
            print(f"Validation failed for {company_name or website}: {e}")

# Example usage
if __name__ == '__main__':
    collect_and_save_data('landscaping', 'Dallas')