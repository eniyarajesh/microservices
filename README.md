# 🧠 User Info Microservice

A backend microservice built using **FastAPI**, **PostgreSQL**, and **Keycloak**, designed to securely register users, issue and validate tokens, and sync data between PostgreSQL and Keycloak using a background scheduler, and trigger password setup emails through Keycloak's built-in flow..

---

## 🚀 Features

- 🔐 Register new users securely with names, email, password(password handled via email setup)
- 🧾 Automated password reset email triggers for new users to set their own password via Keycloak
- ⚙️ Background sync job to sync unsynced PostgreSQL users into Keycloak
- ✅ Keycloak token validation for secured endpoints
- 📜 Email, username, and password validation using modular pattern checks
- 📁 Centralized Logging to both terminal and `logs/user_log.log`

---


## 📁 Project Structure

<pre><code>
user_service/
├── main.py
├── models/
│   └── user_model.py
├── db/
│   └── postgres.py
├── services/
│   ├── user_service.py   
│   ├── auth_service.py
│   └── postgres_service.py
├── auth/
│   └── keycloak_auth.py
├── tasks/
│   └── sync_to_keycloak.py
├── routers/
│   ├── user_router.py
│   └── auth_router.py
├── config/
│   └── settings.py
├── utils/
│   ├── email_pattern.py          
│   ├── email_trigger.py         
│   ├── pswd_pattern.py           
│   └── username_pattern.py      
├── .env
├── requirements.txt   
└── README.md
</code></pre>


---

## 🚀 Getting Started

### ✅ Prerequisites

Before running this project, make sure you have the following installed and configured:

- Python 3.8+
- PostgreSQL (Database created)
- Keycloak (Running locally or via Docker)
- SMTP Email Server (For sending password setup/reset emails)

- **Python 3.8+**  
  Recommended to use a virtual environment

- **PostgreSQL**  
  - Database created  
  - `users` table with required schema

- **Keycloak**  
  - Running locally or via Docker  
  - Realm created (e.g., `user-info-realm`)  
  - Client (e.g., `user-info-client`) with **Direct Access Grants** enabled  
  - Admin user credentials available

- **Redis** 
    (Optional but recommended for caching passwords before syncing to Keycloak)

- **Dependencies**
  - Install Python packages via:
    ```bash
    pip install -r requirements.txt
    ```

- **Environment Variables**

  Set in a .env file or environment:
  <pre><code>
    DATABASE_URL
    KEYCLOAK_URL
    KEYCLOAK_ADMIN
    KEYCLOAK_ADMIN_PASSWORD
    KEYCLOAK_REALM
    KEYCLOAK_CLIENT_ID
    KEYCLOAK_CLIENT_SECRET
    REDIS_HOST
    REDIS_PORT
    EMAIL_USER
    EMAIL_PASSWORD
    </code></pre>

---

### 🔧 Setup

1. Clone the repository:

```bash
git clone https://github.com/your-username/user_service.git
cd user_service
```

2. Create a .env file in the root with the following contents:

3. Update settings.py with your real config if not using .env.

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the app:
```bash
uvicorn main:app --reload
```

6. (Optional) Use Docker:
```bash
docker-compose up --build
```

---

## 📫 API Endpoints

### 👤 Users

#### `POST /users/register`
- Registers a new user
- Stores user details (excluding password) in PostgreSQL
- Triggers a password setup email through Keycloak to the user's email


#### `POST /users/send-password-setup-email`
- Manually triggers a reset password email for existing users via Keycloak

---

### 🔐 Authentication

#### `POST /auth/token`
- Generates an access token using username and password via Keycloak

#### `GET /auth/validate-token`
- Validates a user by verifying the Keycloak access token
- Returns user information if the token is valid

---

## 🔄 Background Sync

A background task runs every **15 seconds** to automatically:

- 🔍 Fetch users from PostgreSQL whose `synced` status is `"False"`
- 🧾 Create those users in Keycloak
- ✅ Mark the users as `synced` in the PostgreSQL database after successful Keycloak registration
- ✅ Trigger email for users to set their own password (using Keycloak action link)

--- 

## ✉️ Email Integration

- Users will receive an email with a password setup link
- Clicking the link opens Keycloak's built-in password reset page
- Users can set their own password securely (without your app handling raw passwords)
---

## Validation Utilities

- Email Validation: **utils/email_pattern.py**
- Username Validation: **utils/username_pattern.py**
- Password Validation: **utils/pswd_pattern.py**
- Modular and reusable **pattern checks**

---

### 🧪 Testing

#### Swagger UI:
```bash
    http://localhost:8000/docs
```

---

### 📋 Logging  

#### All logs are saved to:
```bash
    logs/user_log.log
```

---

### 📦 Tech Stack

- FastAPI – API framework
- PostgreSQL – Relational DB with SQLAlchemy ORM
- Keycloak – Identity & access management
- Redis – (Optional) Caching passwords
- APScheduler – Background jobs
- SMTP (aiosmtplib) – Sending emails
- httpx – Async HTTP client
- Docker – Deployment

---

### 📄 License

    MIT License - free for personal and commercial use.

---
    
  
