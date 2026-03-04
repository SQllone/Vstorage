# VStorage - Warehouse Management System
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
## API Endpoints

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

