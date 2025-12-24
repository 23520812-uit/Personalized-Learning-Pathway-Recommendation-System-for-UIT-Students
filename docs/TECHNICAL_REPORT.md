# Báo Cáo Kỹ Thuật: Mô Hình Biểu Diễn Tri Thức

## Hệ thống Tư vấn Lộ trình Học tập Cá nhân hóa - UIT

**Môn học:** CS214 - Biểu diễn Tri thức và Suy luận  
**Trường:** Đại học Công nghệ Thông tin - ĐHQG-HCM  
**Học kỳ:** HK1 2024-2025

---

## Mục lục

1. [Tổng quan hệ thống](#1-tổng-quan-hệ-thống)
2. [Mô hình biểu diễn tri thức](#2-mô-hình-biểu-diễn-tri-thức)
3. [Hệ thống luật suy luận](#3-hệ-thống-luật-suy-luận)
4. [Bài toán và thuật giải](#4-bài-toán-và-thuật-giải)
5. [Cơ chế suy luận](#5-cơ-chế-suy-luận)
6. [Ví dụ minh họa](#6-ví-dụ-minh-họa)

---

## 1. Tổng Quan Hệ Thống

### 1.1. Bài toán

Xây dựng hệ thống tư vấn lộ trình học tập cá nhân hóa cho sinh viên ngành KHMT và TTNT tại UIT, với các chức năng:

- Gợi ý môn học phù hợp theo từng học kỳ
- Kiểm tra ràng buộc môn tiên quyết
- Tính toán tiến độ tốt nghiệp
- Cá nhân hóa theo sở thích và năng lực

### 1.2. Kiến trúc hệ thống

```text
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                    │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ Student Form│  │ Progress View│  │ Recommendation View│  │
│  └─────────────┘  └──────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Reasoning Engine (reasoning_engine.py)          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ Rule Engine │  │ Scoring Algo │  │ Progress Calculator│  │
│  └─────────────┘  └──────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Knowledge Base (knowledge/)               │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │courses.json │  │ rules.json   │  │teaching_plans.json │  │
│  │ (Ontology)  │  │   (Rules)    │  │     (Plans)        │  │
│  └─────────────┘  └──────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Mô Hình Biểu Diễn Tri Thức

### 2.1. Kiến thức về môn học

Mỗi môn học được biểu diễn bằng một object JSON với các thuộc tính:

```json
{
  "course_id": "CS214",
  "course_name": "Biểu diễn tri thức và suy luận",
  "credits": 4,
  "major": ["KHMT", "TTNT"],
  "course_group": "Chuyên ngành",
  "knowledge_area": ["AI", "Knowledge Representation"],
  "prerequisites": ["IT003", "CS106"],
  "description": "Môn học cung cấp kiến thức về biểu diễn tri thức..."
}
```

**Giải thích các thuộc tính:**

| Thuộc tính | Ý nghĩa | Ví dụ |
|------------|---------|-------|

| `course_id` | Mã môn học duy nhất | "CS214" |
| `course_name` | Tên môn tiếng Việt | "Biểu diễn tri thức và suy luận" |
| `credits` | Số tín chỉ | 4 |
| `major` | Ngành áp dụng | ["KHMT", "TTNT"] |
| `course_group` | Nhóm môn | "Đại cương" / "Cơ sở ngành" / "Chuyên ngành" / "Tốt nghiệp" |
| `knowledge_area` | Lĩnh vực kiến thức | ["AI", "Machine Learning"] |
| `prerequisites` | Môn tiên quyết | ["IT003", "CS106"] |
| `description` | Mục tiêu học tập | "Môn học cung cấp..." |

### 2.2. Quan hệ tiên quyết

Quan hệ tiên quyết được biểu diễn dạng danh sách mã môn trong thuộc tính `prerequisites`:

```text
CS214.prerequisites = ["IT003", "CS106"]

Nghĩa là:
- Phải hoàn thành IT003 (CTDL&GT) VÀ CS106 (TTNT) 
- MỚI được đăng ký CS214
```

**Đồ thị tiên quyết (ví dụ):**

```text
IT001 (NMLT)
    │
    ▼
IT002 (LTHDT) ──────┬──► IT003 (CTDL&GT)
                    │         │
                    │         ▼
                    │    CS106 (TTNT) ──► CS114 (Máy học)
                    │         │
                    │         ▼
                    └──► CS214 (BDTT&SL)
```

### 2.3. Kế hoạch giảng dạy

Kế hoạch giảng dạy được tổ chức theo cấu trúc phân cấp:

```text
teaching_plans/
├── cohort_mappings/
│   ├── K18 → K2023 (CTĐT 2023)
│   ├── K19 → K2024 (CTĐT 2024)
│   └── K20 → K2024 (CTĐT 2024)
│
└── teaching_plans/
    ├── KHMT_K2023/
    │   ├── semester 1: [IT001, MA006, MA003, CS005, ME001]
    │   ├── semester 2: [IT002, IT003, IT012, MA004, MA005]
    │   ├── ...
    │   └── semester 7: [Phương án tốt nghiệp]
    │
    └── TTNT_K2024/
        └── ...
```

### 2.4. Phương án tốt nghiệp

**K18 (K2023) - KHMT & TTNT:**
| Mã môn | Tên môn | TC |

|--------|---------|-----|
| - | Các môn học chuyên đề tốt nghiệp | 10 |
| CS505/AI505 | Khóa luận tốt nghiệp | 10 |

**K19, K20 (K2024) - KHMT:**
| Mã môn | Tên môn | TC |

|--------|---------|-----|
| - | Đồ án tốt nghiệp (CS553) + Môn chuyên đề | 10 |
| CS554 | Đồ án tốt nghiệp tại doanh nghiệp | 10 |
| CS505 | Khóa luận tốt nghiệp | 10 |

**K19, K20 (K2024) - TTNT:**
| Mã môn | Tên môn | TC |

|--------|---------|-----|
| AI505 | Khóa luận tốt nghiệp | 10 |
| AI504 | Đồ án thực tập tại doanh nghiệp | 10 |
| AI503 | Đồ án tốt nghiệp | 6 |
| - | Một trong các môn học chuyên đề tốt nghiệp | 4 |

---

## 3. Hệ Thống Luật Suy Luận

### 3.1. Phân loại luật

```text
Rules
├── hard_rules          # Luật cứng - bắt buộc tuân thủ
├── soft_rules          # Luật mềm - ưu tiên nhưng có thể bỏ qua
├── recommendation_rules # Luật tính điểm gợi ý
└── inference_rules      # Luật suy diễn năng lực
```

### 3.2. Luật cứng (Hard Rules)

#### R001: Kiểm tra tiên quyết

```text
IF course.prerequisites NOT SUBSET OF student.completed_courses
THEN DENY registration
```

**Ví dụ:**

```text
student.completed = [IT001, IT002, IT003]
course = CS214 (prerequisites = [IT003, CS106])

Kiểm tra: IT003 ∈ completed? YES
Kiểm tra: CS106 ∈ completed? NO

Kết luận: KHÔNG đủ điều kiện đăng ký CS214
Thiếu: CS106
```

#### R002: Ràng buộc năm học Anh văn

```text
IF course = ENG01 AND student.year > 1 THEN DENY
IF course = ENG02 AND student.year > 2 THEN DENY
IF course = ENG03 AND student.year > 3 THEN DENY
```

#### R003: Giáo dục quốc phòng cố định

```text
IF course = ME001 
THEN must_register(year=1, semester='HK1')
```

#### R004: Thể dục theo học kỳ

```text
IF course = PE231 THEN only_open_in('HK1')
IF course = PE232 THEN only_open_in('HK2')
```

#### R005: Giới hạn tín chỉ

```text
IF semester_credits < 14 OR semester_credits > 24
THEN WARNING "Tín chỉ không hợp lệ"
```

#### R006: Ưu tiên học lại môn tiên quyết

```text
IF course IN failed_courses 
   AND course IS prerequisite_for(other_courses)
THEN PRIORITIZE course FOR retake
```

#### R007: Ưu tiên bắt buộc trước tự chọn

```text
IF compulsory_courses.remaining > 0
THEN PRIORITIZE compulsory OVER elective
```

### 3.3. Luật mềm (Soft Rules)

#### F001: Bỏ qua môn rớt có thay thế

```text
IF course IN failed_courses 
   AND alternative IN same_elective_slot 
   AND alternative IN (completed ∪ in_progress)
THEN SKIP course FROM recommendations
```

**Ví dụ:**

```text
Slot: "Môn cơ sở ngành-Lập trình (chọn 1)"
Choices: [SE104, CS111]

student.failed = [SE104]
student.completed = [CS111]

Vì CS111 đã hoàn thành → Bỏ qua SE104 trong gợi ý
```

#### F002: Giới hạn Top N môn tự chọn

```text
FOR elective_courses IN recommendations
RETURN TOP(3) ORDER BY score DESC
```

### 3.4. Luật tính điểm gợi ý

#### Công thức tổng hợp

```text
Score = α × Interest + β × Difficulty + γ × Time

Với:
  α = 0.55 (trọng số sở thích)
  β = 0.25 (trọng số độ khó phù hợp)
  γ = 0.20 (trọng số thời gian)
```

#### Interest Match Score

```python
interest_score = |course.knowledge_area ∩ student.interests| / |student.interests|
```

**Ví dụ:**

```text
course.knowledge_area = ["AI", "Machine Learning", "Data Science"]
student.interests = ["AI", "Web Development"]

intersection = ["AI"]
interest_score = 1/2 = 0.5 = 50%
```

#### Difficulty Fit Score

```python
difficulty_score = 1 - |course.difficulty - student.readiness| / max_difficulty
```

#### Time Fit Score

```python
time_score = mapping_function(student.time_availability, course.credits)

# "Nhiều" → prefer 4TC courses → score = 1.0 for 4TC
# "Vừa phải" → prefer 3-4TC → score = 0.8 for 4TC
# "Ít" → prefer 2-3TC → score = 0.5 for 4TC
```

### 3.5. Luật suy diễn năng lực

#### I001: Suy diễn trình độ lập trình

```text
programming_level = MAX(
  1 if IT001 completed,
  2 if IT002 completed,
  3 if CS116 completed
)
```

#### I002: Suy diễn tư duy tính toán

```text
thinking_level = MAX(
  1 if IT003 completed,
  2 if CS112 completed,
  1 if MA006 completed
)
```

#### I003: Suy diễn độ sẵn sàng học tập

```text
academic_readiness = AVG(programming_level, thinking_level) + year_bonus

year_bonus = (current_year - 1) × 0.2
```

---

## 4. Bài Toán và Thuật Giải

### 4.1. Bài toán 1: Kiểm tra điều kiện tiên quyết

**Input:** `course_id`, `completed_courses`  
**Output:** `(is_eligible, missing_prerequisites)`

**Thuật giải:**

```python
def check_prerequisites(course_id, completed_courses):
    course = courses_dict[course_id]
    prerequisites = course.get('prerequisites', [])
    
    missing = []
    for prereq in prerequisites:
        if prereq not in completed_courses:
            missing.append(prereq)
    
    return (len(missing) == 0, missing)
```

**Độ phức tạp:** O(P) với P = số môn tiên quyết

**Ví dụ:**

```text
Input: course_id = "CS214", completed = ["IT001", "IT002", "IT003"]
CS214.prerequisites = ["IT003", "CS106"]

Check: IT003 in completed? → YES
Check: CS106 in completed? → NO

Output: (False, ["CS106"])
```

### 4.2. Bài toán 2: Lọc môn học đủ điều kiện

**Input:** `student_data`  
**Output:** `List[eligible_courses]`

**Thuật giải:**

```python
def get_eligible_courses(student_data):
    completed = student_data['completed_courses']
    current = student_data['current_courses']
    failed = student_data['failed_courses']
    major = student_data['major']
    
    # Build alternative mapping for elective slots
    slot_alternatives = build_elective_slot_groups(major, cohort)
    
    eligible = []
    failed_priority = []  # Failed prereqs first
    
    for course in all_courses:
        course_id = course['course_id']
        
        # Filter 1: Major compatibility
        if major not in course['major']:
            continue
        
        # Filter 2: Not completed or in-progress
        if course_id in completed or course_id in current:
            continue
        
        # Filter 3: Check if failed with alternative done
        if course_id in failed:
            alternatives = slot_alternatives.get(course_id, [])
            if any(alt in completed or alt in current for alt in alternatives):
                continue  # Skip, has alternative
        
        # Filter 4: Prerequisites met
        is_eligible, missing = check_prerequisites(course_id, completed)
        if not is_eligible:
            continue
        
        # Add to appropriate list
        course_copy = course.copy()
        course_copy['is_failed'] = course_id in failed
        
        if course_copy['is_failed'] and is_prerequisite_for_others(course_id):
            failed_priority.append(course_copy)
        else:
            eligible.append(course_copy)
    
    return failed_priority + eligible
```

**Độ phức tạp:** O(C × P) với C = số môn học, P = trung bình số tiên quyết

### 4.3. Bài toán 3: Tính điểm gợi ý cá nhân hóa

**Input:** `course`, `student_profile`  
**Output:** `score ∈ [0, 100]`

**Thuật giải:**

```python
def calculate_recommendation_score(course, student):
    # 1. Interest Match Score (55%)
    course_areas = set(course.get('knowledge_area', []))
    student_interests = set(student.get('interests', []))
    
    if student_interests:
        common = course_areas & student_interests
        interest_score = len(common) / len(student_interests)
    else:
        interest_score = 0.5  # Neutral
    
    # 2. Difficulty Fit Score (25%)
    course_difficulty = calculate_difficulty(course)
    student_readiness = infer_academic_readiness(student)
    
    difficulty_diff = abs(course_difficulty - student_readiness)
    difficulty_score = max(0, 1 - difficulty_diff / 3)
    
    # 3. Time Fit Score (20%)
    time_availability = student.get('time_availability', 'Vừa phải')
    course_credits = course.get('credits', 4)
    
    time_mapping = {
        'Nhiều': {2: 0.6, 3: 0.8, 4: 1.0},
        'Vừa phải': {2: 0.8, 3: 1.0, 4: 0.8},
        'Ít': {2: 1.0, 3: 0.8, 4: 0.5}
    }
    time_score = time_mapping.get(time_availability, {}).get(course_credits, 0.7)
    
    # 4. Combined Score
    final_score = (
        0.55 * interest_score +
        0.25 * difficulty_score +
        0.20 * time_score
    ) * 100
    
    return round(final_score, 1)
```

### 4.4. Bài toán 4: Tính tiến độ tốt nghiệp

**Input:** `student_data`  
**Output:** `progress_report` với quy đổi tín chỉ

**Thuật giải:**

```python
def calculate_graduation_progress(student_data):
    completed = student_data['completed_courses']
    major = student_data['major']
    cohort = student_data['cohort']
    
    # Get graduation requirements
    requirements = get_graduation_requirements(major, cohort)
    
    # Step 1: Count raw credits by category
    raw_credits = {
        'dai_cuong': 0,
        'co_so_nganh': 0,
        'chuyen_nganh': 0,
        'tot_nghiep': 0,
        'tu_chon_tu_do': 0
    }
    
    for course_id in completed:
        course = courses_dict.get(course_id)
        if not course:
            continue
        
        credits = course['credits']
        group = course['course_group']
        
        # Map group to category
        category = map_group_to_category(group)
        raw_credits[category] += credits
    
    # Step 2: Credit conversion (overflow handling)
    final_credits = raw_credits.copy()
    required = requirements['categories']
    
    # Chuyên ngành excess → Tốt nghiệp → Tự do
    excess_major = max(0, raw_credits['chuyen_nganh'] - required['chuyen_nganh'])
    if excess_major > 0:
        final_credits['chuyen_nganh'] = required['chuyen_nganh']
        
        # Transfer to Tốt nghiệp first
        need_grad = required['tot_nghiep'] - final_credits['tot_nghiep']
        transfer_grad = min(excess_major, need_grad)
        final_credits['tot_nghiep'] += transfer_grad
        excess_major -= transfer_grad
        
        # Remaining to Tự do
        final_credits['tu_chon_tu_do'] += excess_major
    
    # Similar for Cơ sở ngành excess → Tự do
    excess_core = max(0, raw_credits['co_so_nganh'] - required['co_so_nganh'])
    if excess_core > 0:
        final_credits['co_so_nganh'] = required['co_so_nganh']
        final_credits['tu_chon_tu_do'] += excess_core
    
    # Step 3: Build progress report
    return {
        'total_required': requirements['total_credits'],
        'total_completed': sum(raw_credits.values()),
        'categories': {
            cat: {
                'required': required[cat],
                'completed': final_credits[cat],
                'percentage': final_credits[cat] / required[cat] * 100
            }
            for cat in raw_credits
        }
    }
```

### 4.5. Bài toán 5: Gợi ý lộ trình học kỳ

**Input:** `student_data`, `target_semester`  
**Output:** `semester_recommendation`

**Thuật giải:**

```python
def recommend_semester_courses(student_data, target_semester):
    major = student_data['major']
    cohort = student_data['cohort']
    
    # Step 1: Get teaching plan for this semester
    plan = get_teaching_plan(major, cohort)
    planned_courses = plan['semesters'][target_semester]
    
    # Step 2: Get all eligible courses
    eligible = get_eligible_courses(student_data)
    eligible_ids = {c['course_id'] for c in eligible}
    
    # Step 3: Prioritize courses
    priority_1 = []  # Compulsory in plan
    priority_2 = []  # Elective in plan
    priority_3 = []  # Core courses
    priority_4 = []  # Other electives
    
    for course in eligible:
        cid = course['course_id']
        group = course['course_group']
        
        if cid in planned_courses['compulsory']:
            priority_1.append(course)
        elif cid in planned_courses['elective']:
            priority_2.append(course)
        elif group in ['Đại cương', 'Cơ sở ngành']:
            priority_3.append(course)
        else:
            priority_4.append(course)
    
    # Step 4: Calculate scores for electives
    for course in priority_2 + priority_3 + priority_4:
        course['score'] = calculate_recommendation_score(course, student_data)
    
    # Step 5: Sort and limit electives
    all_electives = sorted(
        priority_2 + priority_3 + priority_4,
        key=lambda x: x.get('score', 0),
        reverse=True
    )
    
    return {
        'compulsory': priority_1,
        'recommended_electives': all_electives[:3],
        'other_electives': all_electives[3:]
    }
```

---

## 5. Cơ Chế Suy Luận

### 5.1. Forward Chaining (Suy luận tiến)

Hệ thống sử dụng Forward Chaining để từ **facts** (dữ liệu sinh viên) suy ra **conclusions** (môn đủ điều kiện, năng lực).

**Ví dụ:**

```text
FACTS:
  student.completed = [IT001, IT002, IT003, MA003, MA004, MA006]
  student.major = KHMT
  student.year = 2

RULES APPLIED:
  R001: IT001 ∈ completed → IT002 eligible ✓
  R001: IT002 ∈ completed → IT003 eligible ✓  
  R001: IT003 ∈ completed → CS106, CS112 eligible ✓
  
  I001: IT002 ∈ completed → programming_level = 2
  I002: IT003 ∈ completed → thinking_level = 1
  I003: readiness = (2+1)/2 + 0.2 = 1.7

CONCLUSIONS:
  eligible_courses = [IT004, IT005, IT007, CS106, CS112, ...]
  academic_readiness = 1.7
```

### 5.2. Backward Chaining (Suy luận lùi)

Sử dụng để kiểm tra một mục tiêu cụ thể.

**Ví dụ: "Sinh viên có thể đăng ký CS214 không?"**

```text
GOAL: can_register(CS214)

BACKWARD TRACE:
  CS214.prerequisites = [IT003, CS106]
  
  Subgoal 1: IT003 ∈ completed?
    → YES (fact)
  
  Subgoal 2: CS106 ∈ completed?
    → NO
    
    Sub-subgoal: can_register(CS106)?
      CS106.prerequisites = [IT003]
      IT003 ∈ completed? → YES
      → CS106 eligible but not completed
  
CONCLUSION:
  can_register(CS214) = FALSE
  Reason: Missing CS106
  Suggestion: Đăng ký CS106 học kỳ này
```

---

## 6. Ví Dụ Minh Họa

### Scenario: Sinh viên K19 KHMT, học kỳ 3

**Input:**

```json
{
  "cohort": "K19",
  "major": "KHMT", 
  "current_semester": 3,
  "completed_courses": [
    "IT001", "IT002", "IT003", "IT012",
    "MA003", "MA004", "MA005", "MA006",
    "CS005", "ME001"
  ],
  "failed_courses": [],
  "interests": ["AI", "Machine Learning"],
  "time_availability": "Nhiều"
}
```

**Bước 1: Suy diễn năng lực**

```text
programming_level = 2 (có IT002)
thinking_level = 1 (có IT003)
year_bonus = (2-1) × 0.2 = 0.2
academic_readiness = (2+1)/2 + 0.2 = 1.7
```

**Bước 2: Lọc môn đủ điều kiện**

```text
Eligible: IT004, IT005, IT007, CS112, CS106, CS115, SS007, ...
```

**Bước 3: So khớp với kế hoạch giảng dạy HK3**

```text
KHMT_K2024.semesters['3']:
  Compulsory: IT004, IT007, AI002, CS115
  (IT005 đã chuyển sang HK4)
```

**Bước 4: Tính điểm và xếp hạng**

| Môn | Loại | Interest | Difficulty | Time | Score |
|-----|------|----------|------------|------|-------|
| IT004 | Bắt buộc | - | - | - | - |
| IT007 | Bắt buộc | - | - | - | - |
| CS115 | Bắt buộc | - | - | - | - |
| SS007 | Bắt buộc | - | - | - | - |
| CS106 | Tự chọn | 0.5 | 0.8 | 1.0 | 68.5 |
| CS114 | Tự chọn | 1.0 | 0.7 | 1.0 | 82.3 |

**Kết quả gợi ý:**

**Môn bắt buộc:**
| Mã môn | Tên môn | TC |

|--------|---------|-----|
| IT004 | Cơ sở dữ liệu | 4 |
| IT007 | Hệ điều hành | 4 |
| CS115 | Toán cho KHMT | 4 |
| SS007 | Triết học Mác-Lênin | 3 |

**Môn tự chọn gợi ý (Top 3):**
| Mã môn | Tên môn | TC | Điểm |

|--------|---------|-----|------|
| CS114 | Máy học | 4 | 82.3 |
| CS106 | Trí tuệ nhân tạo | 4 | 68.5 |
| CS231 | Thị giác máy tính | 4 | 65.0 |

**Tổng: 15-19 TC** (trong giới hạn 14-24 TC)

---

## Kết Luận

### Ưu điểm của mô hình

1. **Tách biệt tri thức và logic**: Knowledge Base (JSON) độc lập với Reasoning Engine (Python)
2. **Dễ mở rộng**: Thêm môn học, luật mới chỉ cần cập nhật file JSON
3. **Cá nhân hóa**: Điểm gợi ý dựa trên profile cụ thể của từng sinh viên
4. **Giải thích được**: Có thể trace ngược lý do cho mỗi gợi ý

### Hạn chế

1. Chưa xử lý xung đột thời khóa biểu
2. Chưa tích hợp đánh giá/feedback từ sinh viên khác
3. Cần cập nhật thủ công khi CTĐT thay đổi

### Hướng phát triển

1. Tích hợp LLM để sinh giải thích bằng ngôn ngữ tự nhiên
2. Học từ lịch sử đăng ký của sinh viên (collaborative filtering)
3. Kết nối với hệ thống đăng ký môn học thực tế của UIT
