# 🛍️ Healthcare Appointment Booking API

This is a FastAPI-based backend application that includes core user management and appointment booking features with proper validation and structure following FastAPI standards

## 🚀 Features Implemented

### ✅ User Management
- **User Registration**
  - Accepts profile image (uploaded via `multipart/form-data`)
  - Stores hashed password
- **JWT-based authentication and route protection**
- **Get Single User by ID**
- **Update User Profile**
  - Allows updating profile image and user details
### 🩺 Appointment Booking
- Book an appointment with:
  - **Doctor Selection**
  - **Appointment Date & Time**
  - **Notes/Symptoms**
  - **Status** (Enum: `pending`, `confirmed`, `cancelled`, `completed`)
- Validates:
  - Doctor availability on requested date and time
  - Logical data integrity

## ⚙️ Tech Stack

- **Backend Framework**: FastAPI
- **Database ORM**: SQLModel (built on SQLAlchemy)
- **Database**: PostgreSQL
- **Password Hashing**: Passlib
- **Validation**: Pydantic + FastAPI Form/File handling




## 🚀 Setup Instructions or Installation


1. **Clone the repository:**

```bash
git clone https://github.com/siamCSEJnU/healthcare-booking-backend.git
cd healthcare-booking-backend
 ```
2. **Create Virtual Environment:**

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
 ```

3. **Install Dependencies:**

```bash
pip install -r requirements.txt
 ```


4. **Configurations:** 
 Create a .env file with these variables:

Add to .env:
```bash
LOCAL_DATABASE_URL=postgresql://postgres:your_password@localhost:5432/database_name
SECRET_KEY = your_own_secret_key
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30
 ```
5. **Run The App**

```bash
uvicorn app.main:app --reload

 ```
or,
```bash
fastapi run app/main.py

 ```

### ✅ **Access Docs**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
### ✅ **images**

<img width="1920" height="1457" alt="screencapture-localhost-8000-docs-2025-07-20-01_36_49" src="https://github.com/user-attachments/assets/85d80b08-0b08-47bf-91b7-37fc87c30f3c" />

## Note

- Profile images are handled via FastAPI File() and stored locally (or can be extended to use cloud storage).
- The system validates that a doctor is not double-booked for the same time.
- Passwords are stored securely using hashing.
- Profile image upload is handled with basic file type checks (can be extended).





## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contact
siamahmed234@gmail.com

