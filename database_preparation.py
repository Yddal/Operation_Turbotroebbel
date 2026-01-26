"""
Database Helper Module for Study Programs
Prepares data structures for MySQL database insertion without implementing connections.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class LearningOutcomes:
    """Learning outcomes for a course."""
    knowledge: Optional[str] = None
    skills: Optional[str] = None
    competence: Optional[str] = None


@dataclass
class Course:
    """Course/Subject data structure."""
    title: str
    credits: Optional[str] = None
    url: Optional[str] = None
    study_level: Optional[str] = None
    learning_outcomes: LearningOutcomes = field(default_factory=LearningOutcomes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insertion."""
        return {
            'title': self.title,
            'credits': self.credits,
            'url': self.url,
            'study_level': self.study_level,
            'learning_outcomes': asdict(self.learning_outcomes)
        }


@dataclass
class StudyProgram:
    """Study program data structure."""
    title: str
    description: Optional[str] = None
    credits: Optional[int] = None
    language: Optional[str] = None
    level: Optional[str] = None
    why_choose: Optional[str] = None
    what_learn: Optional[str] = None
    teaching_format: Optional[str] = None
    mandatory_attendance: Optional[str] = None
    police_certificate: Optional[str] = None
    career_opportunities: Optional[str] = None
    contact_info: Optional[str] = None
    study_url: Optional[str] = None
    courses: List[Course] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insertion."""
        return {
            'title': self.title,
            'description': self.description,
            'credits': self.credits,
            'language': self.language,
            'level': self.level,
            'why_choose': self.why_choose,
            'what_learn': self.what_learn,
            'teaching_format': self.teaching_format,
            'mandatory_attendance': self.mandatory_attendance,
            'police_certificate': self.police_certificate,
            'career_opportunities': self.career_opportunities,
            'contact_info': self.contact_info,
            'study_url': self.study_url
        }
    
    def to_database_format(self) -> Dict[str, Any]:
        """Convert to format suitable for database insertion."""
        data = self.to_dict()
        data['courses'] = [course.to_dict() for course in self.courses]
        return data


class DatabasePreparation:
    """Prepare extracted data for database insertion."""
    
    @staticmethod
    def validate_study_program(program: Dict[str, Any]) -> bool:
        """Validate study program data before database insertion."""
        required_fields = ['title']
        return all(program.get(field) is not None for field in required_fields)
    
    @staticmethod
    def validate_course(course: Dict[str, Any]) -> bool:
        """Validate course data before database insertion."""
        required_fields = ['title']
        return all(course.get(field) is not None for field in required_fields)
    
    @staticmethod
    def prepare_insert_statements(data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate SQL INSERT statements (as strings, not executed).
        
        Args:
            data: Extracted data structure
            
        Returns:
            Dictionary with 'study_programs' and 'courses' lists of SQL statements
        """
        statements = {
            'study_programs': [],
            'courses': []
        }
        
        # Prepare study programs inserts
        for program in data.get('study_programs', []):
            if not DatabasePreparation.validate_study_program(program):
                continue
            
            # Build INSERT statement (parameterized style)
            columns = []
            placeholders = []
            for key, value in program.items():
                if key not in ['id']:  # Skip auto-increment id
                    columns.append(f'`{key}`')
                    placeholders.append('%s')
            
            insert_sql = f"""
            INSERT INTO study_programs ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            """
            statements['study_programs'].append({
                'sql': insert_sql,
                'values': [program.get(col.strip('`')) for col in columns]
            })
        
        # Prepare courses inserts
        for course in data.get('courses', []):
            if not DatabasePreparation.validate_course(course):
                continue
            
            # Remove learning_outcomes for now (goes to separate table)
            course_copy = {k: v for k, v in course.items() if k != 'learning_outcomes'}
            
            columns = []
            placeholders = []
            for key, value in course_copy.items():
                columns.append(f'`{key}`')
                placeholders.append('%s')
            
            insert_sql = f"""
            INSERT INTO courses ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            """
            statements['courses'].append({
                'sql': insert_sql,
                'values': [course_copy.get(col.strip('`')) for col in columns]
            })
        
        return statements
    
    @staticmethod
    def generate_sql_script(data: Dict[str, Any]) -> str:
        """
        Generate a complete SQL script (as string) for data insertion.
        Can be manually reviewed before execution in MySQL.
        """
        statements = DatabasePreparation.prepare_insert_statements(data)
        
        script = "-- Generated SQL Insert Statements\n"
        script += "-- REVIEW BEFORE EXECUTION IN MYSQL DATABASE\n\n"
        
        # Add study programs
        script += "-- ===== STUDY PROGRAMS =====\n"
        for stmt in statements['study_programs']:
            script += stmt['sql'] + "\n"
        
        # Add courses
        script += "\n-- ===== COURSES =====\n"
        for stmt in statements['courses']:
            script += stmt['sql'] + "\n"
        
        return script


class DataStructureValidator:
    """Validate and report on data structure completeness."""
    
    @staticmethod
    def check_data_coverage(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check which fields are populated vs None.
        
        Returns:
            Dictionary with field coverage statistics
        """
        coverage = {
            'study_programs': {},
            'courses': {},
            'summary': {}
        }
        
        # Check study programs
        if data.get('study_programs'):
            program = data['study_programs'][0]
            total_fields = len(program)
            populated = sum(1 for v in program.values() if v is not None)
            
            coverage['study_programs'] = {
                'total_fields': total_fields,
                'populated_fields': populated,
                'coverage_percent': (populated / total_fields) * 100,
                'fields_status': {
                    k: 'populated' if v is not None else 'missing'
                    for k, v in program.items()
                }
            }
        
        # Check courses
        if data.get('courses'):
            course = data['courses'][0]
            total_fields = len(course)
            populated = sum(1 for v in course.values() if v is not None and v != {})
            
            coverage['courses'] = {
                'total_courses': len(data['courses']),
                'fields_per_course': total_fields,
                'avg_populated_fields': populated,
                'coverage_percent': (populated / total_fields) * 100,
                'fields_status': {
                    k: 'populated' if v is not None and v != {} else 'missing'
                    for k, v in course.items()
                }
            }
        
        coverage['summary'] = {
            'total_study_programs': len(data.get('study_programs', [])),
            'total_courses': len(data.get('courses', [])),
            'ready_for_database': True
        }
        
        return coverage


# Example usage and testing
if __name__ == "__main__":
    # Load extracted data
    with open('study_data_structure.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("="*70)
    print("DATABASE PREPARATION REPORT")
    print("="*70)
    
    # Validate data coverage
    validator = DataStructureValidator()
    coverage = validator.check_data_coverage(data)
    
    print("\n--- Data Coverage ---")
    print(f"Study Programs: {coverage['summary']['total_study_programs']}")
    print(f"Courses: {coverage['summary']['total_courses']}")
    print(f"\nStudy Program Coverage: {coverage['study_programs']['coverage_percent']:.1f}%")
    print(f"Course Coverage: {coverage['courses']['coverage_percent']:.1f}%")
    
    # Show missing fields
    print("\n--- Missing Fields in Study Programs ---")
    for field, status in coverage['study_programs']['fields_status'].items():
        if status == 'missing':
            print(f"  • {field}")
    
    print("\n--- Missing Fields in Courses ---")
    for field, status in coverage['courses']['fields_status'].items():
        if status == 'missing':
            print(f"  • {field}")
    
    # Generate SQL script
    print("\n" + "="*70)
    print("GENERATED SQL INSERT STATEMENTS")
    print("="*70)
    
    sql_script = DatabasePreparation.generate_sql_script(data)
    print(sql_script)
    
    # Save SQL script
    with open('insert_statements.sql', 'w', encoding='utf-8') as f:
        f.write(sql_script)
    print("\n✓ SQL script saved to: insert_statements.sql")
    
    # Save coverage report
    with open('data_coverage_report.json', 'w', encoding='utf-8') as f:
        json.dump(coverage, f, ensure_ascii=False, indent=2)
    print("✓ Coverage report saved to: data_coverage_report.json")
