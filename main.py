"""
Script to extract study program information from HTML and structure it with pandas.
Prepares data for MySQL database (without implementing MySQL functions).
Outputs result as JSON showing the data structure.
"""

import json
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Dict, List, Optional, Any

class StudyDataExtractor:
    """Extract and structure study program information from HTML."""
    
    def __init__(self, html_file_path: str):
        """Initialize with HTML file path."""
        self.html_file = html_file_path
        self.soup = None
        self.study_data = {}
        self.courses_data = []
        
    def load_html(self):
        """Load and parse HTML file."""
        try:
            with open(self.html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            self.soup = BeautifulSoup(html_content, 'html.parser')
            print(f"✓ HTML file loaded successfully")
        except FileNotFoundError:
            print(f"✗ HTML file not found: {self.html_file}")
            return False
        except Exception as e:
            print(f"✗ Error loading HTML: {e}")
            return False
        return True
    
    def extract_text(self, selector: str, attribute: Optional[str] = None) -> Optional[str]:
        """Extract text from a CSS selector or attribute."""
        try:
            element = self.soup.select_one(selector)
            if element:
                if attribute:
                    return element.get(attribute)
                return element.get_text(strip=True)
            return None
        except Exception:
            return None
    
    def extract_section_text(self, heading_text: str) -> Optional[str]:
        """Extract section text following a heading."""
        try:
            heading = None
            for h in self.soup.find_all(['h2', 'h3']):
                if h.get_text(strip=True) == heading_text:
                    heading = h
                    break
            
            if not heading:
                return None
            
            parts = []
            for el in heading.find_all_next():
                if el.name in ['h2', 'h3'] and el != heading:
                    break
                if el.name in ['p']:
                    text = el.get_text(strip=True)
                    if text:
                        parts.append(text)
            
            return "\n".join(parts) if parts else None
        except Exception:
            return None
    
    def extract_courses(self) -> List[Dict[str, Any]]:
        """Extract course/subject information."""
        courses = []
        try:
            # Find course links
            course_links = self.soup.find_all('a', class_='study-course__link')
            
            for link in course_links:
                course_title = link.select_one('.study-course__title')
                course_points = link.select_one('.study-course__points')
                course_url = link.get('href')
                
                course_dict = {
                    'title': course_title.get_text(strip=True) if course_title else None,
                    'credits': course_points.get_text(strip=True) if course_points else None,
                    'url': course_url,
                    'study_level': None,  # To be extracted from course page if available
                    'learning_outcomes': {
                        'knowledge': None,
                        'skills': None,
                        'competence': None
                    }
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
            study_info['title'] = title_elem.get_text(strip=True) if title_elem else None
            
            # Description (intro text)
            intro_elem = self.soup.select_one('.study-detail--intro__text')
            study_info['description'] = intro_elem.get_text(strip=True) if intro_elem else None
            
            # Credits
            credits_elem = self.soup.select_one('div.field--name-field-study-points .field__item')
            study_info['credits'] = credits_elem.get_text(strip=True) if credits_elem else None
            
            # Language
            language_elem = self.soup.select_one('div.field--name-field-language .field__item')
            study_info['language'] = language_elem.get_text(strip=True) if language_elem else None
            
            # Level
            level_elem = self.soup.select_one('div.field--name-field-level .field__item')
            study_info['level'] = level_elem.get_text(strip=True) if level_elem else None
            
            # Why choose this study
            study_info['why_choose'] = self.extract_section_text('Hvorfor velge dette studiet?')
            
            # What you learn
            learn_text = self.extract_section_text('Hva lærer du?')
            if not learn_text:
                # Try to get from the courses body section
                courses_body = self.soup.select_one('.study-detail--courses__body')
                if courses_body:
                    learn_text = courses_body.get_text(strip=True)
            study_info['what_learn'] = learn_text
            
            # Teaching format and attendance
            teaching_elem = self.soup.select_one('.study-detail--courses__body.other-info')
            if teaching_elem:
                teaching_text = teaching_elem.get_text(strip=True)
                # Extract teaching format
                if 'nettbasert deltid' in teaching_text.lower():
                    study_info['teaching_format'] = 'Nettbasert deltid med fysiske samlinger'
                study_info['mandatory_attendance'] = teaching_text
            
            # Career opportunities
            skills_elem = self.soup.select_one('div.field--name-field-skills-jobs')
            study_info['career_opportunities'] = skills_elem.get_text(strip=True) if skills_elem else None
            
            # Contact info
            contact_elem = self.soup.select_one('.study-detail--questions')
            if contact_elem:
                contact_text = contact_elem.get_text(strip=True)
                study_info['contact_info'] = contact_text
            
            # Study URL (from meta)
            canonical = self.soup.find('link', {'rel': 'canonical'})
            if canonical:
                study_info['study_url'] = canonical.get('href')
            
            # Police certificate - check in admission section
            admission_text = self.soup.get_text(strip=True)
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
                    'id': None,  # To be assigned by database
                    'title': study_info['title'],
                    'description': study_info['description'],
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
        
        # Convert None to null in JSON and pretty print
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
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
        
        print("\n" + "="*70)
        print("STUDY PROGRAMS DATA (DataFrame)")
        print("="*70)
        print(study_df.to_string())
        
        print("\n" + "="*70)
        print("COURSES DATA (DataFrame)")
        print("="*70)
        print(courses_df.to_string())
        
        return study_df, courses_df


# Main execution
if __name__ == "__main__":
    # Path to HTML file
    html_file_path = "Administrativ koordinator.html"
    
    # Initialize extractor
    extractor = StudyDataExtractor(html_file_path)
    
    # Load and process
    if extractor.load_html():
        print("\nExtracting study data...")
        extractor.display_dataframes_summary()
        
        print("\n" + "="*70)
        print("Exporting to JSON...")
        print("="*70)
        extractor.to_json()
        
        print("\n✓ Data extraction complete!")

