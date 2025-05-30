# Examples and Workflows

This guide provides practical examples and common workflows for using SingleAgent effectively. Learn through real-world scenarios and step-by-step tutorials.

## Getting Started Examples

### Basic Project Setup

**Scenario**: Setting up a new Python web application with authentication.

```bash
# Start SingleAgent
python main.py

# User interaction
User: "I want to create a Flask web application with user authentication"

# Architect Agent Response
Architect: "I'll help you design a Flask application with authentication. Let me create the project structure and plan the implementation."

# The system creates:
# - Project directory structure
# - Requirements file
# - Basic Flask application
# - Authentication blueprints
# - Database models
```

**Resulting Project Structure**:
```
my_flask_app/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   └── main/
│       ├── __init__.py
│       └── routes.py
├── migrations/
├── tests/
├── config.py
├── requirements.txt
└── run.py
```

### Code Implementation Workflow

**Scenario**: Implementing a specific feature with the Code Agent.

```bash
User: "Implement JWT-based authentication for the login endpoint"

# Code Agent Response
Code Agent: "I'll implement JWT authentication for your login endpoint. Let me create the necessary code."
```

The Code Agent creates:

1. **Authentication Service** (`app/services/auth_service.py`):
```python
import jwt
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from app.models.user import User

class AuthService:
    def __init__(self, secret_key):
        self.secret_key = secret_key
    
    def authenticate_user(self, email, password):
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            return self.generate_token(user)
        return None
    
    def generate_token(self, user):
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
```

2. **Login Route** (`app/auth/routes.py`):
```python
from flask import request, jsonify
from app.auth import bp
from app.services.auth_service import AuthService

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    auth_service = AuthService(current_app.config['SECRET_KEY'])
    token = auth_service.authenticate_user(email, password)
    
    if token:
        return jsonify({'token': token}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
```

3. **Tests** (`tests/test_auth.py`):
```python
import pytest
from app import create_app
from app.models.user import User

def test_login_success(client):
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'token' in response.json

def test_login_invalid_credentials(client):
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert 'error' in response.json
```

## Advanced Workflows

### Multi-Agent Collaboration

**Scenario**: Building a complex feature that requires both architectural planning and implementation.

```bash
User: "I need to add a real-time chat feature to my web application"

# Architect Agent starts
Architect: "I'll design the real-time chat architecture. This will require WebSocket connections, message persistence, and room management."
```

**Phase 1: Architecture Planning**
```bash
Architect: "Here's the proposed architecture:

1. WebSocket server using Flask-SocketIO
2. Message storage with Redis for real-time features
3. Database persistence for chat history
4. Room-based chat organization
5. User presence tracking

Let me create the system design and hand over to the Code Agent for implementation."
```

**Phase 2: Implementation**
```bash
# Automatic handoff to Code Agent
Code Agent: "I'll implement the chat feature based on the architecture design. Starting with the WebSocket server setup."
```

The Code Agent implements:

1. **WebSocket Configuration**:
```python
# app/__init__.py
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    socketio.init_app(app, cors_allowed_origins="*")
    return app
```

2. **Chat Events Handler**:
```python
# app/chat/events.py
from flask_socketio import emit, join_room, leave_room
from app import socketio
from app.models.message import Message

@socketio.on('join_room')
def handle_join_room(data):
    room = data['room']
    username = data['username']
    join_room(room)
    emit('user_joined', {'username': username}, room=room)

@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    message = data['message']
    username = data['username']
    
    # Save to database
    msg = Message(content=message, username=username, room=room)
    msg.save()
    
    # Broadcast to room
    emit('new_message', {
        'message': message,
        'username': username,
        'timestamp': msg.timestamp.isoformat()
    }, room=room)
```

### API Development Workflow

**Scenario**: Creating a RESTful API with proper documentation and testing.

```bash
User: "Create a RESTful API for a task management system"

# Architect Agent designs the API structure
Architect: "I'll design a RESTful API for task management with the following endpoints:

- GET /api/tasks - List all tasks
- POST /api/tasks - Create new task
- GET /api/tasks/{id} - Get specific task
- PUT /api/tasks/{id} - Update task
- DELETE /api/tasks/{id} - Delete task

The API will include proper error handling, validation, and documentation."
```

**Implementation by Code Agent**:

1. **Task Model** (`app/models/task.py`):
```python
from app import db
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
```

2. **API Routes** (`app/api/tasks.py`):
```python
from flask import Blueprint, request, jsonify
from app.models.task import Task
from app import db

bp = Blueprint('tasks', __name__)

@bp.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])

@bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    task = Task(
        title=data['title'],
        description=data.get('description', '')
    )
    db.session.add(task)
    db.session.commit()
    
    return jsonify(task.to_dict()), 201

@bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())

@bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'completed' in data:
        task.completed = data['completed']
    
    db.session.commit()
    return jsonify(task.to_dict())

@bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return '', 204
```

3. **API Tests** (`tests/test_api.py`):
```python
import pytest
import json

def test_create_task(client):
    response = client.post('/api/tasks', 
        json={'title': 'Test Task', 'description': 'Test Description'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Test Task'

def test_get_tasks(client):
    response = client.get('/api/tasks')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_update_task(client):
    # Create task first
    create_response = client.post('/api/tasks', json={'title': 'Original Title'})
    task_id = create_response.get_json()['id']
    
    # Update task
    response = client.put(f'/api/tasks/{task_id}', 
        json={'title': 'Updated Title', 'completed': True})
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Updated Title'
    assert data['completed'] == True
```

### Database Migration Workflow

**Scenario**: Adding new features that require database changes.

```bash
User: "Add user profiles with avatar support to the existing user system"

# Architect Agent plans the database changes
Architect: "I'll design the user profile extension:

1. Create UserProfile model linked to User
2. Add avatar upload functionality
3. Create migration scripts
4. Update API endpoints

This requires careful database migration to preserve existing data."
```

**Migration Implementation**:

1. **New Profile Model** (`app/models/profile.py`):
```python
from app import db

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    bio = db.Column(db.Text)
    avatar_filename = db.Column(db.String(255))
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    
    user = db.relationship('User', backref=db.backref('profile', uselist=False))
```

2. **Migration Script** (`migrations/add_user_profiles.py`):
```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('user_profile',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('avatar_filename', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

def downgrade():
    op.drop_table('user_profile')
```

3. **Avatar Upload Service** (`app/services/upload_service.py`):
```python
import os
from werkzeug.utils import secure_filename
from PIL import Image

class UploadService:
    def __init__(self, upload_folder, allowed_extensions):
        self.upload_folder = upload_folder
        self.allowed_extensions = allowed_extensions
    
    def save_avatar(self, file, user_id):
        if not self.allowed_file(file.filename):
            raise ValueError("Invalid file type")
        
        filename = f"avatar_{user_id}_{secure_filename(file.filename)}"
        filepath = os.path.join(self.upload_folder, filename)
        
        # Resize and save image
        image = Image.open(file)
        image.thumbnail((200, 200))
        image.save(filepath)
        
        return filename
    
    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
```

## Testing Workflows

### Test-Driven Development

**Scenario**: Implementing a feature using TDD approach.

```bash
User: "Implement a password reset feature using test-driven development"

# Code Agent starts with tests
Code Agent: "I'll implement password reset using TDD. Starting with writing the tests first."
```

**Test First Approach**:

1. **Write Tests First** (`tests/test_password_reset.py`):
```python
import pytest
from app.services.password_reset_service import PasswordResetService

def test_generate_reset_token():
    service = PasswordResetService()
    token = service.generate_reset_token('user@example.com')
    assert token is not None
    assert len(token) == 64  # Expected token length

def test_validate_reset_token():
    service = PasswordResetService()
    token = service.generate_reset_token('user@example.com')
    is_valid = service.validate_reset_token(token, 'user@example.com')
    assert is_valid == True

def test_reset_password():
    service = PasswordResetService()
    token = service.generate_reset_token('user@example.com')
    result = service.reset_password(token, 'user@example.com', 'new_password')
    assert result == True
```

2. **Implement Service** (`app/services/password_reset_service.py`):
```python
import secrets
import hashlib
from datetime import datetime, timedelta
from app.models.user import User
from app import db

class PasswordResetService:
    def __init__(self):
        self.token_expiry_hours = 24
    
    def generate_reset_token(self, email):
        token = secrets.token_urlsafe(48)
        # Store token with expiry
        return token
    
    def validate_reset_token(self, token, email):
        # Validate token and check expiry
        return True
    
    def reset_password(self, token, email, new_password):
        if self.validate_reset_token(token, email):
            user = User.query.filter_by(email=email).first()
            user.set_password(new_password)
            db.session.commit()
            return True
        return False
```

### Integration Testing

**Scenario**: Testing the complete authentication flow.

```bash
User: "Create integration tests for the complete authentication system"

# Code Agent creates comprehensive integration tests
Code Agent: "I'll create integration tests that cover the entire authentication flow from registration to protected endpoint access."
```

**Integration Test Suite** (`tests/test_auth_integration.py`):
```python
import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_complete_auth_flow(client):
    # 1. Register new user
    registration_data = {
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }
    response = client.post('/auth/register', json=registration_data)
    assert response.status_code == 201
    
    # 2. Login with credentials
    login_data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    response = client.post('/auth/login', json=login_data)
    assert response.status_code == 200
    token = response.json['token']
    
    # 3. Access protected endpoint
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/api/profile', headers=headers)
    assert response.status_code == 200
    
    # 4. Test token expiry (mock time advancement)
    # 5. Test refresh token functionality
    # 6. Test logout
```

## Deployment Workflows

### Docker Deployment

**Scenario**: Preparing application for containerized deployment.

```bash
User: "Prepare my Flask application for Docker deployment"

# Architect Agent designs deployment strategy
Architect: "I'll create a Docker deployment setup with multi-stage builds, environment configuration, and production optimizations."
```

**Docker Configuration**:

1. **Dockerfile**:
```dockerfile
# Multi-stage build
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.9-slim

WORKDIR /app

# Copy dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make sure scripts are executable
RUN chmod +x boot.sh

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 5000

ENTRYPOINT ["./boot.sh"]
```

2. **Docker Compose** (`docker-compose.yml`):
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

3. **Boot Script** (`boot.sh`):
```bash
#!/bin/bash
set -e

# Wait for database
while ! nc -z db 5432; do
  echo "Waiting for database..."
  sleep 1
done

# Run migrations
flask db upgrade

# Start application
exec gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### CI/CD Pipeline

**Scenario**: Setting up automated testing and deployment.

```bash
User: "Set up CI/CD pipeline for automated testing and deployment"

# Code Agent creates GitHub Actions workflow
Code Agent: "I'll create a CI/CD pipeline using GitHub Actions with testing, security scanning, and automated deployment."
```

**GitHub Actions Workflow** (`.github/workflows/ci-cd.yml`):
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest --cov=app tests/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run security scan
      run: |
        pip install safety bandit
        safety check
        bandit -r app/

  deploy:
    needs: [test, security]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        # Deployment script here
        echo "Deploying to production..."
```

## Common Patterns and Best Practices

### Error Handling Pattern

```python
# Consistent error handling across the application
from functools import wraps
from flask import jsonify

def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            return jsonify({'error': 'Validation failed', 'details': str(e)}), 400
        except NotFoundError as e:
            return jsonify({'error': 'Resource not found'}), 404
        except Exception as e:
            # Log the error
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    return decorated_function
```

### Configuration Management Pattern

```python
# Environment-based configuration
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

### Service Layer Pattern

```python
# Service layer for business logic
class UserService:
    def __init__(self, user_repository, email_service):
        self.user_repository = user_repository
        self.email_service = email_service
    
    def create_user(self, email, password):
        # Validate input
        if not self._is_valid_email(email):
            raise ValidationError("Invalid email format")
        
        # Check if user exists
        if self.user_repository.find_by_email(email):
            raise ConflictError("User already exists")
        
        # Create user
        user = User(email=email)
        user.set_password(password)
        self.user_repository.save(user)
        
        # Send welcome email
        self.email_service.send_welcome_email(user.email)
        
        return user
```

---

*For more examples and advanced patterns, see [Tools Reference](tools.md) and [API Reference](api-reference.md).*
