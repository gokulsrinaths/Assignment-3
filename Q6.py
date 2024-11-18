import pymongo
import urllib.request
from bs4 import BeautifulSoup

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["crawlerdb"]
professors_collection = db["professors"]

professors_collection.create_index('email', unique=True)
print("Ensured unique index on 'email'.")

target_url = 'https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml'

try:
    response = urllib.request.urlopen(target_url)
    html_data = response.read().decode('utf-8')
except Exception as e:
    print(f"Failed to retrieve the page: {e}")
    exit(1)

soup = BeautifulSoup(html_data, 'html.parser')

faculty_profiles = soup.find_all('h2')

def get_label_value(strong_tag):
    label = strong_tag.get_text(strip=True).lower().rstrip(':')
    current = strong_tag.next_sibling
    value_parts = []
    while current and (isinstance(current, str) and current.strip() in ['', ':'] or current.name == 'br'):
        current = current.next_sibling
    while current and not (hasattr(current, 'name') and current.name == 'strong'):
        if isinstance(current, str):
            value_parts.append(current.strip())
        elif current.name == 'a':
            value_parts.append(current.get('href', '').strip() if label == 'web' else current.get_text(strip=True))
        elif current.name == 'br':
            pass  
        else:
            value_parts.append(current.get_text(strip=True))
        current = current.next_sibling
    return label, ' '.join(value_parts).strip()

processed_emails = set()

for name_tag in faculty_profiles:
    name = name_tag.get_text(strip=True)
    
    title = office = phone = email = website = None
    
    p_tag = name_tag.find_next_sibling('p')
    if p_tag:
        strong_tags = p_tag.find_all('strong')
        for strong_tag in strong_tags:
            label, value = get_label_value(strong_tag)
            if label == 'title':
                title = value
            elif label == 'office':
                office = value
            elif label == 'phone':
                phone = value
            elif label == 'email':
                email = value
            elif label == 'web':
                website = value

    if not name or not email:
        print(f"Missing critical information for a faculty member ({name}). Skipping.")
        continue

    if email in processed_emails:
        print(f"Duplicate email found in HTML for {name} ({email}). Skipping duplicate.")
        continue
    processed_emails.add(email)

    professor_data = {
        'name': name,
        'title': title,
        'office': office,
        'phone': phone,
        'email': email,
        'website': website
    }

    try:
        professors_collection.insert_one(professor_data)
        print(f"Inserted professor: {name}")
    except pymongo.errors.DuplicateKeyError:
        print(f"Professor with email {email} already exists in MongoDB. Skipping.")

print(f"Total unique professors inserted: {len(processed_emails)}")
