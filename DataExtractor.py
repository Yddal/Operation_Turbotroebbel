"""
Script to extract study program information from HTML and structure it with pandas.
Prepares data for MySQL database (without implementing MySQL functions).
Outputs result as JSON showing the data structure.
"""

import json
import pandas as pd
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from urllib.request import Request, urlopen


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
        """Extract course/subject information from course pages."""
        courses = []
        try:
            # Find course links
            course_links = self.soup.find_all('a', class_='study-course__link')
            
            for link in course_links:
                course_title = link.select_one('.study-course__title')
                course_points = link.select_one('.study-course__points')
                course_url = link.get('href')
                
                course_points_Int = course_points.get_text(separator=" ",strip=True).split(" ")
                
                #print(course_points_Int)
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
                                    label_text = label.get_text(strip=True)
                                    item_text = item.get_text(strip=True)
                                    
                                    if 'Emnekode' in label_text:
                                        course_id = item_text
                                    elif 'Studienivå' in label_text:
                                        study_level = item_text
                        
                        # Extract learning outcomes
                        knowledge_elem = course_soup.select_one('div.field-learning-outcome-knowledge.label-above')
                        if knowledge_elem:
                            learning_outcomes['knowledge'] = knowledge_elem.get_text(strip=True)
                        
                        skills_elem = course_soup.select_one('div.field-learning-outcome-skills.label-above')
                        if skills_elem:
                            learning_outcomes['skills'] = skills_elem.get_text(strip=True)
                        
                        competence_elem = course_soup.select_one('div.field-learning-outcome-reflec.label-above')
                        if competence_elem:
                            learning_outcomes['competence'] = competence_elem.get_text(strip=True)
                    
                    except Exception as e:
                        print(f"  Warning: Error extracting course details from {course_url}: {e}")

                course_dict = {
                    'id': course_id,
                    'title': course_title.get_text(strip=True) if course_title else None,
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

url = "https://fagskolen-viken.no/studier/ledelse/administrativ-koordinator"

# Main execution
if __name__ == "__main__":
    # Fetch HTML from the URL
    try:
        print(f"Fetching data from URL: {url}")
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html_content = urlopen(req).read().decode("utf-8", errors="ignore")
        print("✓ Data fetched successfully from URL\n")
    except Exception as e:
        print(f"✗ Error fetching URL: {e}")
        exit(1)
    
    # Initialize extractor with HTML content
    extractor = StudyDataExtractor(html_content)
    
    # Load and process
    if extractor.soup:
        print("Extracting study data...")
        extractor.display_dataframes_summary()
        
        print("\n" + "="*70)
        print("Exporting to JSON...")
        print("="*70)
        extractor.to_json()
        
        print("\n✓ Data extraction complete!")

