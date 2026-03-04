# VStorage - Warehouse Management System

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3+-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

VStorage is a comprehensive Warehouse Management System (WMS) built with FastAPI, providing complete functionality for managing inventory, suppliers, categories, and orders with JWT authentication.

## 🚀 Features

- **User Management**: Registration, authentication, and authorization with JWT tokens
- **Category Management**: Organize products into hierarchical categories
- **Supplier Management**: Manage supplier information and contacts
- **Product Management**: Complete CRUD operations for products with SKU tracking
- **Order Management**: Create and track supply/sale orders with detailed items
- **Inventory Tracking**: Real-time stock levels with minimum stock alerts
- **RESTful API**: Complete REST API with automatic documentation
- **Security**: JWT authentication, password hashing, and input validation
- **Testing**: Comprehensive test suite with pytest
- **Documentation**: Complete API documentation and user manual

## 📋 Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

## 🛠️ Installation

1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or using the Makefile:
   ```bash
   make install
   ```

3. **Start the application**:
   ```bash
   python main.py
   ```
   
   Or using the Makefile:
   ```bash
   make run
   ```

4. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## 📁 Project Structure

```
vstorage/
├── main.py                 # Application entry point
├── requirements.txt       # Python dependencies
├── Makefile              # Development commands
├── README.md             # This file
├── vstorage.db           # SQLite database (auto-created)
├── app/                  # Main application package
│   ├── __init__.py
│   ├── database/         # Database configuration
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── routers/         # API endpoints
│   └── auth/            # Authentication utilities
├── tests/               # Test suite
│   ├── __init__.py
│   ├── test_api.py      # Comprehensive API tests
│   └── test_simple.py   # Simple functionality tests
├── scripts/              # Utility scripts
│   ├── clean_database.py    # Database cleanup
│   ├── demo.py              # API demonstration
│   └── security_audit.py    # Security analysis
├── docs/                 # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── USER_MANUAL.md
│   └── TECHNICAL_DOCS.md
└── config/               # Configuration files
    ├── .env.example
    └── pytest.ini
```

## 🎯 Quick Start

### 1. Start the Application
```bash
python main.py
```

### 2. Test the API
```bash
python tests/test_simple.py
```

### 3. Run Full Demonstration
```bash
python scripts/demo.py
```

### 4. Run Security Audit
```bash
python scripts/security_audit.py
```

## 🔐 Authentication

1. **Register a user**:
   ```bash
   curl -X POST "http://localhost:8000/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
          "username": "admin",
          "email": "admin@example.com",
          "full_name": "Admin User",
          "password": "123456"
        }'
   ```

2. **Login to get JWT token**:
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
        -H "Content-Type: application/json" \
        -d '{
          "username": "admin",
          "password": "123456"
        }'
   ```

3. **Use the token** in subsequent requests:
   ```bash
   curl -X GET "http://localhost:8000/categories/" \
        -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```

## 📊 API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/auth/register` | POST | Register new user | No |
| `/auth/login` | POST | User login | No |
| `/auth/me` | GET | Get current user | Yes |
| `/categories/` | GET/POST | List/Create categories | Yes |
| `/categories/{id}` | GET/PATCH/DELETE | Category operations | Yes |
| `/suppliers/` | GET/POST | List/Create suppliers | Yes |
| `/suppliers/{id}` | GET/PATCH/DELETE | Supplier operations | Yes |
| `/products/` | GET/POST | List/Create products | Yes |
| `/products/{id}` | GET/PATCH/DELETE | Product operations | Yes |
| `/products/low-stock/` | GET | Get low stock products | Yes |
| `/orders/` | GET/POST | List/Create orders | Yes |
| `/orders/{id}` | GET/PATCH/DELETE | Order operations | Yes |
| `/orders/stats/` | GET | Get order statistics | Yes |
| `/users/` | GET | List users | Yes (Admin) |
| `/health` | GET | Health check | No |

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Simple API Test
```bash
python tests/test_simple.py
```

### Run Comprehensive Tests
```bash
python tests/test_api.py
```

### Using Makefile
```bash
make test        # All tests
make test-api   # API tests only
make demo       # Interactive demo
```

## 🔧 Development Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make run` | Start application |
| `make test` | Run all tests |
| `make demo` | Run API demonstration |
| `make clean` | Clean temporary files |
| `make reset-db` | Reset database |
| `make security` | Run security audit |
| `make status` | Check system status |

## 📖 Documentation

- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API reference
- **[User Manual](docs/USER_MANUAL.md)** - Step-by-step user guide
- **[Technical Documentation](docs/TECHNICAL_DOCS.md)** - Architecture and implementation details

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt with salt for password security
- **Input Validation**: Pydantic models for data validation
- **SQL Injection Protection**: ORM prevents SQL injection
- **Authorization**: Role-based access control
- **Error Handling**: Secure error responses without information leakage

## 🏗️ Architecture

- **Backend**: FastAPI (Python 3.12+)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens with HTTPBearer
- **Validation**: Pydantic models
- **Documentation**: Automatic with FastAPI
- **Testing**: pytest with comprehensive test coverage

## 📝 Coursework Requirements

This project fulfills all requirements for a modern warehouse management system:

✅ **User Management**: Registration, authentication, authorization  
✅ **Data Models**: Products, categories, suppliers, orders  
✅ **CRUD Operations**: Create, Read, Update, Delete for all entities  
✅ **Relationships**: Proper foreign key relationships between entities  
✅ **Validation**: Input validation and business rules  
✅ **Security**: JWT authentication and password hashing  
✅ **API Design**: RESTful API with proper HTTP methods  
✅ **Documentation**: Complete API documentation  
✅ **Testing**: Comprehensive test suite  
✅ **Error Handling**: Proper error responses and logging  

## 🚀 Production Deployment

For production deployment:

1. **Environment Variables**:
   ```bash
   export SECRET_KEY="your-super-secret-key"
   export DATABASE_URL="postgresql://user:pass@localhost/db"
   export ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

2. **Database**: Migrate to PostgreSQL or MySQL
3. **Security**: Enable HTTPS, configure CORS, set up rate limiting
4. **Monitoring**: Add logging and monitoring
5. **Container**: Use Docker for deployment

## 🤝 Contributing

This is a coursework project. For improvements:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is created for educational purposes as part of a coursework assignment.

## 🆘 Support

If you encounter issues:

1. Check the [User Manual](docs/USER_MANUAL.md)
2. Run the [Security Audit](scripts/security_audit.py)
3. Check the [API Documentation](http://localhost:8000/docs)
4. Run tests: `python tests/test_simple.py`

---

**VStorage** - Professional Warehouse Management System for Coursework