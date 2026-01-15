# 🎯 Code Review System

A full-stack automated code review platform built with React, FastAPI, and PostgreSQL. Submit code, get instant feedback, track your progress, and improve your coding skills!

![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-Frontend-61dafb)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-316192)

## ✨ Features

- 🔐 **User Authentication** - Secure registration and login system
- 📝 **Code Submission** - Submit code in multiple programming languages
- 🤖 **Automated Feedback** - Get instant AI-powered code reviews
- 📊 **Analytics Dashboard** - Track your coding progress and statistics
- 🔔 **Real-time Notifications** - Stay updated on review status
- 📈 **Student Progress Tracking** - Monitor improvement over time

## 🚀 Quick Start (Using Docker)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Installation

1. **Create a `docker-compose.yml` file** with the following content:

```yaml
services:
  db:
    image: postgres:15-alpine
    container_name: code_review_db
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: pass12345
      POSTGRES_DB: code_review_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - app-network

  backend:
    image: amansingh3413/code-review-system-backend:latest
    container_name: code_review_backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:pass12345@db:5432/code_review_db
      SECRET_KEY: change-this-secret-key-in-production
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 30
    depends_on:
      - db
    networks:
      - app-network

  frontend:
    image: amansingh3413/code-review-system-frontend:latest
    container_name: code_review_frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    networks:
      - app-network
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

2. **Run the application:**

```bash
docker-compose up -d
```

3. **Access the application:**

- 🌐 **Frontend**: [http://localhost:3000](http://localhost:3000)
- 🔌 **Backend API**: [http://localhost:8000](http://localhost:8000)
- 📖 **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🛠️ Tech Stack

### Frontend
- **React** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

### Backend
- **FastAPI** - Python web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Uvicorn** - ASGI server

### Database
- **PostgreSQL 15** - Relational database

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Frontend web server

## 📖 Usage

### First Time Setup

1. **Register a new account:**
   - Navigate to http://localhost:3000
   - Click "Register"
   - Fill in your details

2. **Login:**
   - Use your credentials to log in

3. **Submit Code:**
   - Go to the submission page
   - Paste your code
   - Select the programming language
   - Submit for review

4. **View Results:**
   - Check your dashboard for feedback
   - View analytics and progress

## 🎮 Docker Commands

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Stop and remove all data (fresh start)
docker-compose down -v

# Restart a specific service
docker-compose restart backend

# Check running containers
docker-compose ps
```

## 🔧 Configuration

### Environment Variables

You can customize the application by modifying environment variables in `docker-compose.yml`:

```yaml
environment:
  DATABASE_URL: postgresql://postgres:pass12345@db:5432/code_review_db
  SECRET_KEY: your-super-secret-key-here  # Change this!
  ALGORITHM: HS256
  ACCESS_TOKEN_EXPIRE_MINUTES: 30
```

⚠️ **Important**: Change the `SECRET_KEY` before deploying to production!

### Ports

Default ports:
- Frontend: `3000`
- Backend: `8000`
- Database: `5432`

To change ports, modify the `docker-compose.yml`:

```yaml
ports:
  - "YOUR_PORT:80"  # Frontend
  - "YOUR_PORT:8000"  # Backend
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find and kill the process using the port
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:3000 | xargs kill -9
```

### Database Connection Issues
```bash
# Check if database is running
docker-compose ps

# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db
```

### Fresh Start
```bash
# Remove everything and start fresh
docker-compose down -v
docker-compose up -d
```

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/submissions` - Submit code for review
- `GET /api/submissions` - Get user submissions
- `GET /api/analytics/student` - Get student analytics
- `GET /api/notifications` - Get notifications

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Author

**Aman Singh**
- GitHub: [@amansingh3413](https://github.com/amansingh3413)
- Docker Hub: [amansingh3413](https://hub.docker.com/u/amansingh3413)

## 🌟 Show Your Support

Give a ⭐️ if this project helped you!

## 📞 Support

If you have any questions or run into issues:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Open an issue on GitHub
3. Check the API documentation at http://localhost:8000/docs

---

**Made with ❤️ by Aman Singh**