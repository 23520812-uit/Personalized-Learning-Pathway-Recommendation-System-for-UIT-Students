"""
Course Recommendation System - Streamlit Application
Hệ thống Tư vấn Lộ trình Học tập Cá nhân hóa
ĐH CNTT - ĐHQG-HCM (UIT)
"""

import streamlit as st
import json
import networkx as nx  
from pyvis.network import Network  
import tempfile
import os
from reasoning_engine import ReasoningEngine


# Page configuration
st.set_page_config(
    page_title="Hệ thống Tư vấn Lộ trình Học tập - UIT",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS with Dark Mode Support
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Course card with dark mode support */
    .course-card {
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        border: 1px solid var(--border-color, #ddd);
        margin-bottom: 0.5rem;
        background-color: var(--card-bg, #f9f9f9);
        color: var(--text-color, #333);
    }
    
    /* Dark mode variables */
    @media (prefers-color-scheme: dark) {
        .course-card {
            --card-bg: #2d2d2d;
            --border-color: #444;
            --text-color: #e0e0e0;
        }
    }
    
    /* Streamlit dark mode detection */
    [data-theme="dark"] .course-card,
    .stApp[data-theme="dark"] .course-card {
        background-color: #2d2d2d;
        border-color: #444;
        color: #e0e0e0;
    }
    
    .compulsory-course {
        border-left: 4px solid #2ecc71;
    }
    .elective-course {
        border-left: 4px solid #f39c12;
    }
    .recommended-course {
        border-left: 4px solid #3498db;
    }
    
    .score-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.85rem;
        font-weight: bold;
    }
    .score-high {
        background-color: #d4edda;
        color: #155724;
    }
    .score-medium {
        background-color: #fff3cd;
        color: #856404;
    }
    .score-low {
        background-color: #f8d7da;
        color: #721c24;
    }
    
    /* Table styling */
    .semester-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1rem;
    }
    .semester-table th, .semester-table td {
        padding: 0.5rem;
        text-align: left;
        border-bottom: 1px solid var(--border-color, #ddd);
    }
    .semester-table th {
        background-color: var(--header-bg, #f0f0f0);
        font-weight: bold;
    }
    
    @media (prefers-color-scheme: dark) {
        .semester-table th {
            --header-bg: #3d3d3d;
        }
        .semester-table th, .semester-table td {
            --border-color: #444;
        }
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_reasoning_engine():
    """Load and cache reasoning engine"""
    return ReasoningEngine()

def display_header():
    """Display application header"""
    st.markdown('<div class="main-header">🎓 Hệ thống Tư vấn Lộ trình Học tập</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">ĐH Công nghệ Thông tin - ĐHQG-HCM (UIT)</div>', 
                unsafe_allow_html=True)
    st.markdown("---")


def create_prerequisite_graph(courses_dict, student_completed=None, student_current=None):
    """Create prerequisite relationship graph"""
    G = nx.DiGraph()
    
    # Add nodes
    for course_id, course in courses_dict.items():
        label = f"{course_id}\n{course['course_name'][:15]}..."
        
        # Color based on completion status
        if student_completed and course_id in student_completed:
            color = "#4CAF50"  # Green for completed
            size = 30
        elif student_current and course_id in student_current:
            color = "#FF9800"  # Orange for currently taking
            size = 35
        else:
            color = "#2196F3"  # Blue for not completed
            size = 25
        
        G.add_node(course_id, label=label, color=color, title=course['course_name'], size=size)
    
    # Add edges (prerequisites)
    for course_id, course in courses_dict.items():
        for prereq in course.get('prerequisites', []):
            if prereq in courses_dict:
                G.add_edge(prereq, course_id)
    
    return G


def visualize_graph(G, height="800px"):
    """Visualize graph using pyvis with improved settings"""
    net = Network(height=height, width="100%", directed=True, 
                  bgcolor="#ffffff", font_color="black")
    net.from_nx(G)
    
    # Configure physics for better layout
    net.set_options("""
    {
      "nodes": {
        "font": {
          "size": 14,
          "face": "arial"
        },
        "scaling": {
          "min": 20,
          "max": 40
        }
      },
      "edges": {
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 1.2
          }
        },
        "color": {
          "color": "#666666",
          "highlight": "#000000"
        },
        "smooth": {
          "type": "curvedCW",
          "roundness": 0.2
        }
      },
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -50000,
          "centralGravity": 0.5,
          "springLength": 250,
          "springConstant": 0.02,
          "damping": 0.5
        },
        "maxVelocity": 50,
        "minVelocity": 0.1
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 100,
        "zoomView": true,
        "dragView": true
      }
    }
    """)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as f:
        net.save_graph(f.name)
        return f.name


def display_student_input_form():
    """Display form for student information input with real-time updates"""
    st.sidebar.header("Thông tin Sinh viên")
    
    engine = load_reasoning_engine()
    
    # Initialize session state for form values (outside form for reactivity)
    if 'form_major' not in st.session_state:
        st.session_state.form_major = "KHMT"
    if 'form_enrollment_year' not in st.session_state:
        st.session_state.form_enrollment_year = 2025
    if 'form_semester' not in st.session_state:
        st.session_state.form_semester = 3
    if 'completed_courses_state' not in st.session_state:
        st.session_state.completed_courses_state = []
    if 'current_courses_state' not in st.session_state:
        st.session_state.current_courses_state = []
    if 'failed_courses_state' not in st.session_state:
        st.session_state.failed_courses_state = []
    if 'course_grades' not in st.session_state:
        st.session_state.course_grades = {}  # Store grades for each completed course
    
    # Major and enrollment year OUTSIDE form for real-time updates
    major = st.sidebar.selectbox(
        "Ngành học",
        options=["KHMT", "TTNT"],
        index=0 if st.session_state.form_major == "KHMT" else 1,
        help="Khoa học Máy tính (KHMT) hoặc Trí tuệ Nhân tạo (TTNT)",
        key="major_select"
    )
    st.session_state.form_major = major
    
    enrollment_year = st.sidebar.selectbox(
        "Năm nhập học",
        options=[2023, 2024, 2025],
        index=[2023, 2024, 2025].index(st.session_state.form_enrollment_year),
        help="Năm bạn nhập học vào UIT",
        key="enrollment_year_select"
    )
    st.session_state.form_enrollment_year = enrollment_year
    
    # Determine cohort and display curriculum info (updates in real-time)
    cohort = engine.determine_cohort(enrollment_year)
    curriculum_key = engine.get_curriculum_for_cohort(cohort, major)
    
    major_name = "Khoa học Máy tính" if major == "KHMT" else "Trí tuệ Nhân tạo"
    cohort_info = engine.teaching_plans['cohort_mappings'][cohort]
    st.sidebar.success(f"**Cử nhân ngành {major_name}** ({cohort_info['description']})")
    
    # Semester selection BEFORE course selections
    col1, col2 = st.sidebar.columns(2)
    with col1:
        current_semester_number = st.selectbox(
            "Học kỳ hiện tại", 
            options=[1, 2, 3, 4, 5, 6, 7], 
            index=st.session_state.form_semester - 1,
            help="Bạn đang ở học kỳ thứ mấy (1-7)",
            key="semester_select"
        )
        st.session_state.form_semester = current_semester_number
    with col2:
        academic_year = (current_semester_number + 1) // 2
        st.metric("Năm học", f"Năm {academic_year}")
    
    # Build course list based on selected major (updates when major changes)
    # Sort by course_group first, then by course_id
    group_order = ['Đại cương', 'Cơ sở ngành', 'Chuyên ngành', 'Tự chọn', 'Tự chọn tự do', 'Tốt nghiệp']
    sorted_courses = sorted(
        [c for c in engine.courses if major in c['major']],
        key=lambda x: (group_order.index(x.get('course_group', 'Tự chọn')) if x.get('course_group') in group_order else 99, x['course_id'])
    )
    all_available_courses = [
        f"{c['course_id']} - {c['course_name']}" 
        for c in sorted_courses
    ]
    
    # Course selection OUTSIDE form for real-time filtering
    st.sidebar.subheader("Môn đã học")
    studied_courses = st.sidebar.multiselect(
        "Chọn các môn đã học",
        options=all_available_courses,
        default=[c for c in st.session_state.completed_courses_state if c in all_available_courses],
        help="Chọn tất cả môn học bạn đã từng học (bao gồm cả đậu và rớt)",
        key="completed_courses_select"
    )
    st.session_state.completed_courses_state = studied_courses
    
    # Grade input for studied courses (exclude PE, ME courses - they don't have grades)
    gradeable_courses = [c for c in studied_courses if not c.startswith("PE") and not c.startswith("ME")]
    if gradeable_courses:
        with st.sidebar.expander("Nhập điểm môn học", expanded=True):
            st.caption("Nhập điểm (0-10). Môn < 5 điểm sẽ tự động phân loại là rớt.")
            for course in gradeable_courses:
                course_id = course.split(" - ")[0]
                default_grade = st.session_state.course_grades.get(course_id, 7.0)
                grade = st.number_input(
                    course,
                    min_value=0.0,
                    max_value=10.0,
                    value=default_grade,
                    step=0.1,
                    key=f"grade_{course_id}",
                    help="Điểm từ 0.0 đến 10.0 (< 5.0 = Rớt)"
                )
                st.session_state.course_grades[course_id] = grade
        
        # Show failed courses summary
        failed_from_grades = [c for c in gradeable_courses 
                            if st.session_state.course_grades.get(c.split(" - ")[0], 7.0) < 5.0]
        if failed_from_grades:
            st.sidebar.warning(f"⚠️ Môn rớt ({len(failed_from_grades)}): " + 
                             ", ".join([c.split(" - ")[0] for c in failed_from_grades]))
    
    # Filter out studied courses from current courses options (real-time)
    remaining_for_current = [c for c in all_available_courses if c not in studied_courses]
    
    st.sidebar.subheader("Môn đang học")
    current_courses = st.sidebar.multiselect(
        "Chọn các môn đang học",
        options=remaining_for_current,
        default=[c for c in st.session_state.current_courses_state if c in remaining_for_current],
        help="Các môn bạn đang đăng ký học kỳ này",
        key="current_courses_select"
    )
    st.session_state.current_courses_state = current_courses
    
    # Now the rest in a form
    with st.sidebar.form("student_form"):
        st.subheader("Sở thích học tập")
        interests = st.multiselect(
            "Lĩnh vực quan tâm",
            options=["AI", "ML", "NLP", "CV", "Multimedia", "Database", 
                    "Network", "SE", "Algorithm", "KE", "DataScience", "IS", "Embedded"],
            default=["AI", "ML"],
            help="KE = Knowledge Engineering, IS = Information Systems, DataScience = Khoa học dữ liệu"
        )
        
        time_availability = st.select_slider(
            "Thời gian dành cho học tập",
            options=["Low", "Medium", "High"],
            value="Medium",
            help="Low: Ít thời gian, Medium: Trung bình, High: Nhiều thời gian"
        )
        
        submitted = st.form_submit_button("Phân tích & Gợi ý", use_container_width=True)
    
    if submitted:
        studied_ids = [c.split(" - ")[0] for c in studied_courses]
        current_ids = [c.split(" - ")[0] for c in current_courses]
        
        # Build course_grades dict (exclude PE, ME - they don't have grades)
        course_grades = {cid: st.session_state.course_grades.get(cid, 7.0) 
                        for cid in studied_ids 
                        if not cid.startswith("PE") and not cid.startswith("ME")}
        
        # Auto-classify: completed (>= 5.0) vs failed (< 5.0)
        completed_ids = [cid for cid in studied_ids 
                        if cid.startswith("PE") or cid.startswith("ME") or course_grades.get(cid, 7.0) >= 5.0]
        failed_ids = [cid for cid in studied_ids 
                     if not cid.startswith("PE") and not cid.startswith("ME") and course_grades.get(cid, 7.0) < 5.0]
        
        return {
            "major": major,
            "cohort": cohort,
            "enrollment_year": enrollment_year,
            "current_semester_number": current_semester_number,
            "current_year": academic_year,
            "current_semester": "HK1" if current_semester_number % 2 == 1 else "HK2",
            "studied_courses": studied_ids,  # All studied courses
            "completed_courses": completed_ids,  # Passed courses (>= 5.0)
            "current_courses": current_ids,
            "failed_courses": failed_ids,  # Failed courses (< 5.0)
            "course_grades": course_grades,
            "interests": interests,
            "time_availability": time_availability
        }
    
    return None


def display_curriculum_plan(engine, major, student_data):
    """Display future study roadmap with recommendations integrated"""
    st.header("Lộ trình Học tập")
    
    cohort = student_data.get('cohort', 'K20')
    current_semester = student_data.get('current_semester_number', 1)
    completed = set(student_data.get('completed_courses', []))
    current_courses = set(student_data.get('current_courses', []))
    
    # Display graduation progress
    st.subheader("Tiến độ Tốt nghiệp")
    progress = engine.calculate_graduation_progress(student_data)
    
    # Calculate credits from current courses
    current_credits = 0
    for course_id in current_courses:
        if course_id in engine.courses_dict:
            current_credits += engine.courses_dict[course_id].get('credits', 0)
    
    projected_total = progress['total_completed'] + current_credits
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.metric(
            "Tổng tín chỉ (đã hoàn thành)",
            f"{progress['total_completed']} / {progress['total_required']} TC",
            f"{progress['total_completed'] / progress['total_required'] * 100:.1f}%"
        )
    with col2:
        remaining = progress['total_required'] - progress['total_completed']
        st.metric("Còn lại", f"{remaining} TC")
    with col3:
        st.metric("Đang học", f"+{current_credits} TC")
    
    # Progress bar showing current + projected
    st.caption("**Tiến độ dự kiến sau kỳ này:**")
    projected_pct = min(projected_total / progress['total_required'], 1.0)
    completed_pct = progress['total_completed'] / progress['total_required']
    st.progress(projected_pct)
    st.caption(f"Dự kiến: {projected_total}/{progress['total_required']} TC ({projected_pct*100:.1f}%) sau khi hoàn thành {len(current_courses)} môn đang học")
    
    # Category progress
    st.write("**Chi tiết theo danh mục:**")
    cols = st.columns(len(progress['categories']))
    for idx, (category, data) in enumerate(progress['categories'].items()):
        with cols[idx]:
            completed_cat = data.get('completed', 0)
            required_cat = data.get('required', 0)
            category_name = {
                'dai_cuong': 'Đại cương',
                'co_so_nganh': 'Cơ sở ngành',
                'chuyen_nganh': 'Chuyên ngành',
                'tu_chon_tu_do': 'Tự chọn',
                'tot_nghiep': 'Tốt nghiệp'
            }.get(category, category)
            
            progress_pct = (completed_cat / required_cat * 100) if required_cat > 0 else 0
            st.metric(category_name, f"{completed_cat}/{required_cat} TC")
            st.progress(min(progress_pct / 100, 1.0))
    
    st.markdown("---")
    
    # Display failed courses that need retake
    failed_courses = student_data.get('failed_courses', [])
    if failed_courses:
        st.subheader("Môn cần học lại")
        import pandas as pd
        retake_info = []
        for course_id in failed_courses:
            course_info = engine.courses_dict.get(course_id)
            if course_info:
                next_retake = engine.get_next_retake_semester(
                    course_id, 
                    current_semester,
                    major, cohort
                )
                grade = student_data.get('course_grades', {}).get(course_id, 'N/A')
                retake_info.append({
                    'Mã môn': course_id,
                    'Tên môn': course_info['course_name'],
                    'TC': course_info['credits'],
                    'Điểm': f"{grade:.1f}" if isinstance(grade, (int, float)) else grade,
                    'Kỳ đăng ký lại': f"HK{next_retake}",
                    'Ghi chú': 'Học lại' + (' - Tiên quyết cho môn khác' if engine._is_prerequisite_for_others(course_id) else '')
                })
        if retake_info:
            df_failed = pd.DataFrame(retake_info)
            st.dataframe(df_failed, use_container_width=True, hide_index=True)
        st.markdown("---")
    
    st.subheader("Gợi ý Học tập Từ Kỳ Hiện tại")
    
    # Get max credits per semester rule (hard_rules is a list, find R005)
    max_credits_per_semester = 24  # Default
    for rule in engine.rules.get('hard_rules', []):
        if rule.get('rule_id') == 'R005':
            max_credits_per_semester = rule.get('max_credits', 24)
            break
    st.caption(f"**Quy tắc:** Tối đa {max_credits_per_semester} tín chỉ/học kỳ theo kế hoạch giảng dạy")
    
    # Display current semester and future semesters only
    for semester_num in range(current_semester, 8):
        semester_data = engine.get_semester_courses(major, semester_num, cohort)
        
        is_current = (semester_num == current_semester)
        
        # Filter out completed courses
        compulsory = [c for c in semester_data.get('compulsory', []) 
                     if c.get('course_id') is None or c.get('course_id') not in completed]
        elective = [c for c in semester_data.get('elective', []) 
                   if c.get('course_id') is None or c.get('course_id') not in completed]
        
        # Always show semesters (even if no specific courses, show placeholders)
        # Only skip if past semester with all courses completed
        # Never skip future semesters
        
        # Get elective slots if available
        elective_slots = semester_data.get('elective_slots', [])
        
        # Calculate remaining credits for this semester
        planned_credits = sum(c['credits'] for c in compulsory) + sum(c['credits'] for c in elective)
        
        # Semester header with status - Use markdown header instead of expander
        if is_current:
            st.markdown(f"### Học kỳ {semester_num} *(Hiện tại)*")
        else:
            st.markdown(f"### Học kỳ {semester_num} *(Dự kiến)* — {planned_credits} TC")
        
        import pandas as pd
        all_semester_courses = []
        
        # For CURRENT semester: Only show courses being taken, no teaching plan
        if is_current:
            if current_courses:
                for course_id in current_courses:
                    course_info = engine.courses_dict.get(course_id)
                    if course_info:
                        grade = student_data.get('course_grades', {}).get(course_id)
                        all_semester_courses.append({
                            'status': 'Đang học',
                            'id': course_id,
                            'name': course_info['course_name'],
                            'credits': course_info['credits'],
                            'type': 'Đăng ký',
                            'choices': None
                        })
                
                if all_semester_courses:
                    total_credits = sum(c['credits'] for c in all_semester_courses)
                    df = pd.DataFrame([{k: v for k, v in c.items() if k != 'choices'} for c in all_semester_courses])
                    df.columns = ['Trạng thái', 'Mã môn', 'Tên môn', 'TC', 'Loại']
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.caption(f"Tổng: {total_credits} TC đang học")
                else:
                    st.info("Chưa chọn môn đang học cho học kỳ này")
            else:
                st.info("Chưa chọn môn đang học cho học kỳ này")
            
            st.markdown("---")
            continue  # Skip to next semester - recommendations will be shown separately
        
        # For FUTURE semesters: Show teaching plan
        # Add compulsory courses from teaching plan
        for course in compulsory:
            course_id = course.get('course_id')
            # Skip if already completed
            if course_id and course_id in completed:
                continue
            
            # Handle placeholder courses (including courses with '-' as id)
            if course.get('is_placeholder'):
                display_id = course_id if course_id == '-' else '(Chọn môn)'
                all_semester_courses.append({
                    'status': 'Kế hoạch',
                    'id': display_id,
                    'name': course['course_name'],
                    'credits': course['credits'],
                    'type': 'Bắt buộc',
                    'choices': None
                })
            else:
                all_semester_courses.append({
                    'status': 'Kế hoạch',
                    'id': course_id if course_id else '',
                    'name': course['course_name'],
                    'credits': course['credits'],
                    'type': 'Bắt buộc',
                    'choices': None
                })
        
        # Add elective courses from teaching plan
        for course in elective:
            course_id = course.get('course_id')
            if course_id and course_id in completed:
                continue
            
            # Handle elective slot with choices
            if course.get('is_elective_slot'):
                slot_name = course.get('slot_name', 'Môn tự chọn')
                choices_ids = course.get('all_choices', [])
                choices_str = ', '.join(choices_ids[:5])  # Show first 5
                if len(choices_ids) > 5:
                    choices_str += f'... (+{len(choices_ids)-5} môn)'
                all_semester_courses.append({
                    'status': 'Kế hoạch',
                    'id': f'[{len(choices_ids)} môn]',
                    'name': slot_name,
                    'credits': course['credits'],
                    'type': 'Tự chọn',
                    'choices': choices_str
                })
            # Handle old placeholder courses
            elif course.get('is_placeholder'):
                all_semester_courses.append({
                    'status': 'Kế hoạch',
                    'id': '(Chọn môn)',
                    'name': course['course_name'],
                    'credits': course['credits'],
                    'type': 'Tự chọn',
                    'choices': None
                })
            else:
                all_semester_courses.append({
                    'status': 'Kế hoạch',
                    'id': course_id,
                    'name': course['course_name'],
                    'credits': course['credits'],
                    'type': 'Tự chọn',
                    'choices': None
                })
        
        if all_semester_courses:
            # Calculate total credits
            total_credits = sum(c['credits'] for c in all_semester_courses)
            
            # Check if this is semester 7 with graduation options
            if semester_num == 7:
                # Count graduation options - each 10TC course is 1 option
                # Special case: 6TC + 4TC courses together form 1 option
                grad_10tc = [c for c in all_semester_courses if c['credits'] == 10]
                grad_6tc = [c for c in all_semester_courses if c['credits'] == 6]
                grad_4tc = [c for c in all_semester_courses if c['credits'] == 4]
                
                num_options = len(grad_10tc)
                # If there's a 6TC + 4TC pair, count as 1 additional option
                if grad_6tc and grad_4tc:
                    num_options += 1
                
                if num_options >= 2:
                    st.info(f"Chọn 1/{num_options} phương án tốt nghiệp (10 TC)")
            elif total_credits > max_credits_per_semester:
                st.warning(f"Tổng tín chỉ ({total_credits} TC) vượt quá quy định ({max_credits_per_semester} TC)")
            
            # Create DataFrame - show choices column only if there are elective slots
            has_choices = any(c['choices'] for c in all_semester_courses)
            if has_choices:
                df = pd.DataFrame(all_semester_courses)
                df.columns = ['Trạng thái', 'Mã môn', 'Tên môn', 'TC', 'Loại', 'Các môn có thể chọn']
                # Replace None with empty string
                df['Các môn có thể chọn'] = df['Các môn có thể chọn'].fillna('')
            else:
                df = pd.DataFrame([{k: v for k, v in c.items() if k != 'choices'} for c in all_semester_courses])
                df.columns = ['Trạng thái', 'Mã môn', 'Tên môn', 'TC', 'Loại']
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.caption(f"Tổng: {total_credits} TC")
            
            # Show expandable elective slot details - MERGED similar slots
            if elective_slots:
                # Group slots by similar names (chuyên ngành 1,2 / tự do 1,2)
                import re
                merged_slots = {}
                for slot in elective_slots:
                    # Extract base name (remove numbers like "1", "2")
                    base_name = re.sub(r'\s*\d+\s*$', '', slot['slot_name']).strip()
                    base_name = re.sub(r'\(chọn \d+\)', '', base_name).strip()
                    
                    if base_name not in merged_slots:
                        merged_slots[base_name] = {
                            'credits': slot['credits'],
                            'choices': [],
                            'slot_count': 0
                        }
                    merged_slots[base_name]['slot_count'] += 1
                    # Add unique choices
                    for choice in slot['choices']:
                        if choice['course_id'] not in [c['course_id'] for c in merged_slots[base_name]['choices']]:
                            merged_slots[base_name]['choices'].append(choice)
                
                with st.expander("Chi tiết các môn tự chọn có thể đăng ký", expanded=False):
                    for base_name, data in merged_slots.items():
                        slot_label = f"{base_name}"
                        if data['slot_count'] > 1:
                            slot_label += f" (cần chọn {data['slot_count']} môn)"
                        st.markdown(f"**{slot_label}** ({data['credits']} TC/môn):")
                        
                        # Sort choices by knowledge_area for better grouping
                        sorted_choices = sorted(data['choices'], 
                            key=lambda x: (x.get('knowledge_area') or ['ZZZ'])[0])
                        
                        choices_df = pd.DataFrame([{
                            'Mã': c['course_id'],
                            'Tên môn': c['course_name'],
                            'TC': c['credits'],
                            'Lĩnh vực': ', '.join(c.get('knowledge_area') or ['-'])
                        } for c in sorted_choices])
                        st.dataframe(choices_df, use_container_width=True, hide_index=True, height=200)
                
                # Add recommendation based on interests - PER SLOT TYPE - only for next semester
                if semester_num == current_semester + 1:
                    with st.expander("Gợi ý môn tự chọn theo sở thích", expanded=True):
                        st.caption(f"Dựa trên sở thích: {', '.join(student_data.get('interests', []))}")
                        
                        student_ability = engine.infer_student_ability(student_data)
                        
                        def get_label(score):
                            if score >= 0.7: return "Rất phù hợp"
                            elif score > 0.5: return "Phù hợp"
                            else: return "Cân nhắc"
                        
                        # Score and recommend for EACH slot type separately
                        for base_name, data in merged_slots.items():
                            slot_label = f"**{base_name}**"
                            slot_label += f" (chọn {data['slot_count']} trong {len(data['choices'])} môn)"
                            
                            st.markdown(slot_label)
                            
                            # Score courses in THIS slot
                            scored = []
                            for course in data['choices']:
                                score_data = engine.compute_recommendation_score(course, student_data, student_ability)
                                scored.append(score_data)
                            
                            scored.sort(key=lambda x: x['total_score'], reverse=True)
                            
                            # Show top N based on how many need to be chosen (at least 5)
                            top_n = min(max(data['slot_count'] + 3, 5), len(scored))
                            top_courses = scored[:top_n]
                            
                            if top_courses:
                                rec_df = pd.DataFrame([{
                                    'Mã': c['course_id'],
                                    'Tên môn': c['course_name'],
                                    'TC': c['credits'],
                                    'Điểm': f"{c['total_score']:.2f}",
                                    'Đánh giá': get_label(c['total_score']),
                                    'Lĩnh vực': ', '.join(c.get('knowledge_area') or ['-'])
                                } for c in top_courses])
                                st.dataframe(rec_df, use_container_width=True, hide_index=True)
                            
                            st.markdown("---")
        else:
            st.info("Đã hoàn thành tất cả môn học theo kế hoạch cho học kỳ này")
        
        st.markdown("---")  # Separator between semesters


def display_reasoning_trace(engine, student_data):
    """Display reasoning trace for course recommendations"""
    st.header("Luồng Suy luận")
    
    cohort = student_data.get('cohort', 'K20')
    current_semester = student_data.get('current_semester_number', 1)
    next_semester = min(current_semester + 1, 7)
    major = student_data['major']
    failed_courses = student_data.get('failed_courses', [])
    
    st.caption(f"Các bước suy luận của hệ thống để đưa ra gợi ý môn học cho **HK{next_semester}**")
    
    # Get eligible courses for reasoning
    eligible = engine.get_eligible_courses(student_data)
    
    # Score elective courses for reasoning trace
    student_ability = engine.infer_student_ability(student_data)
    semester_plan = engine.get_semester_courses(major, next_semester, cohort)
    planned_compulsory_ids = [c['course_id'] for c in semester_plan.get('compulsory', [])]
    
    other_eligible = [c for c in eligible 
                     if not c.get('is_failed') 
                     and c['course_id'] not in planned_compulsory_ids]
    
    scored_electives = []
    for course in other_eligible:
        score_data = engine.compute_recommendation_score(course, student_data, student_ability)
        scored_electives.append(score_data)
    scored_electives.sort(key=lambda x: x['total_score'], reverse=True)
    
    # Get detailed reasoning trace from engine
    reasoning_trace = engine.get_reasoning_trace(student_data, eligible, scored_electives)
    
    # Display reasoning trace with rule descriptions
    for trace_step in reasoning_trace:
        with st.container():
            step_num = trace_step['step']
            rule_id = trace_step['rule_id']
            rule_name = trace_step['rule_name']
            description = trace_step['description']
            
            st.markdown(f"#### Bước {step_num}: {rule_name}")
            st.info(f"📜 **Luật {rule_id}:** {description}")
            
            if trace_step['result']:
                for item in trace_step['result']:
                    st.markdown(f"- {item}")
            
            st.caption(f"=> {trace_step['summary']}")
            st.markdown("---")
    
    # Additional context analysis
    with st.expander("Chi tiết Ngữ cảnh Sinh viên", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
**Thông tin cơ bản:**
- Ngành: {major}
- Năm: {student_data['current_year']}
- Học kỳ hiện tại: HK{current_semester}
- Khóa: {cohort}
""")
        with col2:
            st.markdown(f"""
**Tiến độ học tập:**
- Đã hoàn thành: {len(student_data.get('completed_courses', []))} môn
- Đang học: {len(student_data.get('current_courses', []))} môn
- Đã rớt: {len(failed_courses)} môn
""")
        
        st.markdown(f"""
**Sở thích:** {', '.join(student_data.get('interests', [])) or 'Chưa chọn'}  
**Thời gian học:** {student_data.get('time_availability', 'Medium')}
""")
    
    # Show scoring details with formula
    weights = engine.rules.get('recommendation_weights', {})
    top_3_for_display = scored_electives[:3] if scored_electives else []
    
    with st.expander("Công thức Tính điểm Chi tiết", expanded=False):
        st.latex(r"Score = \alpha \times Interest + \beta \times Difficulty + \gamma \times Time")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("α (Interest)", weights.get('alpha_interest', 0.55))
        with col2:
            st.metric("β (Difficulty)", weights.get('beta_difficulty', 0.25))
        with col3:
            st.metric("γ (Time)", weights.get('gamma_time', 0.20))
        
        if top_3_for_display:
            st.markdown("**Điểm chi tiết Top 3:**")
            for i, c in enumerate(top_3_for_display, 1):
                st.markdown(f"""
**{i}. {c['course_id']} - {c['course_name']}**
- Interest: {c['interest_match']:.3f} × {weights.get('alpha_interest', 0.55)} = {c['interest_match'] * weights.get('alpha_interest', 0.55):.3f}
- Difficulty: {c['difficulty_fit']:.3f} × {weights.get('beta_difficulty', 0.25)} = {c['difficulty_fit'] * weights.get('beta_difficulty', 0.25):.3f}
- Time: {c['time_fit']:.3f} × {weights.get('gamma_time', 0.20)} = {c['time_fit'] * weights.get('gamma_time', 0.20):.3f}
- **Total: {c['total_score']:.3f}**
""")


def display_knowledge_view(engine, student_data):
    """Display knowledge representation"""
    st.header("Biểu diễn Tri thức")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Môn học", "Sinh viên", "Luật", "Năng lực Suy diễn"
    ])
    
    with tab1:
        st.subheader("Knowledge Base - Courses")
        
        # Filter courses by major
        major = student_data.get('major')
        major_courses = [c for c in engine.courses if major in c['major']]
        
        st.info(f"Tổng số môn học cho ngành {major}: {len(major_courses)}")
        
        # Sample courses
        st.json(major_courses[:3])
        
        with st.expander("Xem toàn bộ dữ liệu môn học"):
            st.json(major_courses)
    
    with tab2:
        st.subheader("Student Profile (Input)")
        st.json(student_data)
        
        st.subheader("Inferred Attributes")
        ability = engine.infer_student_ability(student_data)
        st.json(ability)
    
    with tab3:
        st.subheader("Rules Base")
        st.json(engine.rules)
        
        st.subheader("Activated Rules")
        year = student_data['current_year']
        semester = student_data['current_semester']
        eligible = engine.get_eligible_courses(student_data, year, semester)
        eligible_ids = [c['course_id'] for c in eligible[:10]]
        
        activated = engine.get_activated_rules(student_data, eligible_ids)
        if activated:
            st.json(activated)
        else:
            st.info("Không có luật đặc biệt nào được kích hoạt")
    
    with tab4:
        st.subheader("Student Ability Inference")
        
        ability = engine.infer_student_ability(student_data)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Programming Level", f"{ability['programming_level']:.1f}/3.5")
        with col2:
            st.metric("Computational Thinking", f"{ability['computational_thinking']:.1f}/2.5")
        with col3:
            st.metric("Academic Readiness", f"{ability['academic_readiness']:.1f}/4")
        
        # Additional grade-based info
        col4, col5 = st.columns(2)
        with col4:
            st.metric("Foundation Completion", ability.get('foundation_completion', 'N/A'))
        with col5:
            st.metric("Foundation Avg Grade", f"{ability.get('foundation_avg_grade', 0):.1f}/10")
        
        st.markdown("""
        **Quy tắc suy diễn (dựa trên điểm):**
        - **Programming Level**: IT001 (1), IT002 (2), CS116 (3) + bonus điểm
        - **Computational Thinking**: IT003 (1), CS112 (2), MA006 (1) + bonus điểm
        - **Academic Readiness**: Dựa trên các môn nền tảng (IT, MA):
          - **Low (1.0)**: Hoàn thành ≥ 1 môn, đa số Pass (< 7.0)
          - **Medium (2.0)**: Hoàn thành ≥ 50% môn, TB ≥ 7.0
          - **High (3.0)**: Hoàn thành 100% môn, đa số ≥ 8.5
        """)


def display_prerequisite_graph(engine, student_data):
    """Display prerequisite relationship graph with legend"""
    st.header("Đồ thị Quan hệ Tiên quyết")
    
    # Legend and explanation
    st.markdown("""
    **Giải thích đồ thị:**
    - Mỗi **nút (node)** đại diện cho một môn học
    - **Mũi tên** chỉ hướng từ môn tiên quyết đến môn yêu cầu (A -> B nghĩa là A là tiên quyết của B)
    - Kéo thả các nút để xem rõ hơn quan hệ giữa các môn
    - Cuộn chuột để phóng to/thu nhỏ
    """)
    
    # Color legend
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Xanh lá**: Đã hoàn thành")
    with col2:
        st.markdown("**Cam**: Đang học")
    with col3:
        st.markdown("**Xanh dương**: Chưa học")
    
    st.markdown("---")
    
    # Filter courses - use course_group instead of course_role
    major = student_data['major']
    compulsory_groups = ['Đại cương', 'Cơ sở ngành', 'Chuyên ngành']
    major_courses = {
        c['course_id']: c 
        for c in engine.courses 
        if major in c['major'] and c.get('course_group') in compulsory_groups
    }
    
    # Add some electives for demonstration
    elective_groups = ['Tự chọn', 'Tự chọn tự do']
    electives = [c for c in engine.courses 
                if major in c['major'] and c.get('course_group') in elective_groups]
    for course in electives[:10]:
        major_courses[course['course_id']] = course
    
    completed = student_data.get('completed_courses', [])
    current = student_data.get('current_courses', [])
    
    st.info(f"Hiển thị {len(major_courses)} môn học cho ngành {major}")
    
    # Create and visualize graph
    with st.spinner("Đang tạo đồ thị..."):
        G = create_prerequisite_graph(major_courses, completed, current)
        html_file = visualize_graph(G, height="900px")
    
    # Display graph
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    st.components.v1.html(html_content, height=950)
    
    # Statistics
    with st.expander("Thống kê đồ thị", expanded=False):
        st.write(f"- Tổng số môn học: {G.number_of_nodes()}")
        st.write(f"- Tổng số quan hệ tiên quyết: {G.number_of_edges()}")
        
        # Find courses with most prerequisites
        prereq_counts = [(node, G.in_degree(node)) for node in G.nodes()]
        prereq_counts.sort(key=lambda x: x[1], reverse=True)
        
        st.write("**Môn có nhiều tiên quyết nhất:**")
        for course_id, count in prereq_counts[:5]:
            if count > 0:
                course_name = major_courses[course_id]['course_name']
                st.write(f"  - {course_id}: {course_name} ({count} tiên quyết)")
    
    # Cleanup
    os.unlink(html_file)


def main():
    """Main application"""
    display_header()
    
    # Load engines
    engine = load_reasoning_engine()
    
    # Sidebar input - returns student_data when form is submitted
    new_student_data = display_student_input_form()
    
    # Store in session state when form is submitted
    if new_student_data is not None:
        st.session_state['student_data'] = new_student_data
    
    # Get student_data from session state (persists across button clicks)
    student_data = st.session_state.get('student_data', None)
    
    if student_data is None:
        # Welcome screen
        st.info("""
        **Chào mừng đến với Hệ thống Tư vấn Lộ trình Học tập!**
        
        Hệ thống này sử dụng:
        - **Biểu diễn tri thức** (Knowledge Representation)
        - **Suy luận dựa trên luật** (Rule-based Reasoning)
        
        **Hướng dẫn sử dụng:**
        1. Nhập thông tin sinh viên ở thanh bên trái
        2. Chọn các môn đã hoàn thành
        3. Chọn sở thích và thời gian học tập
        4. Nhấn "Phân tích & Gợi ý"
        
        **Lưu ý:** Hệ thống CHỈ gợi ý môn tự chọn khi có trong học kỳ hiện tại.
        """)
        
        st.markdown("---")
        st.subheader("Giới thiệu về Hệ thống")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Biểu diễn Tri thức:**
            - Môn học: 33 thuộc tính JSON
            - Sinh viên: Hồ sơ + thuộc tính suy diễn
            - Luật: Hard rules + Soft rules
            """)
        
        with col2:
            st.markdown("""
            **Suy luận:**
            - Kiểm tra tiên quyết
            - Tính độ khó môn học
            - Tính điểm gợi ý (α, β, γ)
            """)
        
        return
    
    # Display results
    st.success(f"Đã tải thông tin sinh viên ngành **{student_data['major']}** - "
              f"Năm {student_data['current_year']} {student_data['current_semester']}")
    
    # Main tabs - Lộ trình, Suy luận, Đồ thị
    tab1, tab2, tab3 = st.tabs([
        "Lộ trình Học tập",
        "Luồng Suy luận",
        "Đồ thị Tiên quyết"
    ])
    
    with tab1:
        display_curriculum_plan(engine, student_data['major'], student_data)
    
    with tab2:
        display_reasoning_trace(engine, student_data)
    
    with tab3:
        display_prerequisite_graph(engine, student_data)
    
    # Footer
    st.markdown("---")
    st.caption("""
    **Đồ án môn Biểu diễn Tri thức và Suy luận (CS214)**  
    ĐH Công nghệ Thông tin - ĐHQG-HCM (UIT)  
    *Hệ thống chỉ mang tính tham khảo, không thay thế tư vấn học vụ chính thức.*
    """)


if __name__ == "__main__":
    main()
