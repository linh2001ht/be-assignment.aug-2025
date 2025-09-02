## ⚙️ Cài đặt

1.  **Clone repository**
    ```bash
    git clone [https://github.com/linh2001ht/be-assignment.aug-2025.git](https://github.com/linh2001ht/be-assignment.aug-2025.git)
    cd be-assignment.aug-2025
    ```

2.  **Cấu hình biến môi trường**
    * Tạo file `.env` từ file mẫu `.env.example`.
    * Điền các giá trị cần thiết như `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, v.v.

3.  **Sử dụng Docker Compose**
    ```bash
    docker-compose up --build -d
    ```
    Lệnh này sẽ build các Docker image, khởi tạo các container và chạy ứng dụng ở chế độ nền.

4.  **Chạy migrations cho cơ sở dữ liệu**
    * Kiểm tra file `alembic/env.py` của bạn. Hãy đảm bảo nó được cấu hình để đọc `DATABASE_URL` từ biến môi trường.
    * **Tạo script migration (chỉ cần chạy lần đầu)**
    ```bash
    docker-compose run --rm backend alembic revision --autogenerate -m "Create all tables"
    ```
    * **Lưu ý**: Kiểm tra file migration mới được tạo trong thư mục `alembic/versions` trước khi áp dụng.
    * **Áp dụng các thay đổi**
    ```bash
    docker-compose run --rm backend alembic upgrade head
    ```

## Cách Sử Dụng

* **API Swagger UI**: `http://localhost:80/docs`.
* Sau khi đăng ký, người dùng có thể tạo một tổ chức mới và tự động được gán vai trò **Admin** của tổ chức đó.
* Hoặc, một **Admin** hiện có của tổ chức có thể thêm người dùng mới vào tổ chức và gán vai trò cho họ.





---

# 📑 Intern Backend Developer Assignment

- Copyright (c) River Flow Solutions, Jsc. 2025. All rights reserved.
- We only use the submissions for candidates evaluation.

## **A. Instructions**
- Submission:
  - Candidate must fork this repository to a private repo under their name for submission. Notify email `hr@riverflow.solutions` when done.
  - Candidate must add the following accounts as collaborators so our team can review your submission:
    - `phunv-abx`
    - `hle-abx`

- Build a **multi-organization Task Management backend** (organizations → projects → tasks) with basic collaboration and notifications.  
- **Stack**: Python, FastAPI, PostgreSQL, Redis, Nginx.
- Use Justfile for all run and development commands.
- Use Docker for deployment.
- Deliverables: GitHub repo, ER + System design diagrams, Dockerized deployment, README. 

---

## **B. Task Management Requirements & Use Cases**

### **B1. Functional Scope**
- **Organizations & Users**
  - Each user belongs to an organization.  
  - Roles: **Admin**, **Manager**, **Member**.  

- **Projects**
  - Belong to one organization.  
  - Can add/remove members.  
  - Admin/Manager can create projects, Members can only participate.  

- **Tasks**
  - CRUD operations.  
  - Belong to a project.  
  - Fields: title, description, status (`todo/in-progress/done`), priority (`low/medium/high`), due_date, assignee.  
  - Status workflow: `todo → in-progress → done` (no complex review step).  

- **Collaboration**
  - Users can comment on tasks.  
  - Users can upload simple file attachments (local storage).  

- **Notifications**
  - Users receive a notification when:  
    - They are assigned a task.  
    - Task status changes.  
    - A comment is added to their task.  

- **Reports (Basic)**
  - Count of tasks by status in a project.  
  - List of overdue tasks.  

---

### **B2. Use Cases**
1. **User Management**
   - Register/login with JWT.  
   - Admin adds users to the organization.  

2. **Project Management**
   - Create/list projects.  
   - Add/remove project members.  

3. **Task Management**
   - Create tasks with title, description, assignee, priority, due date.  
   - Update task status (`todo → in-progress → done`).  
   - List tasks in a project (filter by status, assignee, priority).  

4. **Collaboration**
   - Add comments to tasks.  
   - Upload attachment to a task.  

5. **Notifications**
   - Retrieve unread notifications.  
   - Mark notifications as read.  

6. **Reporting**
   - Get per-project task count by status.  
   - Get overdue tasks in a project.  

---

### **B3. Business Rules**
- Only project members can create or update tasks in that project.  
- Only Admin/Manager can assign tasks to others. Members can assign only to themselves.  
- Due date must be today or in the future (not past).  
- Task status can only progress forward (`todo → in-progress → done`), but not backward.  
- Attachments limited to 5MB each, max 3 per task.  

---

## **C. Tech Requirements**
- **Backend**: Python + FastAPI, SQLAlchemy, Alembic migrations.  
- **Database**: PostgreSQL with foreign keys + indexes.  
- **Cache/Notify**: Redis for caching task lists and storing notifications.  
- **Auth**: JWT (PyJWT) + role-based access (Admin/Manager/Member).  
- **Testing**: pytest with mock PostgreSQL & Redis.  
- **Deployment**: Docker + docker-compose (FastAPI + PostgreSQL + Redis + Nginx).  

---

## **D. Review Criteria**

### **D1. Database & System Design**
- [ ] Schema with correct relations & constraints.  
- [ ] Indexes on `users(email)`, `tasks(status, project_id)`.  
- [ ] ER diagram + system design diagram included.  

### **D2. Core Functionality**
- [ ] JWT auth with role-based permissions.  
- [ ] CRUD for Projects and Tasks with proper rules.  
- [ ] Status workflow enforced (`todo → in-progress → done`).  
- [ ] Comments & file attachments working.  
- [ ] Notifications created on assign/status/comment.  
- [ ] Basic reporting endpoints working.  

### **D3. Code Quality**
- [ ] Centralized error handling & logging.  
- [ ] Configurable via `.env`.  

### **D4. Testing**
- [ ] Coverage ≥ 70%.  

### **D5. Deployment**
- [ ] Nginx configuration.  
- [ ] Dockerized deployment (Include Nginx)

### **D6. Documentation**
- [ ] README with setup guide.  
- [ ] API documentation (Swagger UI).
