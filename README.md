# Mô Hình Biểu Diễn Tri Thức và Suy Luận
## Hệ thống Tư vấn Lộ trình Học tập Cá nhân hóa - UIT

**Môn học:** CS214 - Biểu diễn Tri thức và Suy luận  
**Nhóm thực hiện:** [Tên nhóm]  
**Ngày cập nhật:** 22/12/2024

---

## 1. Tổng Quan Hệ Thống

### 1.1. Mô tả bài toán
Hệ thống tư vấn lộ trình học tập cá nhân hóa cho sinh viên ngành **Khoa học Máy tính (KHMT)** và **Trí tuệ Nhân tạo (TTNT)** tại Trường Đại học Công nghệ Thông tin - ĐHQG-HCM.

### 1.2. Mục tiêu
- Gợi ý môn học phù hợp theo từng học kỳ
- Kiểm tra ràng buộc môn tiên quyết
- Tính toán tiến độ tốt nghiệp
- Cá nhân hóa theo sở thích và năng lực sinh viên

---

## 2. Mô Hình Biểu Diễn Tri Thức

### 2.1. Kiến trúc Knowledge Base

```
knowledge/
├── courses.json        # Ontology môn học
├── rules.json          # Luật suy luận
└── teaching_plans.json # Kế hoạch giảng dạy theo khóa
```

### 2.2. Ontology Môn học (courses.json)

#### 2.2.1. Schema biểu diễn một môn học

```json
{
  "course_id": "CS214",
  "course_name": "Biểu diễn tri thức và suy luận",
  "credits": 4,
  "major": ["KHMT", "TTNT"],
  "course_group": "Chuyên ngành",
  "knowledge_area": ["AI", "Knowledge Representation"],
  "prerequisites": ["IT003", "CS106"],
  "description": "Mô tả chi tiết môn học..."
}
```

#### 2.2.2. Các thuộc tính quan trọng

| Thuộc tính | Kiểu dữ liệu | Mô tả |
|------------|--------------|-------|
| `course_id` | String | Mã môn học duy nhất |
| `course_name` | String | Tên môn học tiếng Việt |
| `credits` | Integer | Số tín chỉ (1-10) |
| `major` | Array[String] | Ngành học áp dụng |
| `course_group` | String | Nhóm: Đại cương / Cơ sở ngành / Chuyên ngành / Tốt nghiệp |
| `knowledge_area` | Array[String] | Lĩnh vực kiến thức |
| `prerequisites` | Array[String] | Danh sách mã môn tiên quyết |
| `description` | String | Mô tả mục tiêu học tập |

#### 2.2.3. Phân loại môn học theo nhóm

```
Đại cương (45 TC)
├── Lý luận chính trị và pháp luật (13 TC)
├── Toán - Tin học - KHTN (18 TC)
├── Ngoại ngữ (12 TC)
└── Kỹ năng nghề nghiệp (2 TC)

Cơ sở ngành (45 TC - KHMT, 57 TC - TTNT)
├── Bắt buộc: IT001, IT002, IT003, IT004, IT005, IT007, IT012, CS005, CS112
├── Tự chọn Lập trình (8 TC): SE104, CS111, CS116, CS311, CS526
└── Tự chọn Thuật toán (4 TC): CS117, CS523

Chuyên ngành (16 TC - KHMT, 8 TC - TTNT)
├── Tri thức và Suy luận: CS217, CS214, CS211, CS315, CS106, CS114
├── Thị giác máy tính: CS231, CS232, CS221, CS229
├── Xử lý ngôn ngữ: CS221, CS222, CS226
└── Máy học và Khai phá dữ liệu: CS114, CS338, CS336

Tốt nghiệp (10 TC)
├── Khóa luận tốt nghiệp
├── Đồ án tốt nghiệp tại doanh nghiệp
└── Chuyên đề tốt nghiệp + Môn bổ sung
```

### 2.3. Kế hoạch Giảng dạy (teaching_plans.json)

#### 2.3.1. Cấu trúc theo Khóa học

```json
{
  "cohort_mappings": {
    "K18": {"enrollment_year": 2023, "curriculum": "K2023"},
    "K19": {"enrollment_year": 2024, "curriculum": "K2024"},
    "K20": {"enrollment_year": 2025, "curriculum": "K2024"}
  },
  "teaching_plans": {
    "KHMT_K2023": {
      "major": "KHMT",
      "curriculum_year": "K2023",
      "semesters": {
        "1": {"courses": [...], "total_credits": 16},
        "2": {"courses": [...], "total_credits": 23},
        ...
        "7": {"courses": [...], "total_credits": 10}
      }
    }
  }
}
```

#### 2.3.2. Biểu diễn môn trong học kỳ

**Môn bắt buộc:**
```json
{
  "id": "IT001",
  "name": "Nhập môn Lập trình",
  "credits": 4,
  "type": "compulsory"
}
```

**Môn tự chọn với các lựa chọn:**
```json
{
  "elective_slot": "Môn cơ sở ngành-Lập trình (chọn 1)",
  "credits": 4,
  "type": "elective",
  "choices": ["SE104", "CS111"]
}
```

**Môn không có mã (placeholder):**
```json
{
  "id": "-",
  "name": "Các môn học chuyên đề tốt nghiệp",
  "credits": 10,
  "type": "compulsory"
}
```

---

## 3. Hệ Thống Luật Suy Luận (rules.json)

### 3.1. Phân loại Luật

```
Rules
├── hard_rules      # Luật cứng - bắt buộc tuân thủ
├── soft_rules      # Luật mềm - ưu tiên nhưng có thể bỏ qua
├── recommendation_rules  # Luật tính điểm gợi ý
└── inference_rules      # Luật suy diễn năng lực
```

### 3.2. Hard Rules (Luật Cứng)

#### R001: Prerequisite Check
```
IF course.prerequisites NOT IN student.completed_courses
THEN DENY registration
```

**Ví dụ:**
- `CS106` (Trí tuệ nhân tạo) yêu cầu `IT003` (CTDL&GT)
- Nếu sinh viên chưa hoàn thành IT003 → Không được đăng ký CS106

#### R002: English Course Year Constraint
```
IF course_id = 'ENG01' AND student.year > 1 THEN DENY
IF course_id = 'ENG02' AND student.year > 2 THEN DENY
IF course_id = 'ENG03' AND student.year > 3 THEN DENY
```

#### R003: Military Education Fixed Semester
```
IF course_id = 'ME001' THEN must_register(year=1, semester='HK1')
```

#### R004: Physical Education Semester Constraint
```
IF course_id = 'PE231' THEN only_open_in('HK1')
IF course_id = 'PE232' THEN only_open_in('HK2')
```

#### R005: Credit Limit
```
IF semester_credits < 14 OR semester_credits > 24
THEN WARNING "Tín chỉ không hợp lệ"
```

#### R006: Course Retake Priority
```
IF course IN failed_courses AND course IS prerequisite_for(other_courses)
THEN PRIORITIZE course FOR retake
```

#### R007: Compulsory Before Elective
```
IF compulsory_courses.remaining > 0
THEN PRIORITIZE compulsory_courses OVER elective_courses
```

### 3.3. Soft Rules (Luật Mềm)

#### F001: Skip Failed Elective With Alternative
```
IF course IN failed_courses 
   AND alternative_course IN same_elective_slot 
   AND alternative_course IN (completed OR in_progress)
THEN SKIP course FROM recommendations
```

**Ví dụ:** Nếu sinh viên rớt SE104 nhưng đã học CS111 (cùng slot "Lập trình"), thì không cần học lại SE104.

#### F002: Top N Elective Selection
```
FOR elective_courses IN recommendations
RETURN TOP(3) ORDER BY recommendation_score DESC
```

### 3.4. Recommendation Rules (Luật Tính Điểm)

#### S001-S004: Công thức tính điểm gợi ý

```
Recommendation_Score = α × Interest_Match + β × Difficulty_Fit + γ × Time_Fit

Với:
- α = 0.55 (trọng số sở thích)
- β = 0.25 (trọng số độ khó phù hợp)
- γ = 0.20 (trọng số thời gian)
```

**Interest Match Score:**
```python
interest_score = len(course.knowledge_area ∩ student.interests) / len(student.interests)
```

**Difficulty Fit Score:**
```python
difficulty_score = 1 - |course.difficulty - student.academic_readiness| / max_difficulty
```

**Time Fit Score:**
```python
time_score = mapping(student.time_availability, course.credits)
# "Nhiều" → prefer 4TC courses
# "Vừa phải" → prefer 3-4TC courses  
# "Ít" → prefer 2-3TC courses
```

### 3.5. Inference Rules (Luật Suy Diễn)

#### I001: Programming Level Inference
```
programming_level = MAX(
  IT001 completed → level 1,
  IT002 completed → level 2,
  CS116 completed → level 3
)
```

#### I002: Computational Thinking Inference
```
thinking_level = MAX(
  IT003 completed → level 1,
  CS112 completed → level 2,
  MA006 completed → level 1
)
```

#### I003: Academic Readiness Inference
```
academic_readiness = AVG(programming_level, thinking_level) + year_bonus
year_bonus = (current_year - 1) × 0.2
```

---

## 4. Bài Toán và Thuật Giải

### 4.1. Bài toán 1: Kiểm tra Điều kiện Tiên quyết

**Input:** `course_id`, `completed_courses`  
**Output:** `(is_eligible: bool, missing_prerequisites: List)`

**Thuật giải:**
```python
def check_prerequisites(course_id, completed_courses):
    course = get_course(course_id)
    prerequisites = course.prerequisites
    missing = [pre for pre in prerequisites if pre not in completed_courses]
    return (len(missing) == 0, missing)
```

**Độ phức tạp:** O(n) với n = số môn tiên quyết

### 4.2. Bài toán 2: Lọc Môn Học Đủ Điều Kiện

**Input:** `student_data` (completed, failed, major, cohort)  
**Output:** `List[eligible_courses]`

**Thuật giải:**
```python
def get_eligible_courses(student_data):
    eligible = []
    for course in all_courses:
        # Filter by major
        if student.major not in course.major:
            continue
        # Filter completed/in-progress
        if course.id in (completed ∪ current):
            continue
        # Check prerequisites
        if not check_prerequisites(course.id, completed):
            continue
        # Check special rules (PE, AV, ME)
        if not check_special_rules(course, year, semester):
            continue
        eligible.append(course)
    return prioritize(eligible)  # Failed prereqs first
```

### 4.3. Bài toán 3: Tính Điểm Gợi Ý Cá Nhân Hóa

**Input:** `course`, `student_profile`  
**Output:** `recommendation_score: float [0-100]`

**Thuật giải:**
```python
def calculate_recommendation_score(course, student):
    # Interest Match (55%)
    common_interests = course.knowledge_area ∩ student.interests
    interest_score = len(common_interests) / len(student.interests)
    
    # Difficulty Fit (25%)
    course_difficulty = calculate_difficulty(course)
    student_readiness = infer_academic_readiness(student)
    difficulty_score = 1 - abs(course_difficulty - student_readiness) / 3
    
    # Time Fit (20%)
    time_score = time_availability_mapping(student.time, course.credits)
    
    # Combined Score
    final_score = (
        0.55 * interest_score +
        0.25 * difficulty_score +
        0.20 * time_score
    ) * 100
    
    return round(final_score, 1)
```

### 4.4. Bài toán 4: Tính Tiến Độ Tốt Nghiệp

**Input:** `student_data`  
**Output:** `progress_report` với quy đổi tín chỉ

**Thuật giải:**
```python
def calculate_graduation_progress(student):
    # 1. Tính tín chỉ thô theo từng nhóm
    raw_credits = count_credits_by_category(completed_courses)
    
    # 2. Quy đổi tín chỉ thừa
    # Chuyên ngành thừa → Tốt nghiệp → Tự do
    excess_major = max(0, raw['chuyen_nganh'] - required['chuyen_nganh'])
    
    if excess_major > 0:
        # Chuyển sang Tốt nghiệp trước
        transfer_to_grad = min(excess_major, required['tot_nghiep'] - raw['tot_nghiep'])
        final['tot_nghiep'] += transfer_to_grad
        excess_major -= transfer_to_grad
        
        # Phần còn lại sang Tự do
        final['tu_chon_tu_do'] += excess_major
    
    return progress_report
```

### 4.5. Bài toán 5: Gợi Ý Lộ Trình Học Kỳ

**Input:** `student_data`, `target_semester`  
**Output:** `recommended_courses` với phân loại

**Thuật giải:**
```python
def recommend_semester_courses(student, semester):
    # 1. Lấy kế hoạch giảng dạy
    teaching_plan = get_teaching_plan(student.major, student.cohort)
    planned = teaching_plan.semesters[semester]
    
    # 2. Lấy môn đủ điều kiện
    eligible = get_eligible_courses(student)
    
    # 3. Phân loại ưu tiên
    priority_1 = filter(eligible, planned.compulsory)  # Bắt buộc theo kế hoạch
    priority_2 = filter(eligible, planned.elective)    # Tự chọn theo kế hoạch
    priority_3 = filter(eligible, core_courses)        # Đại cương, Cơ sở ngành
    priority_4 = remaining(eligible)                   # Các môn khác
    
    # 4. Tính điểm và sắp xếp
    for course in eligible:
        course.score = calculate_recommendation_score(course, student)
    
    # 5. Trả về kết quả
    return {
        'compulsory': priority_1,
        'elective': sorted(priority_2 + priority_3 + priority_4, by='score')[:3]
    }
```

---

## 5. Cơ Chế Suy Luận

### 5.1. Forward Chaining (Suy luận tiến)

Hệ thống sử dụng Forward Chaining để:
1. Từ các **facts** (môn đã học) → suy ra **conclusions** (môn đủ điều kiện)
2. Từ **profile** sinh viên → suy ra **academic readiness**

```
Facts:
  - student.completed = [IT001, IT002, IT003, MA003, MA004]
  - student.major = KHMT

Rules Applied:
  R001: IT001 done → IT002 eligible ✓
  R001: IT003 done → CS106 eligible ✓
  R001: IT003 done → CS112 eligible ✓
  I001: IT002 done → programming_level = 2
  I002: IT003 done → thinking_level = 1

Conclusions:
  - eligible_courses = [CS106, CS112, IT004, IT005, ...]
  - academic_readiness = 1.5
```

### 5.2. Backward Chaining (Suy luận lùi)

Sử dụng để kiểm tra mục tiêu cụ thể:

```
Goal: Can student register CS214?

Backward Trace:
  CS214.prerequisites = [IT003, CS106]
  
  Check IT003 in completed? → YES
  Check CS106 in completed? → NO
  
  Subgoal: Can register CS106?
    CS106.prerequisites = [IT003]
    Check IT003 in completed? → YES
    → CS106 eligible

Conclusion: CS214 not eligible yet (need CS106 first)
Suggestion: Register CS106 this semester
```

---

## 6. Kiến Trúc Hệ Thống

```
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
│  │ courses.json│  │  rules.json  │  │teaching_plans.json │  │
│  │ (Ontology)  │  │   (Rules)    │  │   (Plans)          │  │
│  └─────────────┘  └──────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Ví Dụ Minh Họa

### 7.1. Scenario: Sinh viên K19 KHMT, HK3

**Input:**
```json
{
  "cohort": "K19",
  "major": "KHMT",
  "current_semester": 3,
  "completed_courses": ["IT001", "IT002", "IT003", "IT012", "MA003", "MA004", "MA005", "MA006", "CS005", "ME001"],
  "interests": ["AI", "Machine Learning"]
}
```

**Suy luận:**
1. Programming Level = 2 (có IT002)
2. Thinking Level = 1 (có IT003)
3. Academic Readiness = 1.5 + 0.4 (year 2) = 1.9

**Kết quả gợi ý HK3:**

| STT | Mã môn | Tên môn | TC | Loại | Điểm |
|-----|--------|---------|-----|------|------|
| 1 | IT004 | Cơ sở dữ liệu | 4 | Bắt buộc | - |
| 2 | IT007 | Hệ điều hành | 4 | Bắt buộc | - |
| 3 | CS115 | Toán cho KHMT | 4 | Bắt buộc | - |
| 4 | SS007 | Triết học Mác-Lênin | 3 | Bắt buộc | - |
| 5 | CS106 | Trí tuệ nhân tạo | 4 | Tự chọn | 85 |
| 6 | CS114 | Máy học | 4 | Tự chọn | 82 |

---

## 8. Hướng Dẫn Triển Khai (Deployment)

### 8.1. Chạy ứng dụng cục bộ (Local)

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/course-recommendation-uit.git
cd course-recommendation-uit

# 2. Cài đặt dependencies
pip install -r requirements.txt

# 3. Chạy ứng dụng
streamlit run app.py
```

### 8.2. Deploy lên Streamlit Cloud

**Bước 1:** Đẩy code lên GitHub repository

```bash
git init
git add .
git commit -m "Initial commit - Course Recommendation System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/course-recommendation-uit.git
git push -u origin main
```

**Bước 2:** Truy cập [share.streamlit.io](https://share.streamlit.io)

**Bước 3:** Đăng nhập bằng tài khoản GitHub

**Bước 4:** Click "New app" và điền thông tin:
- **Repository:** `YOUR_USERNAME/course-recommendation-uit`
- **Branch:** `main`
- **Main file path:** `app.py`

**Bước 5:** Click "Deploy!" và đợi quá trình build hoàn tất

### 8.3. Cấu trúc thư mục cho deployment

```
course-recommendation-uit/
├── .streamlit/
│   └── config.toml          # Cấu hình Streamlit
├── knowledge/
│   ├── courses.json         # Dữ liệu môn học
│   ├── rules.json           # Luật suy luận
│   └── teaching_plans.json  # Kế hoạch giảng dạy
├── docs/
│   └── TECHNICAL_REPORT.md  # Báo cáo kỹ thuật chi tiết
├── app.py                   # Ứng dụng Streamlit chính
├── reasoning_engine.py      # Engine suy luận
├── requirements.txt         # Dependencies
├── README.md               # Tài liệu hướng dẫn
└── .gitignore              # Files cần ignore
```

### 8.4. Yêu cầu hệ thống

- Python 3.8+
- Streamlit 1.31.0+
- NetworkX 3.2.1+
- PyVis 0.3.2+
- Pandas 2.2.0+

---

## 9. Kết Luận

### 9.1. Ưu điểm mô hình
- **Tách biệt tri thức và logic**: Knowledge Base độc lập với Reasoning Engine
- **Dễ mở rộng**: Thêm môn học, luật mới chỉ cần cập nhật JSON
- **Cá nhân hóa**: Điểm gợi ý dựa trên profile cụ thể của sinh viên
- **Giải thích được**: Có thể trace ngược lý do gợi ý

### 9.2. Hạn chế
- Chưa xử lý xung đột thời khóa biểu
- Chưa tích hợp đánh giá từ sinh viên khác
- Cần cập nhật thủ công khi CTĐT thay đổi

### 9.3. Hướng phát triển
- Tích hợp LLM để giải thích tự nhiên
- Học từ lịch sử đăng ký của sinh viên
- Kết nối với hệ thống đăng ký môn học thực tế

---

## Tài liệu tham khảo

1. Chương trình đào tạo KHMT, TTNT - UIT (2023, 2024)
2. Quy chế đào tạo đại học - ĐHQG-HCM
3. Russell & Norvig - Artificial Intelligence: A Modern Approach (Chapter 7, 8 - Knowledge Representation)
