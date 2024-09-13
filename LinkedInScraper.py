from linkedin_api import Linkedin
from datetime import datetime, timezone
from MongoConnection import get_mongo_collection
from validators import validate_data, companies_schema, people_schema


# Authenticate using LinkedIn credentials
linkedin = Linkedin('user', 'pasword')

def normalize_url(url):
    """Remove the scheme (http or https) and www from the URL for comparison."""
    if url.startswith('http://'):
        url = url[len('http://'):]
    elif url.startswith('https://'):
        url = url[len('https://'):]
    
    if url.startswith('www.'):
        url = url[len('www.'):]
    
    return url

def scrape_linkedin(company_name, company_website):
    try:
        # Search for the company using its name
        normalized_website = normalize_url(company_website)

        results = linkedin.search_companies(keywords=[company_name])
        
        for result in results:
            
            # Fetch the company data
            company_data = linkedin.get_company(result['urn_id'])
            
            # Check if the company website matches
            linkedin_website = company_data.get('companyPageUrl', '').split('//')[-1]
            linkedin_website = normalize_url(linkedin_website)
            if normalized_website in linkedin_website:
                # Extract relevant data for each company and save to the database
                company_info = {
                    'name':company_data['name'],
                    'website_domain':company_data['companyPageUrl'].split('//')[-1],
                    'linkedin_id':company_data['entityUrn'].split(':')[-1],
                    'linkedin_profile_url':company_data['companyPageUrl'],
                    'year_founded':company_data.get('yearFounded', None),
                    'logo_url':company_data.get('logo', None),
                    'short_description':company_data.get('tagline', None),
                    'long_description':company_data.get('description', None),
                    'linkedin_description':company_data.get('specialities', None),
                    'linkedin_specialities':company_data.get('specialities', []),
                    'linkedin_industries':company_data.get('industries', []),
                    'linkedin_employees': company_data.get('size')      
                }
                
                return company_info
    except Exception as e:
        print(f"Error scraping LinkedIn for {company_name}: {e}")
        return None



def scrape_linkedin__companies_by_keywords(keywords,industry,headcount,location):

    results = linkedin.search_companies(keywords,industry,headcount,location)
        
    companyList = []
    # Extract relevant data for each company and save to the database
    for result in results:
        
        company_data = linkedin.get_company(result['urn_id'])
                
                # Extract desired information
        company_info = {
                'name':company_data['name'],
                'website_domain':company_data['companyPageUrl'].split('//')[-1],
                'linkedin_id':company_data['entityUrn'].split(':')[-1],
                'linkedin_profile_url':company_data['companyPageUrl'],
                'year_founded':company_data.get('yearFounded', None),
                'logo_url':company_data.get('logo', None),
                'short_description':company_data.get('tagline', None),
                'long_description':company_data.get('description', None),
                'linkedin_description':company_data.get('specialities', None),
                'linkedin_specialities':company_data.get('specialities', []),
                'linkedin_industries':company_data.get('industries', []),
                'linkedin_employees': company_data.get('size') 
                }
        companyList.append(company_info)
    
    return companyList

def update_linkedin_info():
    companies = Company.objects.filter(linkedin_profile_url__isnull=True, website_domain__isnull=False)
    print(f"Number of companies to update: {companies.count()}")

    for company in companies:
        print(f"Checking LinkedIn info for {company.name}")
        linkedin_data = scrape_linkedin(company.name, company.website_domain)
        print(linkedin_data)
        if linkedin_data:
            company.linkedin_id = linkedin_data.get('linkedin_id')
            company.linkedin_profile_url = linkedin_data.get('linkedin_profile_url')
            company.year_founded = linkedin_data.get('year_founded')
            company.logo_url = linkedin_data.get('logo_url')
            company.short_description = linkedin_data.get('short_description')
            company.long_description = linkedin_data.get('long_description')
            company.linkedin_description = linkedin_data.get('linkedin_description')
            company.linkedin_specialities = linkedin_data.get('linkedin_specialities')
            company.linkedin_industries = linkedin_data.get('linkedin_industries')
            company.linkedin_employees = linkedin_data.get('linkedin_employees')
            company.save()

            print(f"Updated LinkedIn info for {company.name}")
        else:
            print(f"No LinkedIn data found for {company.name}")



          
if __name__ == '__main__':
           
    update_linkedin_info()   
        