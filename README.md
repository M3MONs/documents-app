# Documents App

A comprehensive full-stack document management system built with FastAPI backend and React frontend. This application allows users to organize, upload, and manage documents within structured organizations, categories, and folders with robust role-based access control.

<img width="1920" height="945" alt="screencapture-localhost-5173-login-2026-01-19-19_54_53" src="https://github.com/user-attachments/assets/d70733b6-9bfe-4505-9fee-88fe9041c5a0" />
<img width="1920" height="945" alt="screencapture-localhost-5173-2026-01-19-19_55_11" src="https://github.com/user-attachments/assets/607ae9c0-a2dd-4fa9-a3db-62a934393cb2" />
<img width="1920" height="945" alt="screencapture-localhost-5173-categories-1b9f5a48-d7d5-4095-b4b9-4f3d6c0c4686-2026-01-19-19_56_22" src="https://github.com/user-attachments/assets/e3117371-e4c5-45ac-a619-f9051a71e943" />
<img width="1920" height="945" alt="screencapture-localhost-5173-categories-1b9f5a48-d7d5-4095-b4b9-4f3d6c0c4686-2026-01-19-19_56_38" src="https://github.com/user-attachments/assets/02823137-a271-4915-90d1-b3d236e66623" />

## Features

- **User Authentication & Authorization**: JWT-based authentication
- **Role-Based Access Control**: Granular permissions for users, admins, and organization roles
- **Organization Management**: Create and manage multiple organizations with departments
- **Document Organization**: Hierarchical structure with categories, folders, and documents
- **File Management**: Upload, download, and view documents with support for various file types
- **Document Viewing**: Built-in viewer for images, PDFs, and text files
- **Admin Panel**: Comprehensive administration interface for system management
- **File Synchronization**: Track file changes and sync status
- **Responsive UI**: Modern, accessible interface built with React, Shadcn and Tailwind CSS

## Technology Stack

### Backend
- **FastAPI**: High-performance web framework for building APIs
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database
- **Pydantic**: Data validation and serialization
- **JWT**: Authentication tokens
- **Alembic**: Database migrations

### Frontend
- **React**: UI library with TypeScript
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Shadcn**: Accessible component library
- **React Query**: Data fetching and caching
- **React Hook Form**: Form management
- **React Router**: Client-side routing

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL database

### Backend Setup

1. Navigate to the server directory:
   ```bash
   cd server
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your database URL and other configuration.

5. Start the backend server:
   ```bash
   fastapi dev main.py
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the client directory:
   ```bash
   cd client
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:5173`

## Usage

1. **Initial Setup**: The application creates default roles and an admin user on startup (credentials configured in `.env`)

2. **Admin Access**: Login with admin credentials to access the admin panel for managing organizations, users, and system settings

3. **User Registration**: Users can register or be assigned to organizations by admins

4. **Document Management**:
   - Create categories to organize documents
   - Add folders within categories for further organization
   - Upload documents to categories or folders
   - Set permissions for viewing/editing documents

5. **File Operations**:
   - View supported document types directly in the browser
   - Download files securely
   - Track file synchronization status

## API Documentation

When the backend is running, API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
documents-app/
├── server/                 # FastAPI backend
│   ├── core/              # Core functionality (config, security, database)
│   ├── models/            # SQLAlchemy models
│   ├── routes/            # API route handlers
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic services
│   ├── repositories/      # Data access layer
│   └── main.py            # Application entry point
├── client/                # React frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom React hooks
│   │   └── utils/         # Utility functions
│   ├── public/            # Static assets
│   └── package.json
└── README.md
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
