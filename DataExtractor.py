"""
Script to extract study program information from HTML and structure it with pandas.
Prepares data for MySQL database (without implementing MySQL functions).
Outputs result as JSON showing the data structure.
"""

import json
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from urllib.request import Request, urlopen

study_locations = {
    0: "Kongsberg",
    1: "Fredrikstad",
    2: "Kjeller",
    3: "Indre Østfold",
    4: "Drammen",
    5: "Jessheim",
    6: "Gauldal",
    7: "Mo i Rana",
    8: "Geilo",
    9: "Sørumsand"
}
study_types = {
    0: "Samlingsbasert",
    1: "Samlingsbasert 6 uker",
    2: "Samlingsbasert ca. 10 uker",
    3: "Samlingsbasert ca. 12 uker",
    4: "Samlingsbasert ca. 14 uker",
    5: "Samlingsbasert ca. 16 uker",
    6: "Samlingsbasert 7 måneder",
    7: "Samlingsbasert 1 år",
    8: "Samlingsbasert 2 år",
    9: "Samlingsbasert 3 år",
    10: "Samlingsbasert 4 år",
    11: "Heltid 2 år",
    12: "Deltid 2 år",
    13: "Deltid 3 år",
    14: "Stedbasert 2 år",
    15: "Nettstudium 1 år",
    16: "Enkeltemne ca. 12 uker"
}


class StudyDataExtractor:
    """Extract and structure study program information from HTML."""
    
    def __init__(self, html_content: str):
        """Initialize with HTML content."""
        self.html_content = html_content
        self.soup = None
        self.study_data = {}
        self.courses_data = []
        self.parse_html()
        
    def parse_html(self):
        """Parse HTML content."""
        try:
            self.soup = BeautifulSoup(self.html_content, 'html.parser')
            print("✓ HTML content parsed successfully")
        except Exception as e:
            print(f"✗ Error parsing HTML: {e}")
            return False
        return True
    
    def extract_text(self, selector: str, attribute: Optional[str] = None) -> Optional[str]:
        """Extract text from a CSS selector or attribute."""
        try:
            element = self.soup.select_one(selector)
            if element:
                if attribute:
                    return element.get(attribute)
                return element.get_text(separator=" | ",strip=True)
            return None
        except Exception:
            return None
    
    def extract_section_text(self, heading_text: str) -> Optional[str]:
        """Extract section text following a heading."""
        try:
            heading = None
            for h in self.soup.find_all(['h2', 'h3']):
                if h.get_text(separator=" | ",strip=True) == heading_text:
                    heading = h
                    break
            
            if not heading:
                return None
            
            parts = []
            for el in heading.find_all_next():
                if el.name in ['h2', 'h3'] and el != heading:
                    break
                if el.name in ['p']:
                    text = el.get_text(separator=" | ",strip=True)
                    if text:
                        parts.append(text)
            
            return "\n".join(parts) if parts else None
        except Exception:
            return None
    
    def extract_courses(self) -> List[Dict[str, Any]]:
        """Extract course/subject information from course pages."""
        courses = []
        try:
            # Find course links
            course_links = self.soup.find_all('a', class_='study-course__link')
            
            for link in course_links:
                course_title = link.select_one('.study-course__title')
                course_points = link.select_one('.study-course__points')
                course_url = link.get('href')
                
                course_points_Int = course_points.get_text(separator=" | ",strip=True).split(" ")
                
                try:
                    course_points_Int = int(course_points_Int[0])
                except ValueError:
                    print(ValueError)
                    course_points_Int = None

                # Extract course details from the course page
                course_id = None
                study_level = None
                learning_outcomes = {
                    'knowledge': None,
                    'skills': None,
                    'competence': None
                }
                
                # Fetch course page to extract additional info
                if course_url:
                    try:
                        req = Request(course_url, headers={"User-Agent": "Mozilla/5.0"})
                        course_html = urlopen(req).read().decode("utf-8", errors="ignore")
                        course_soup = BeautifulSoup(course_html, 'html.parser')
                        
                        # Extract course ID (Emnekode) from facts container
                        facts_container = course_soup.select_one('div#facts-containter')
                        if facts_container:
                            # Find all facts and look for Emnekode
                            facts_items = facts_container.find_all('li')
                            for fact_item in facts_items:
                                label = fact_item.select_one('.facts-label')
                                item = fact_item.select_one('.facts-item')
                                if label and item:
                                    label_text = label.get_text(separator=" | ",strip=True)
                                    item_text = item.get_text(separator=" | ",strip=True)
                                    
                                    if 'Emnekode' in label_text:
                                        course_id = item_text
                                    elif 'Studienivå' in label_text:
                                        study_level = item_text
                        
                        # Extract learning outcomes
                        knowledge_elem = course_soup.select_one('div.field-learning-outcome-knowledge.label-above')
                        if knowledge_elem:
                            learning_outcomes['knowledge'] = knowledge_elem.get_text(separator=" ",strip=True)
                        
                        skills_elem = course_soup.select_one('div.field-learning-outcome-skills.label-above')
                        if skills_elem:
                            learning_outcomes['skills'] = skills_elem.get_text(separator=" ",strip=True)
                        
                        competence_elem = course_soup.select_one('div.field-learning-outcome-reflec.label-above')
                        if competence_elem:
                            learning_outcomes['competence'] = competence_elem.get_text(separator=" ",strip=True)
                    
                    except Exception as e:
                        print(f"  Warning: Error extracting course details from {course_url}: {e}")

                course_dict = {
                    'id': course_id,
                    'title': course_title.get_text(separator=" | ",strip=True) if course_title else None,
                    'credits': course_points_Int,
                    'url': course_url,
                    'study_level': study_level,
                    'learning_outcomes': learning_outcomes
                }
                courses.append(course_dict)
        except Exception as e:
            print(f"  Warning: Error extracting courses: {e}")
        
        return courses
    
    def extract_study_info(self) -> Dict[str, Any]:
        """Extract main study program information."""
        study_info = {
            'title': None,
            'description': None,
            'study_category': None,
            'study_location': None,
            'study_type': None,
            'credits': None,
            'language': None,
            'level': None,
            'why_choose': None,
            'what_learn': None,
            'teaching_format': None,
            'mandatory_attendance': None,
            'police_certificate': None,
            'career_opportunities': None,
            'contact_info': None,
            'study_url': None
        }
        
        try:
            # Title
            title_elem = self.soup.select_one('.study-detail__title')
            study_info['title'] = title_elem.get_text(separator=" | ",strip=True) if title_elem else None
            
            # Description (intro text)
            intro_elem = self.soup.select_one('.study-detail--intro__text')
            study_info['description'] = intro_elem.get_text(separator=" | ",strip=True) if intro_elem else None
            
            # Study Category
            intro_elem = self.soup.select_one('.study-detail--intro__tag')
            study_info['study_category'] = intro_elem.get_text(strip=True) if intro_elem else None

            # Study Location:
            location_info = self.soup.select_one('.study-detail--campus__select')
            location_info = location_info.get_text(separator=" | ",strip=True) if intro_elem else None
            
            study_info['study_location'], study_info['study_type'] = match_location_and_studyType(location_info)
            
            # Credits
            credits_elem = self.soup.select_one('div.field.field--name-field-study-points.field--type-integer.field--label-hidden.field__item')
            credits_elem = credits_elem.get_text(separator=" | ",strip=True)
            try:
                credits_elem_int = int(credits_elem)
            except ValueError:
                print(ValueError)
                credits_elem_int = None
            
            study_info['credits'] = credits_elem_int
            
            # Language
            language_elem = self.soup.select_one('div.field.field--name-field-language.field--type-entity-reference.field--label-hidden.field__item')
            study_info['language'] = language_elem.get_text(separator=" | ",strip=True) if language_elem else None
            
            # Level
            level_elem = self.soup.select_one('div.field.field--name-field-level.field--type-entity-reference.field--label-hidden.field__item')
            study_info['level'] = level_elem.get_text(separator=" | ",strip=True) if level_elem else None
            
            # Why choose this study
            study_info['why_choose'] = self.extract_section_text('Hvorfor velge dette studiet?')
            
            # What you learn
            learn_text = self.extract_section_text('Hva lærer du?')
            if not learn_text:
                # Try to get from the courses body section
                courses_body = self.soup.select_one('.study-detail--courses__body')
                if courses_body:
                    learn_text = courses_body.get_text(separator=" | ",strip=True)
            study_info['what_learn'] = learn_text
            
            # Teaching format and attendance
            #TODO: Skal denne fjernes? Informasjonen står allerede i mandatory_attendance.
            teaching_elem = self.soup.select_one('.study-detail--courses__body.other-info')
            if teaching_elem:
                teaching_text = teaching_elem.get_text(separator=" ",strip=True)
                # Extract teaching format
                if 'nettbasert deltid' in teaching_text.lower():
                    study_info['teaching_format'] = 'Nettbasert deltid med fysiske samlinger'
                study_info['mandatory_attendance'] = teaching_text

            # Career opportunities
            skills_elem = self.soup.select_one('div.field--name-field-skills-jobs')
            study_info['career_opportunities'] = skills_elem.get_text(separator=" ",strip=True) if skills_elem else None
            
            # Contact info
            contact_elem = self.soup.select_one('.study-detail--questions')
            if contact_elem:
                contact_text = contact_elem.get_text(separator=" | ",strip=True)
                study_info['contact_info'] = contact_text
            
            # Study URL (from meta)
            canonical = self.soup.find('link', {'rel': 'canonical'})
            if canonical:
                study_info['study_url'] = canonical.get('href')
            
            # Police certificate - check in admission section
            admission_text = self.soup.get_text(separator=" | ",strip=True)
            study_info['police_certificate'] = None if 'politiattest' not in admission_text.lower() else 'Sjekk opptakskrav'
            
        except Exception as e:
            print(f"Error extracting study info: {e}")
        
        return study_info
    
    def structure_for_database(self) -> Dict[str, Any]:
        """Structure all extracted data for database storage."""
        study_info = self.extract_study_info()
        courses = self.extract_courses()
        
        # Create structured data object
        data_structure = {
            'study_programs': [
                {
                    'id': study_info['title'] + " - " + str(study_info['credits']),  # To be assigned by database
                    'title': study_info['title'],
                    'description': study_info['description'],
                    'study_category': study_info['study_category'],
                    'study_location': study_info['study_location'],
                    'study_type': study_info['study_type'],
                    'credits': study_info['credits'],
                    'language': study_info['language'],
                    'level': study_info['level'],
                    'why_choose': study_info['why_choose'],
                    'what_learn': study_info['what_learn'],
                    'teaching_format': study_info['teaching_format'],
                    'mandatory_attendance': study_info['mandatory_attendance'],
                    'police_certificate': study_info['police_certificate'],
                    'career_opportunities': study_info['career_opportunities'],
                    'contact_info': study_info['contact_info'],
                    'study_url': study_info['study_url']
                }
            ],
            'courses': courses
        }
        
        return data_structure
    
    def to_dataframes(self):
        """Convert structured data to pandas DataFrames.
        
        Returns:
            tuple: (study_df, courses_df) - Two pandas DataFrames
        """
        data = self.structure_for_database()
        
        # Study programs DataFrame
        study_df = pd.DataFrame(data['study_programs'])
        
        # Courses DataFrame
        courses_df = pd.DataFrame(data['courses'])
        
        return study_df, courses_df
    
    def to_json(self, output_file: str = 'study_data_structure.json'):
        """Export structured data to JSON file."""
        data = self.structure_for_database()
        folder = "json_for_processing/"
        
        # Convert None to null in JSON and pretty print
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        # Define the full path to the file
        if data['study_programs'][0]['id'] is not None:
            output_file = folder + data['study_programs'][0]['id'] + ".json"
        else:
            output_file = folder + output_file
        
        output_file = Path(output_file)
        # sjekk om mappe eksisterer, hvis ikke opprett.
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_data)
            print(f"✓ JSON file created: {output_file}")
            return json_data
        except Exception as e:
            print(f"✗ Error writing JSON file: {e}")
            return None
    
    def display_dataframes_summary(self):
        """Display summary of extracted data."""
        study_df, courses_df = self.to_dataframes()
        
        #print("\n" + "="*70)
        #print("STUDY PROGRAMS DATA (DataFrame)")
        #print("="*70)
        #print(study_df.to_string())
        
        #print("\n" + "="*70)
        #print("COURSES DATA (DataFrame)")
        #print("="*70)
        #print(courses_df.to_string())
        
        return study_df, courses_df

def match_location_and_studyType(object):
    global study_locations, study_types
    object = object.split(sep=" | ") # split ut lokasjonene. Studietype splittes senere.
    study_location = {}
    study_type = {}
    for o in object:
        object_splitted = o.split(sep="(") # splitt ut lokasjon og studietype 

        # Match lokasjon mot ID i databasen.
        for loc in study_locations:
            target = object_splitted[0].strip()
            
            #print(f"Prøver å matche '{study_locations[loc]}' mot '{target}'")
            if target not in study_locations.values():
                print(f"lokasjon ikke funnet: '{target}'")
                break
            if study_locations[loc] == target:
                #print(f"match found at location ID: {loc}, adding..")
                study_location[loc] = target
                #print(f"Lokasjon: {target}, plassert som ID: {loc}")
        # Match studietype mot ID i databasen.
        for type in study_types:
            target = object_splitted[1].replace(")","").strip()
            if target not in study_types.values():
                print(f"studietype ikke funnet: '{target}'")
                break
            #print(f"Prøver å matche '{study_types[type]}' mot '{target}'")
            if study_types[type] == target:
                #print(f"match found at type ID: {type}, adding..")
                study_type[type] = target
                #print(f"studietype: {target}, plassert som ID: {type}")
            
    return study_location, study_type

def extract(url):
    # Fetch HTML from the URL
    try:
        #print(f"Fetching data from URL: {url}")
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html_content = urlopen(req).read().decode("utf-8", errors="ignore")
        #print("✓ Data fetched successfully from URL\n")
    except Exception as e:
        print(f"✗ Error fetching URL: {e}")
        exit(1)
    
    # Initialize extractor with HTML content
    extractor = StudyDataExtractor(html_content)
    
    # Load and process
    if extractor.soup:
        #print("Extracting study data...")
        extractor.display_dataframes_summary()
        
        #print("\n" + "="*70)
        #print("Exporting to JSON...")
        #print("="*70)
        extractor.to_json()
        
        #print("\n✓ Data extraction complete!")

# Test commit