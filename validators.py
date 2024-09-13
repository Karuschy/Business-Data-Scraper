from cerberus import Validator

# User collection schema
user_schema = {
    'username': {'type': 'string', 'required': True},
    'password': {'type': 'string', 'required': True},
    'role': {'type': 'string', 'allowed': ['admin', 'user'], 'required': True}
}

# Companies collection schema
companies_schema = {
    'company_name': {'type': 'string', 'required': True},  # Only company_name is required
    'address': {'type': 'string', 'nullable': True},  # Nullable fields can be None or empty
    'industry': {'type': 'string', 'nullable': True},
    'website': {'type': 'string', 'nullable': True},
    'linkedin_url': {'type': 'string', 'nullable': True},
    'year_founded': {'type': 'string', 'nullable': True},
    'linkedin_employees': {'type': 'string', 'nullable': True},
    'phone_number': {'type': 'string', 'nullable': True},
    'email': {'type': 'string', 'nullable': True, 'regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'},
    'linkedin_description': {'type': 'string', 'nullable': True},
    'search_term_used': {'type': 'string', 'required': True},
    'scrape_timestamp': {'type': 'datetime', 'required': True},
     'has_been_hunted': {'type': 'boolean', 'default': False},
    'other_emails': {  # New field for other emails, an array of strings
        'type': 'list',
        'schema': {'type': 'string', 'regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'},
        'nullable': True  # This field can be None if no other emails are found
    }

}

# People collection schema
people_schema = {
    'first_name': {'type': 'string', 'required': True},  # Only first_name is required
    'last_name': {'type': 'string', 'required': True},   # Last name is also required
    'position': {'type': 'string', 'nullable': True},
    'company_name': {'type': 'string', 'required': True},
    'email': {'type': 'string', 'nullable': True, 'regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'},
    'linkedin_profile': {'type': 'string', 'nullable': True},
     'has_been_hunted': {'type': 'boolean', 'default': False},
    'scrape_timestamp': {'type': 'datetime', 'required': True}

}

def validate_data(data, schema):
    """
    Validates the data against the given schema using Cerberus.
    
    :param data: The data to be validated.
    :param schema: The schema to validate against.
    :return: True if data is valid, raises ValueError if not.
    """
    v = Validator(schema, allow_unknown=False)  
    if not v.validate(data):
        raise ValueError(f"Validation error: {v.errors}")
    return True