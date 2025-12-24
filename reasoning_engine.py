"""
Reasoning Engine for Course Recommendation System
Implements rule-based reasoning and scoring logic
"""

import json
import os
from typing import Dict, List, Set, Tuple
from pathlib import Path


def get_base_path():
    """Get the base path for knowledge files, works both locally and on Streamlit Cloud"""
    # Get the directory where this script is located
    return Path(__file__).parent


class ReasoningEngine:
    def __init__(self, courses_path: str = None, 
                 rules_path: str = None,
                 teaching_plans_path: str = None):
        """Initialize reasoning engine with knowledge base"""
        base_path = get_base_path()
        
        # Use default paths relative to the script location
        if courses_path is None:
            courses_path = base_path / "knowledge" / "courses.json"
        if rules_path is None:
            rules_path = base_path / "knowledge" / "rules.json"
        if teaching_plans_path is None:
            teaching_plans_path = base_path / "knowledge" / "teaching_plans.json"
            
        self.courses = self._load_courses(courses_path)
        self.rules = self._load_rules(rules_path)
        self.teaching_plans = self._load_teaching_plans(teaching_plans_path)
        self.courses_dict = {c['course_id']: c for c in self.courses}
        
    def _load_courses(self, path: str) -> List[Dict]:
        """Load courses from JSON file"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['courses']
    
    def _load_rules(self, path: str) -> Dict:
        """Load rules from JSON file"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_teaching_plans(self, path: str) -> Dict:
        """Load teaching plans from JSON file"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def determine_cohort(self, enrollment_year: int) -> str:
        """
        Determine student cohort (K18/K19/K20) from enrollment year
        
        Args:
            enrollment_year: Year student enrolled (e.g., 2023, 2024, 2025)
            
        Returns:
            Cohort code (e.g., 'K18', 'K19', 'K20')
        """
        cohort_mappings = self.teaching_plans.get('cohort_mappings', {})
        
        for cohort, info in cohort_mappings.items():
            if info['enrollment_year'] == enrollment_year:
                return cohort
        
        # Default to most recent cohort
        return 'K20'
    
    def get_curriculum_for_cohort(self, cohort: str, major: str) -> str:
        """
        Get curriculum version for a given cohort
        
        Args:
            cohort: Cohort code (K18/K19/K20)
            major: Major (KHMT/TTNT)
            
        Returns:
            Curriculum key (e.g., 'KHMT_K2023', 'TTNT_K2024')
        """
        cohort_mappings = self.teaching_plans.get('cohort_mappings', {})
        
        if cohort in cohort_mappings:
            curriculum_version = cohort_mappings[cohort]['curriculum']
            return f"{major}_{curriculum_version}"
        
        # Default to K2024 (latest)
        return f"{major}_K2024"
    
    def get_semester_courses(self, major: str, semester_number: int, cohort: str = 'K20') -> Dict[str, List[Dict]]:
        """
        Get courses for a specific semester according to teaching plan
        
        Args:
            major: Major (KHMT/TTNT)
            semester_number: Semester number (1-7)
            cohort: Cohort code (K18/K19/K20)
            
        Returns:
            Dictionary with 'compulsory', 'elective' course lists and 'elective_slots'
        """
        curriculum_key = self.get_curriculum_for_cohort(cohort, major)
        teaching_plan = self.teaching_plans.get('teaching_plans', {}).get(curriculum_key, {})
        
        semester_data = teaching_plan.get('semesters', {}).get(str(semester_number), {})
        courses = semester_data.get('courses', [])
        
        compulsory = []
        elective = []
        elective_slots = []  # New: structured elective slots with choices
        
        for course in courses:
            course_id = course.get('id')
            course_type = course.get('type')
            
            # Handle NEW elective_slot format with choices
            if 'elective_slot' in course:
                slot_info = {
                    'slot_name': course.get('elective_slot'),
                    'credits': course.get('credits', 4),
                    'choices': []
                }
                # Expand choices to full course details
                for choice_id in course.get('choices', []):
                    if choice_id in self.courses_dict:
                        choice_course = self.courses_dict[choice_id].copy()
                        choice_course['teaching_plan_type'] = 'elective'
                        slot_info['choices'].append(choice_course)
                elective_slots.append(slot_info)
                # Also add first choice as representative to elective list
                if slot_info['choices']:
                    rep = slot_info['choices'][0].copy()
                    rep['is_elective_slot'] = True
                    rep['slot_name'] = slot_info['slot_name']
                    rep['all_choices'] = [c['course_id'] for c in slot_info['choices']]
                    elective.append(rep)
                continue
            
            # Handle old placeholder entries (e.g., "Môn chuyên ngành 3") or courses with '-' as id
            if not course_id or course_id == '-':
                placeholder_course = {
                    'course_id': course_id if course_id == '-' else None,
                    'course_name': course.get('name') or course.get('placeholder', 'Môn tự chọn'),
                    'credits': course.get('credits', 4),
                    'prerequisites': [],
                    'is_placeholder': True,
                    'teaching_plan_type': course_type
                }
                if course_type == 'compulsory':
                    compulsory.append(placeholder_course)
                else:
                    elective.append(placeholder_course)
                continue
            
            # Get full course details from courses_dict
            if course_id in self.courses_dict:
                course_detail = self.courses_dict[course_id].copy()
                course_detail['teaching_plan_type'] = course_type
                
                if course_type == 'compulsory':
                    compulsory.append(course_detail)
                else:
                    elective.append(course_detail)
        
        return {
            'compulsory': compulsory,
            'elective': elective,
            'elective_slots': elective_slots,  # NEW: structured elective slots
            'total_credits': semester_data.get('total_credits', 0)
        }
    
    def calculate_graduation_progress(self, student_data: Dict) -> Dict:
        """
        Calculate graduation progress based on completed courses
        
        Quy đổi tín chỉ:
        - Tín chỉ chuyên ngành thừa → Tốt nghiệp → Tự do (theo thứ tự ưu tiên)
        
        Args:
            student_data: Student information including completed_courses, major, cohort
            
        Returns:
            Dictionary with progress for each credit category
        """
        major = student_data.get('major')
        cohort = student_data.get('cohort', 'K20')
        completed_courses = student_data.get('completed_courses', [])
        
        # Get graduation requirements
        curriculum_key = self.get_curriculum_for_cohort(cohort, major)
        graduation_reqs = self.rules.get('graduation_requirements', {}).get(curriculum_key, {})
        
        # Get required credits for each category first
        categories_req = graduation_reqs.get('categories', {})
        required = {
            'dai_cuong': categories_req.get('dai_cuong', {}).get('total', 45),
            'co_so_nganh': categories_req.get('co_so_nganh', {}).get('min_credits', 45),
            'chuyen_nganh': categories_req.get('chuyen_nganh', {}).get('min_credits', 16),
            'tot_nghiep': categories_req.get('tot_nghiep', {}).get('credits', 10),
            'tu_chon_tu_do': categories_req.get('tu_chon_tu_do', categories_req.get('tu_chon_lien_nganh', {})).get('min_credits', 10)
        }
        
        # Initialize raw completed credits
        raw_completed = {cat: 0 for cat in required.keys()}
        total_completed = 0
        
        # Calculate raw credits by category
        for course_id in completed_courses:
            if course_id not in self.courses_dict:
                continue
            
            course = self.courses_dict[course_id]
            credits = course.get('credits', 0)
            course_group = course.get('course_group', '')
            
            total_completed += credits
            
            # Map course_group to category
            if course_group == 'Đại cương':
                category = 'dai_cuong'
            elif course_group == 'Cơ sở ngành':
                category = 'co_so_nganh'
            elif course_group == 'Chuyên ngành':
                category = 'chuyen_nganh'
            elif course_group == 'Tốt nghiệp':
                category = 'tot_nghiep'
            else:
                category = 'tu_chon_tu_do'
            
            raw_completed[category] += credits
        
        # Quy đổi tín chỉ thừa: Chuyên ngành → Tốt nghiệp → Tự do
        final_completed = raw_completed.copy()
        
        # Tính tín chỉ thừa từ chuyên ngành
        chuyen_nganh_excess = max(0, raw_completed['chuyen_nganh'] - required['chuyen_nganh'])
        if chuyen_nganh_excess > 0:
            # Cap chuyên ngành at requirement
            final_completed['chuyen_nganh'] = required['chuyen_nganh']
            
            # Quy đổi sang tốt nghiệp trước (nếu còn thiếu)
            tot_nghiep_needed = required['tot_nghiep'] - final_completed['tot_nghiep']
            if tot_nghiep_needed > 0:
                transfer_to_tn = min(chuyen_nganh_excess, tot_nghiep_needed)
                final_completed['tot_nghiep'] += transfer_to_tn
                chuyen_nganh_excess -= transfer_to_tn
            
            # Phần còn lại quy đổi sang tự do
            if chuyen_nganh_excess > 0:
                final_completed['tu_chon_tu_do'] += chuyen_nganh_excess
        
        # Tương tự cho cơ sở ngành thừa → tự do
        co_so_excess = max(0, raw_completed['co_so_nganh'] - required['co_so_nganh'])
        if co_so_excess > 0:
            final_completed['co_so_nganh'] = required['co_so_nganh']
            final_completed['tu_chon_tu_do'] += co_so_excess
        
        # Build progress dictionary
        progress = {
            'total_required': graduation_reqs.get('total_credits', 126),
            'total_completed': total_completed,
            'categories': {}
        }
        
        for cat in required.keys():
            progress['categories'][cat] = {
                'completed': final_completed[cat],
                'required': required[cat],
                'raw_completed': raw_completed[cat]
            }
        
        return progress
    
    def get_course_offered_semesters(self, course_id: str, major: str, cohort: str) -> List[str]:
        """
        Get which semesters a course is typically offered (HK1 or HK2)
        Based on teaching plan - courses usually repeat every 2 semesters
        
        Args:
            course_id: Course ID
            major: Student's major
            cohort: Student's cohort
            
        Returns:
            List of semester types where course is offered ['HK1'] or ['HK2'] or ['HK1', 'HK2']
        """
        curriculum_key = self.get_curriculum_for_cohort(cohort, major)
        teaching_plan = self.teaching_plans.get('teaching_plans', {}).get(curriculum_key, {})
        
        offered_semesters = set()
        
        for semester_num, semester_data in teaching_plan.get('semesters', {}).items():
            sem_num = int(semester_num)
            semester_type = "HK1" if sem_num % 2 == 1 else "HK2"
            
            # Check courses - support both 'id' and 'course_id' keys
            for course in semester_data.get('courses', []):
                cid = course.get('course_id') or course.get('id')
                if cid == course_id:
                    offered_semesters.add(semester_type)
                # Check elective choices
                if 'choices' in course and course_id in course['choices']:
                    offered_semesters.add(semester_type)
        
        return list(offered_semesters) if offered_semesters else ['HK1', 'HK2']  # Default: both
    
    def get_next_retake_semester(self, course_id: str, current_semester_number: int, 
                                  major: str, cohort: str) -> int:
        """
        Get the next semester number when a failed course can be retaken
        Courses typically offered every 2 semesters (HK1->HK1, HK2->HK2)
        
        Args:
            course_id: Failed course ID
            current_semester_number: Current semester (1-8)
            major: Student's major
            cohort: Student's cohort
            
        Returns:
            Next semester number when course is available
        """
        offered = self.get_course_offered_semesters(course_id, major, cohort)
        current_type = "HK1" if current_semester_number % 2 == 1 else "HK2"
        next_semester = current_semester_number + 1
        
        # If course is offered in both semesters, can retake next semester
        if len(offered) == 2:
            return next_semester
        
        # Otherwise, find next matching semester type
        offered_type = offered[0] if offered else current_type
        
        while next_semester <= 8:
            sem_type = "HK1" if next_semester % 2 == 1 else "HK2"
            if sem_type == offered_type:
                return next_semester
            next_semester += 1
        
        return current_semester_number + 2  # Default: skip one semester
    
    def prioritize_courses_by_teaching_plan(self, eligible_courses: List[Dict], 
                                           semester_number: int, major: str, cohort: str) -> List[Dict]:
        """
        Prioritize courses based on teaching plan: compulsory first, then electives
        
        Args:
            eligible_courses: List of eligible courses
            semester_number: Current semester number
            major: Student's major
            cohort: Student's cohort
            
        Returns:
            Prioritized list of courses
        """
        # Get planned courses for this semester
        planned = self.get_semester_courses(major, semester_number, cohort)
        planned_compulsory_ids = [c['course_id'] for c in planned['compulsory']]
        planned_elective_ids = [c['course_id'] for c in planned['elective']]
        
        # Separate courses into priority groups
        priority_1 = []  # Compulsory courses in teaching plan
        priority_2 = []  # Elective courses in teaching plan
        priority_3 = []  # Other compulsory courses (from previous semesters)
        priority_4 = []  # Other elective courses
        
        for course in eligible_courses:
            course_id = course['course_id']
            course_group = course.get('course_group', '')
            
            if course_id in planned_compulsory_ids:
                priority_1.append(course)
            elif course_id in planned_elective_ids:
                priority_2.append(course)
            elif course_group in ['Đại cương', 'Cơ sở ngành']:
                priority_3.append(course)
            else:
                priority_4.append(course)
        
        return priority_1 + priority_2 + priority_3 + priority_4
    
    def check_prerequisites(self, course_id: str, completed_courses: List[str]) -> Tuple[bool, List[str]]:
        """
        Check if student has completed all prerequisites for a course
        
        Returns:
            (is_eligible, missing_prerequisites)
        """
        course = self.courses_dict.get(course_id)
        if not course:
            return False, []
        
        prerequisites = course.get('prerequisites', [])
        missing = [pre for pre in prerequisites if pre not in completed_courses]
        
        return len(missing) == 0, missing
    
    def get_eligible_courses(self, student_data: Dict, target_year: int = None, 
                            target_semester: str = None) -> List[Dict]:
        """
        Get all courses student is eligible to take in target semester
        
        Args:
            student_data: Student information including completed_courses, failed_courses
            target_year: Target year (1-4) - optional
            target_semester: Target semester (HK1/HK2) - optional
            
        Returns:
            List of eligible courses
        """
        completed = student_data.get('completed_courses', [])
        current_courses = student_data.get('current_courses', [])
        failed_courses = student_data.get('failed_courses', [])
        major = student_data.get('major')
        cohort = student_data.get('cohort', 'K20')
        
        # Build elective slot groups for checking alternatives
        elective_slot_groups = self._get_elective_slot_groups(major, cohort)
        
        eligible = []
        
        # Prioritize failed courses that are prerequisites
        failed_priority = []
        
        for course in self.courses:
            course_id = course['course_id']
            
            # Skip PE012 (removed from system)
            if course_id == 'PE012':
                continue
            
            # Skip if already completed or currently taking
            if course_id in completed or course_id in current_courses:
                continue
            
            # Check major compatibility
            if major not in course['major']:
                continue
            
            # Check if this is a failed course
            is_failed = course_id in failed_courses
            
            # If failed, check if alternative in same slot is completed/in-progress
            if is_failed and course_id in elective_slot_groups:
                alternatives = elective_slot_groups[course_id]
                # Check if any alternative is completed or being taken
                alternative_done = any(
                    alt in completed or alt in current_courses 
                    for alt in alternatives if alt != course_id
                )
                if alternative_done:
                    # Skip this failed course, student has alternative
                    continue
            
            # Check prerequisites
            is_eligible, missing = self.check_prerequisites(course_id, completed)
            if not is_eligible:
                continue
            
            # Add course to appropriate list
            course_copy = course.copy()
            course_copy['is_failed'] = is_failed
            course_copy['is_prerequisite_for_other'] = self._is_prerequisite_for_others(course_id)
            
            if is_failed and course_copy['is_prerequisite_for_other']:
                failed_priority.append(course_copy)
            else:
                eligible.append(course_copy)
        
        # Return failed prerequisites first, then other courses
        return failed_priority + eligible
    
    def _get_elective_slot_groups(self, major: str, cohort: str) -> Dict[str, List[str]]:
        """
        Build a mapping of course_id -> list of alternative course_ids in same slot
        
        Returns:
            Dict mapping each course to its alternatives in the same elective slot
        """
        curriculum_key = self.get_curriculum_for_cohort(cohort, major)
        teaching_plan = self.teaching_plans.get('teaching_plans', {}).get(curriculum_key, {})
        
        slot_groups = {}
        
        for semester_num, semester_data in teaching_plan.get('semesters', {}).items():
            for course in semester_data.get('courses', []):
                if 'elective_slot' in course:
                    choices = course.get('choices', [])
                    # Map each choice to all choices in this slot
                    for choice_id in choices:
                        slot_groups[choice_id] = choices
        
        return slot_groups
    
    def _is_prerequisite_for_others(self, course_id: str) -> bool:
        """Check if a course is a prerequisite for other courses"""
        for course in self.courses:
            if course_id in course.get('prerequisites', []):
                return True
        return False
    
    def _check_special_course_rules(self, course: Dict, year: int, semester: str) -> bool:
        """Apply hard rules for AV, PE, ME courses"""
        course_id = course['course_id']
        
        # English courses year constraint
        if course_id == 'ENG01' and year > 1:
            return False
        if course_id == 'ENG02' and year > 2:
            return False
        if course_id == 'ENG03' and year > 3:
            return False
        
        # PE semester constraints
        if course_id == 'PE231' and semester != 'HK1':
            return False
        if course_id == 'PE232' and semester != 'HK2':
            return False
        
        # ME fixed in Year 1 HK1
        if course_id == 'ME001' and (year != 1 or semester != 'HK1'):
            return False
        
        return True
    
    def compute_difficulty_score(self, course: Dict) -> float:
        """
        Calculate course difficulty score
        
        Formula: difficulty = 2 × w1 × Npre + w2 × Yrec + w3 × Wgroup
        """
        weights = self.rules['difficulty_weights']
        w1 = weights['w1_prerequisite']
        w2 = weights['w2_year']
        w3 = weights['w3_group']
        
        # Number of prerequisites (with double weight)
        n_pre = len(course.get('prerequisites', []))
        
        # Recommended year
        y_rec = course.get('recommended_year', 1)
        
        # Course group weight
        group = course.get('course_group', 'General')
        w_group = weights['group_weights'].get(group, 1)
        
        difficulty = 2 * w1 * n_pre + w2 * y_rec + w3 * w_group
        
        return difficulty
    
    def infer_student_ability(self, student_data: Dict) -> Dict[str, float]:
        """
        Infer student abilities from completed courses and grades
        
        Returns:
            Dictionary with programming_level, computational_thinking, academic_readiness
        
        Academic Readiness calculation based on IT and MA courses:
        - Low (1.0): Completed ≥ 1 course, mostly Pass level (< 7.0)
        - Medium (2.0): Completed ≥ 50% courses, average ≥ 7.0
        - High (3.0): Completed 100% courses, mostly ≥ 8.5
        """
        completed = student_data.get('completed_courses', [])
        current_year = student_data.get('current_year', 1)
        course_grades = student_data.get('course_grades', {})  # NEW: Get grades
        
        # Infer programming level based on grades
        programming_courses = {
            'IT001': 1,  # Nhập môn lập trình
            'IT002': 2,  # Lập trình hướng đối tượng  
            'CS116': 3   # Lập trình Python cho ML
        }
        
        # Calculate programming level with grade bonus
        prog_completed = [c for c in completed if c in programming_courses]
        if prog_completed:
            max_level = max([programming_courses.get(c, 0) for c in prog_completed])
            prog_grades = [course_grades.get(c, 7.0) for c in prog_completed]
            avg_prog_grade = sum(prog_grades) / len(prog_grades)
            # Grade bonus: +0.5 if avg >= 8.5, +0.25 if avg >= 7.0
            grade_bonus = 0.5 if avg_prog_grade >= 8.5 else (0.25 if avg_prog_grade >= 7.0 else 0)
            programming_level = max_level + grade_bonus
        else:
            programming_level = 0
        
        # Infer computational thinking based on grades
        algorithm_courses = {
            'IT003': 1,  # Cấu trúc dữ liệu và giải thuật
            'CS112': 2,  # Phân tích và thiết kế thuật toán
            'MA006': 1   # Giải tích
        }
        
        algo_completed = [c for c in completed if c in algorithm_courses]
        if algo_completed:
            max_level = max([algorithm_courses.get(c, 0) for c in algo_completed])
            algo_grades = [course_grades.get(c, 7.0) for c in algo_completed]
            avg_algo_grade = sum(algo_grades) / len(algo_grades)
            grade_bonus = 0.5 if avg_algo_grade >= 8.5 else (0.25 if avg_algo_grade >= 7.0 else 0)
            computational_thinking = max_level + grade_bonus
        else:
            computational_thinking = 0
        
        # Calculate academic readiness based on IT and MA courses
        # IT courses: IT001, IT002, IT003, IT004, IT005, IT007, IT008, IT009, IT012, IT013, IT014
        # MA courses: MA003, MA004, MA005, MA006
        foundation_courses = ['IT001', 'IT002', 'IT003', 'IT004', 'IT005', 'IT007', 
                             'MA003', 'MA004', 'MA005', 'MA006']
        
        foundation_completed = [c for c in completed if c in foundation_courses]
        total_foundation = len(foundation_courses)
        num_completed = len(foundation_completed)
        
        if num_completed == 0:
            # No foundation courses completed
            academic_readiness = 0.5
        else:
            foundation_grades = [course_grades.get(c, 7.0) for c in foundation_completed]
            avg_grade = sum(foundation_grades) / len(foundation_grades)
            high_grade_count = sum(1 for g in foundation_grades if g >= 8.5)
            pass_count = sum(1 for g in foundation_grades if g < 7.0)
            
            completion_rate = num_completed / total_foundation
            
            # Determine academic readiness level
            if completion_rate >= 1.0 and high_grade_count / num_completed >= 0.5:
                # High: 100% completed, mostly >= 8.5
                academic_readiness = 3.0
            elif completion_rate >= 0.5 and avg_grade >= 7.0:
                # Medium: >= 50% completed, avg >= 7.0
                academic_readiness = 2.0
            elif num_completed >= 1:
                # Low: >= 1 completed, mostly pass
                academic_readiness = 1.0
            else:
                academic_readiness = 0.5
            
            # Fine-tune based on completion rate and grades
            if academic_readiness == 2.0:
                # Bonus for higher completion and grades
                academic_readiness += (completion_rate - 0.5) * 1.0  # Up to +0.5
                academic_readiness += (avg_grade - 7.0) / 3.0 * 0.5  # Up to +0.5 for grade 10
            elif academic_readiness == 1.0:
                academic_readiness += (num_completed / total_foundation) * 0.5  # Partial completion bonus
        
        # Year bonus (smaller than before since grades are factored in)
        year_bonus = (current_year - 1) * 0.2  # 0, 0.2, 0.4, 0.6 for years 1-4
        academic_readiness = min(academic_readiness + year_bonus, 4.0)  # Cap at 4.0
        
        return {
            'programming_level': programming_level,
            'computational_thinking': computational_thinking,
            'academic_readiness': round(academic_readiness, 2),
            'foundation_completion': f"{num_completed}/{total_foundation}",
            'foundation_avg_grade': round(sum(course_grades.get(c, 7.0) for c in foundation_completed) / max(len(foundation_completed), 1), 2) if foundation_completed else 0
        }
    
    def compute_interest_match(self, course: Dict, student_interests: List[str]) -> float:
        """
        Calculate interest match score
        
        Returns value between 0 and 1
        """
        if not student_interests:
            return 0.5  # Neutral score if no interests specified
        
        # Handle None knowledge_area (when JSON has null)
        knowledge_area = course.get('knowledge_area')
        course_areas = set(knowledge_area) if knowledge_area else set()
        student_areas = set(student_interests)
        
        if not course_areas:
            return 0.3  # Low score for courses without knowledge area
        
        intersection = course_areas.intersection(student_areas)
        
        if len(intersection) == 0:
            return 0.2  # Low but not zero for non-matching courses
        
        # Score based on proportion of student interests matched
        score = len(intersection) / len(student_areas)
        return min(score, 1.0)
    
    def compute_difficulty_fit(self, course_difficulty: float, 
                              student_readiness: float) -> float:
        """
        Calculate how well course difficulty matches student readiness
        
        Returns value between 0 and 1 (1 = perfect match)
        """
        max_difficulty = 15.0  # Approximate max difficulty score
        
        # Calculate normalized difference
        diff = abs(course_difficulty - student_readiness)
        
        # Convert to fit score (closer = better)
        fit = 1.0 - min(diff / max_difficulty, 1.0)
        
        # Apply penalty if too difficult
        if course_difficulty > student_readiness + 2:
            fit *= 0.7  # 30% penalty
        
        return fit
    
    def compute_time_fit(self, course: Dict, time_availability: str) -> float:
        """
        Calculate time availability fit
        
        Returns value between 0 and 1
        """
        credits = course.get('credits', 3)
        
        # Map time availability to preferred credit range
        time_map = {
            'Low': (1, 3),     # Prefer 1-3 credit courses
            'Medium': (3, 4),  # Prefer 3-4 credit courses
            'High': (4, 5)     # Can handle 4+ credit courses
        }
        
        min_pref, max_pref = time_map.get(time_availability, (3, 4))
        
        if min_pref <= credits <= max_pref:
            return 1.0  # Perfect match
        elif credits < min_pref:
            return 0.8  # Slightly less preferred
        else:  # credits > max_pref
            penalty = (credits - max_pref) * 0.15
            return max(0.3, 1.0 - penalty)
    
    def compute_recommendation_score(self, course: Dict, student_data: Dict,
                                    student_ability: Dict) -> Dict:
        """
        Compute overall recommendation score for a course
        
        Formula: score = α × interest_match + β × difficulty_fit + γ × time_fit
        
        Returns:
            Dictionary with score and component breakdowns
        """
        weights = self.rules['recommendation_weights']
        alpha = weights['alpha_interest']
        beta = weights['beta_difficulty']
        gamma = weights['gamma_time']
        
        # Calculate course difficulty
        difficulty = self.compute_difficulty_score(course)
        
        # Calculate component scores
        interest_score = self.compute_interest_match(
            course, 
            student_data.get('interests', [])
        )
        
        difficulty_score = self.compute_difficulty_fit(
            difficulty,
            student_ability['academic_readiness']
        )
        
        time_score = self.compute_time_fit(
            course,
            student_data.get('time_availability', 'Medium')
        )
        
        # Calculate weighted total
        total_score = (
            alpha * interest_score +
            beta * difficulty_score +
            gamma * time_score
        )
        
        return {
            'course_id': course['course_id'],
            'course_name': course['course_name'],
            'total_score': total_score,
            'interest_match': interest_score,
            'difficulty_fit': difficulty_score,
            'time_fit': time_score,
            'difficulty_score': difficulty,
            'credits': course['credits'],
            'knowledge_area': course['knowledge_area']
        }
    
    def rank_elective_courses(self, student_data: Dict, target_year: int,
                             target_semester: str) -> List[Dict]:
        """
        Rank all eligible elective courses for recommendation
        
        Returns:
            Sorted list of courses with recommendation scores
        """
        # Get eligible courses
        eligible = self.get_eligible_courses(student_data, target_year, target_semester)
        
        # Filter only elective courses
        electives = [c for c in eligible if c.get('course_group', '') in ['Tự chọn', 'Tự chọn tự do']]
        
        # Infer student abilities
        student_ability = self.infer_student_ability(student_data)
        
        # Score each course
        scored_courses = []
        for course in electives:
            score_data = self.compute_recommendation_score(course, student_data, student_ability)
            scored_courses.append(score_data)
        
        # Sort by total score (descending)
        scored_courses.sort(key=lambda x: x['total_score'], reverse=True)
        
        return scored_courses
    
    def get_curriculum_plan(self, major: str) -> Dict[str, List[Dict]]:
        """
        Get the full curriculum plan organized by year and semester
        
        Returns:
            Dictionary mapping semester keys to course lists
        """
        plan = {}
        
        for year in range(1, 5):
            for semester in ['HK1', 'HK2']:
                key = f"Year {year} - {semester}"
                
                # Get compulsory courses for this semester
                semester_courses = [
                    c for c in self.courses
                    if c['recommended_year'] == year
                    and c['recommended_semester'] == semester
                    and c.get('course_group', '') in ['Đại cương', 'Cơ sở ngành', 'Chuyên ngành']
                    and major in c['major']
                ]
                
                if semester_courses:
                    plan[key] = semester_courses
        
        return plan
    
    def has_electives_in_semester(self, major: str, year: int, semester: str) -> bool:
        """
        Check if there are elective courses available in the given semester
        """
        electives = [
            c for c in self.courses
            if c['recommended_year'] == year
            and c['recommended_semester'] == semester
            and c.get('course_group', '') in ['Tự chọn', 'Tự chọn tự do']
            and major in c['major']
        ]
        
        return len(electives) > 0
    
    def get_rule_description(self, rule_id: str) -> str:
        """Get description for a rule by ID from rules.json"""
        # Search in hard_rules
        for rule in self.rules.get('hard_rules', []):
            if rule.get('rule_id') == rule_id:
                return rule.get('description', 'Không có mô tả')
        
        # Search in soft_rules
        for rule in self.rules.get('soft_rules', []):
            if rule.get('rule_id') == rule_id:
                return rule.get('description', 'Không có mô tả')
        
        # Search in recommendation_rules
        for rule in self.rules.get('recommendation_rules', []):
            if rule.get('rule_id') == rule_id:
                return rule.get('description', 'Không có mô tả')
        
        # Search in inference_rules
        for rule in self.rules.get('inference_rules', []):
            if rule.get('rule_id') == rule_id:
                return rule.get('description', 'Không có mô tả')
        
        # Fallback for combined rule IDs like "I001-I003"
        if '-' in rule_id:
            return 'Suy diễn năng lực từ các môn đã hoàn thành'
        
        # Special case for TOP3
        if rule_id == 'TOP3':
            return 'Chỉ lấy 3 môn tự chọn có điểm cao nhất để gợi ý'
        
        return 'Không có mô tả'
    
    def get_all_rules_with_descriptions(self) -> List[Dict]:
        """Get all rules with their descriptions for display"""
        all_rules = []
        
        # Add hard rules
        for rule in self.rules.get('hard_rules', []):
            all_rules.append({
                'rule_id': rule.get('rule_id'),
                'rule_name': rule.get('rule_name'),
                'description': rule.get('description'),
                'category': 'Luật cứng (Hard Rules)',
                'priority': rule.get('priority', 1)
            })
        
        # Add soft rules
        for rule in self.rules.get('soft_rules', []):
            all_rules.append({
                'rule_id': rule.get('rule_id'),
                'rule_name': rule.get('rule_name'),
                'description': rule.get('description'),
                'category': 'Luật mềm (Soft Rules)',
                'priority': rule.get('priority', 2)
            })
        
        # Add recommendation rules
        for rule in self.rules.get('recommendation_rules', []):
            all_rules.append({
                'rule_id': rule.get('rule_id'),
                'rule_name': rule.get('rule_name'),
                'description': rule.get('description'),
                'category': 'Luật gợi ý (Recommendation Rules)',
                'priority': 3
            })
        
        # Add inference rules
        for rule in self.rules.get('inference_rules', []):
            all_rules.append({
                'rule_id': rule.get('rule_id'),
                'rule_name': rule.get('rule_name'),
                'description': rule.get('description'),
                'category': 'Luật suy diễn (Inference Rules)',
                'priority': 4
            })
        
        return all_rules
    
    def get_reasoning_trace(self, student_data: Dict, eligible_courses: List[Dict], 
                           scored_courses: List[Dict]) -> List[Dict]:
        """
        Generate detailed reasoning trace (thinking chain) for the recommendation process
        
        Returns:
            List of reasoning steps with rule applications
        """
        trace = []
        completed = student_data.get('completed_courses', [])
        current = student_data.get('current_courses', [])
        failed = student_data.get('failed_courses', [])
        major = student_data.get('major')
        cohort = student_data.get('cohort', 'K20')
        
        # Step 1: Prerequisites Check
        prereq_results = []
        for course in eligible_courses[:10]:  # Check first 10
            is_eligible, missing = self.check_prerequisites(course['course_id'], completed)
            if is_eligible:
                prereq_results.append(f"✅ {course['course_id']}: Đủ tiên quyết")
        trace.append({
            'step': 1,
            'rule_id': 'R001',
            'rule_name': 'Kiểm tra Tiên quyết',
            'description': self.get_rule_description('R001'),
            'result': prereq_results[:5],
            'summary': f'{len(eligible_courses)} môn đủ điều kiện tiên quyết'
        })
        
        # Step 2: Failed course alternative check (always show)
        slot_groups = self._get_elective_slot_groups(major, cohort)
        alt_check = []
        if failed:
            for course_id in failed:
                if course_id in slot_groups:
                    alts = [a for a in slot_groups[course_id] if a != course_id]
                    done_alts = [a for a in alts if a in completed or a in current]
                    if done_alts:
                        alt_check.append(f"⏭️ {course_id}: Bỏ qua (đã có {done_alts[0]})")
                    else:
                        alt_check.append(f"🔄 {course_id}: Cần học lại")
                else:
                    alt_check.append(f"🔄 {course_id}: Cần học lại")
        trace.append({
            'step': 2,
            'rule_id': 'F001',
            'rule_name': 'Kiểm tra Môn rớt có Thay thế',
            'description': self.get_rule_description('F001'),
            'result': alt_check if alt_check else ['✅ Không có môn rớt'],
            'summary': f'{len(failed)} môn rớt được kiểm tra' if failed else 'Không có môn rớt'
        })
        
        # Step 3: Teaching plan alignment
        trace.append({
            'step': 3,
            'rule_id': 'R008',
            'rule_name': 'Đối chiếu Kế hoạch Giảng dạy',
            'description': self.get_rule_description('R008'),
            'result': [f'Áp dụng KHGD: {major}_{cohort}'],
            'summary': f'Lọc môn theo kế hoạch giảng dạy {major}'
        })
        
        # Step 4: Ability inference
        ability = self.infer_student_ability(student_data)
        trace.append({
            'step': 4,
            'rule_id': 'I001-I003',
            'rule_name': 'Suy diễn Năng lực Sinh viên',
            'description': 'Suy diễn năng lực từ các môn đã hoàn thành',
            'result': [
                f'Programming Level: {ability["programming_level"]:.1f}/3 (I001)',
                f'Computational Thinking: {ability["computational_thinking"]:.1f}/3 (I002)',
                f'Academic Readiness: {ability["academic_readiness"]:.2f} (I003)'
            ],
            'summary': f'Readiness = {ability["academic_readiness"]:.2f}'
        })
        
        # Step 5: Scoring
        if scored_courses:
            score_examples = []
            for c in scored_courses[:3]:
                score_examples.append(
                    f"📊 {c['course_id']}: Score={c['total_score']:.2f} "
                    f"(I={c['interest_match']:.2f}, D={c['difficulty_fit']:.2f}, T={c['time_fit']:.2f})"
                )
            trace.append({
                'step': 5,
                'rule_id': 'S004',
                'rule_name': 'Tính điểm Gợi ý',
                'description': self.get_rule_description('S004'),
                'result': score_examples,
                'summary': f'Đã tính điểm {len(scored_courses)} môn tự chọn'
            })
        
        # Step 6: Top 3 selection
        trace.append({
            'step': 6,
            'rule_id': 'TOP3',
            'rule_name': 'Chọn Top 3 Môn Gợi ý',
            'description': 'Chỉ lấy 3 môn tự chọn có điểm cao nhất để gợi ý',
            'result': [f'🎯 {c["course_id"]}: {c["course_name"]} ({c["total_score"]:.2f})' 
                      for c in scored_courses[:3]] if scored_courses else ['Không có môn tự chọn'],
            'summary': f'Top 3 được chọn từ {len(scored_courses)} môn'
        })
        
        return trace
    
    def get_activated_rules(self, student_data: Dict, target_courses: List[str]) -> List[Dict]:
        """
        Get list of rules that are activated for given student and courses
        
        Returns:
            List of activated rule descriptions
        """
        activated = []
        completed = student_data.get('completed_courses', [])
        
        # Check prerequisite rules
        for course_id in target_courses:
            is_eligible, missing = self.check_prerequisites(course_id, completed)
            if not is_eligible:
                activated.append({
                    'rule_id': 'R001',
                    'rule_name': 'Prerequisite Check',
                    'description': self.get_rule_description('R001'),
                    'course': course_id,
                    'status': 'FAILED',
                    'message': f"Missing prerequisites: {', '.join(missing)}"
                })
        
        # Check special course rules
        year = student_data.get('current_year')
        semester = student_data.get('current_semester')
        
        for course_id in target_courses:
            if course_id.startswith('ENG'):
                activated.append({
                    'rule_id': 'R002',
                    'rule_name': 'English Course Year Constraint',
                    'description': self.get_rule_description('R002'),
                    'course': course_id,
                    'status': 'ACTIVE'
                })
            elif course_id.startswith('PE'):
                activated.append({
                    'rule_id': 'R004',
                    'rule_name': 'PE Semester Constraint',
                    'description': self.get_rule_description('R004'),
                    'course': course_id,
                    'status': 'ACTIVE'
                })
            elif course_id == 'ME001':
                activated.append({
                    'rule_id': 'R003',
                    'rule_name': 'Military Education Fixed Semester',
                    'description': self.get_rule_description('R003'),
                    'course': course_id,
                    'status': 'ACTIVE'
                })
        
        return activated
