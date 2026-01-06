# 📁 DOT SHOP Project Structure

```
control/
├── backend/                    # FastAPI Backend
│   ├── api/
│   │   └── routes/            # API endpoints
│   │       ├── products.py    # Product APIs
│   │       ├── orders.py      # Order management
│   │       ├── users.py       # User authentication
│   │       ├── platforms.py   # Platform info
│   │       └── dashboard.py   # Analytics
│   ├── core/
│   │   ├── config.py          # Settings
│   │   ├── database.py        # DB connection
│   │   └── security.py        # Auth & JWT
│   ├── integrations/          # Platform integrations
│   │   ├── base.py           # Base platform class
│   │   ├── digikala.py       # Digikala scraper
│   │   ├── mihanstore.py     # Mihanstore scraper
│   │   └── torob.py          # Torob price comparison
│   ├── models/               # Database models
│   │   ├── product.py        # Product & Category
│   │   ├── order.py          # Order & OrderItem
│   │   └── user.py           # User & Address
│   ├── services/
│   │   └── platform_selector.py  # Smart platform selection
│   ├── main.py               # FastAPI app entry
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                  # Next.js Frontend
│   ├── app/
│   │   ├── layout.tsx        # Root layout (RTL)
│   │   ├── page.tsx          # Home page
│   │   └── globals.css       # Global styles
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   └── tailwind.config.js
│
├── telegram-bot/             # Telegram Bot
│   ├── bot.py               # Main bot logic
│   ├── Dockerfile
│   └── requirements.txt
│
├── database/                # Database initialization
│   └── init.sql            # Initial schema & data
│
├── scripts/                 # Utility scripts
│   ├── import_digikala.py  # Import from Digikala
│   └── import_mihanstore.py # Import from Mihanstore
│
├── docs/                    # Documentation
│   ├── API.md              # API documentation
│   └── DEPLOYMENT.md       # Deployment guide
│
├── config/                  # Configuration files
│   └── .env.example        # Environment template
│
├── docker-compose.yml      # Docker orchestration
├── README.md              # Main documentation
└── .gitignore
```

## Key Components

### Backend (FastAPI)
- **Purpose**: REST API for all operations
- **Port**: 8000
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Cache**: Redis
- **Features**:
  - Multi-platform product search
  - Smart commission-based selection
  - Order management
  - User authentication (JWT)
  - Admin dashboard analytics

### Frontend (Next.js 14)
- **Purpose**: Web interface for customers
- **Port**: 3000
- **Features**:
  - RTL Persian UI
  - Product browsing
  - Shopping cart
  - Order tracking
  - Responsive design

### Telegram Bot
- **Purpose**: Shopping via Telegram
- **Features**:
  - Product search
  - Price comparison
  - Order placement
  - Order tracking
  - Admin notifications

### Platform Integrations
- **Digikala**: 9-20% commission
- **Mihanstore**: 30-50% commission (best for fashion)
- **Torob**: Price comparison
- **Extendable**: Easy to add more platforms

## Database Schema

### Main Tables
1. **users** - Customer & admin accounts
2. **products** - Product catalog
3. **categories** - Product categorization
4. **orders** - Order information
5. **order_items** - Order line items
6. **addresses** - Shipping addresses

## Services Flow

```
User Request
    ↓
Frontend/Bot/API
    ↓
Backend (FastAPI)
    ↓
Platform Selector
    ↓
[Digikala | Mihanstore | Torob | ...]
    ↓
Compare Prices & Commissions
    ↓
Select Best Platform
    ↓
Return to User
```

## Development Workflow

1. **Local Development**:
   ```bash
   docker-compose up -d
   ```

2. **Add New Platform**:
   - Create new file in `backend/integrations/`
   - Extend `BasePlatform` class
   - Add to `PlatformSelector`

3. **Add New API Endpoint**:
   - Create route in `backend/api/routes/`
   - Add to router in `backend/main.py`

4. **Database Changes**:
   - Update models in `backend/models/`
   - Create migration (if using Alembic)
   - Update `database/init.sql`

## Environment Variables

See `config/.env.example` for all required configuration.

## Deployment

See `docs/DEPLOYMENT.md` for complete deployment instructions.
