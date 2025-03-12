# Multi-Tenant SaaS Platform

## Overview
This project is a **multi-tenant SaaS (Software-as-a-Service) API** that enables organizations to create accounts, manage users, and handle subscriptions.

## Features
- Multi-tenancy support
- Organization and subscription management
- User authentication and management
- Project and task management

## Tech Stack
- **Backend**: Django REST Framework (DRF)
- **Authentication**: JWT-based authentication
- **Database**: PostgreSQL (supports multi-tenancy)
- **API Documentation**: drf-spectacular (OpenAPI/Swagger)

## API Documentation

- For a full list of API endpoints, check out the Swagger documentation:
 - 🔗 Swagger UI
## API Endpoints
### Organization & Subscription Management
- **Create Organization & Subscription**: `POST /organization/`
- **Change Subscription Plan**: `PUT /organization/{org_id}/change-subscription/`
- **Get Organization Details**: `GET /organization/{org_id}/`

### User & Authentication
- **User Registration & Login**: `POST /register/`, `POST /login/`
- **Invite User to Organization**: `POST /organization/{org_id}/invite/`
- **Remove User from Organization**: `DELETE /organization/{org_id}/removeuser/`

### Project & Task Management
- **Create Project**: `POST /projects/`
- **Assign Task to User**: `POST /tasks/`
- **Retrieve Tasks**: `GET /tasks/all/?status=&project=&due_date=` (Filterable)

## Installation & Setup
1. **Clone Repository**
   ```sh
   git clone https://github.com/sufyanfaizi/Saas-Platform.git
   cd Saas-Platform
   ```
2. **Create & Activate Virtual Environment**
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Apply Migrations**
   ```sh
   python manage.py migrate
   ```
5. **Run Development Server**
   ```sh
   python manage.py runserver
   ```

## Authentication
- Uses JWT (JSON Web Token)
- Obtain token: `POST /login/`
- Include token in requests:
  ```sh
  Authorization: Bearer <your_token>
  ```

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature-xyz`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to your fork and create a Pull Request

## License
This project is licensed under the MIT License.

