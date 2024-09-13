from GoogleMapsScraper import collect_and_save_data
from WebsiteScraper import update_company_info
from HunterScraper import hunter_scraper
from MongoConnection import get_mongo_collection
from datetime import datetime

# List of (industry, location) sets to iterate through
industry_location_sets = [
    ('roofing', 'Oakville Ontario'),
    ('roofing', 'Markham Ontario'),
    ('roofing', 'Mississauga Ontario'),
    ('roofing', 'Burlington Ontario'),
    ('roofing', 'Richmond Hill Ontario'),
    ('roofing', 'Aurora Ontario'),
    ('roofing', 'Brampton Ontario'),
    ('roofing', 'Oshawa Ontario'),
    ('roofing', 'Kitchener Ontario'),
    ('roofing', 'Hamilton Ontario'),
    ('roofing', 'Vaughan Ontario'),
    ('roofing', 'Toronto Ontario')
   
    # Add more (industry, location) pairs as needed
]

def run_google_maps_scraper(industry, location):
    """Run the GoogleMapsScraper to add new companies to the database."""
    print(f"Running GoogleMapsScraper for {industry} in {location}...")
    collect_and_save_data(industry, location)

def run_website_scraper():
    """Run the WebsiteScraper to update company information."""
    print("Running WebsiteScraper to update company information...")
    update_company_info()

def run_hunter_scraper():
    """Run the HunterScraper to further enrich company and people data."""
    print("Running HunterScraper to enrich data...")
    companies_collection = get_mongo_collection('TestingDatabase', 'companies')
    
    # Fetch companies that haven't been processed by HunterScraper
    companies = companies_collection.find({'has_been_hunted': False})
    
    for company in companies:
        domain = company.get('website', '')
        if domain:
            hunter_scraper(domain)

            # Retrieve required fields
            company_name = company.get('company_name', 'Unknown Company')
            search_term_used = company.get('search_term_used', 'Unknown Search Term')

            # Update the has_been_hunted flag along with required fields
            companies_collection.update_one(
                {'_id': company['_id']},
                {'$set': {
                    'has_been_hunted': True,
                    'company_name': company_name,
                    'search_term_used': search_term_used
                }}
            )
            print(f"Updated Hunter status for company: {company_name}")


def main():
    # Step 1: Add new companies using GoogleMapsScraper
    for industry, location in industry_location_sets:
        run_google_maps_scraper(industry, location)

    # Step 2: Update companies using WebsiteScraper
    run_website_scraper()

    # Step 3: Enrich data using HunterScraper
    run_hunter_scraper()

if __name__ == '__main__':
    print(f"Starting Business Data Scraper at {datetime.now()}")
    main()
    print(f"Finished Business Data Scraper at {datetime.now()}")