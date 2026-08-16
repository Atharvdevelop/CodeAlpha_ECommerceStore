# sweepKart — Premium E-Commerce Store

**sweepKart** is a full-featured, modern Django e-commerce platform built as part of the **CodeAlpha** Web Development Internship roadmap. It features a dark-themed glassmorphism visual interface, full shopping cart mechanics, atomic checkout processing, customer account management, and a comprehensive Django Admin portal.

---

## Key Features

### 🛒 Customer Storefront
- **Responsive Dark Theme UI**: Custom CSS glassmorphism cards, glowing indigo gradients, and cyan price highlights.
- **Product Browsing & Search**: Real-time category filtering, search keyword query, and price range filtering.
- **Product Details & Stock Badges**: Detailed views with stock availability badges, high-res images, and SVG fallback placeholders.
- **Shopping Cart System**: Session-based cart that automatically merges with user account upon login.
- **Atomic Checkout & Order Confirmation**: Transactional checkout that validates stock limits, decrements inventory, and generates order invoices.
- **Order History**: User dashboard tracking past order status (`Pending`, `Processing`, `Shipped`, `Completed`, `Cancelled`).
- **User Authentication**: Built-in Django authentication (`UserCreationForm`, `AuthenticationForm`).

### ⚙️ Admin Management Portal
- **Inventory & Stock CRUD**: Inline price and stock editing (`list_editable`), active status toggles, and auto-generated slug fields.
- **Category Management**: Organized product categorization with product counts.
- **Order Lifecycle Fulfillment**: Update order statuses and inspect inline order items (`OrderItemInline`).
- **Advanced Filtering**: Search by customer username, order ID, or address; filter products by category and stock availability.

---

## Tech Stack

- **Backend**: Python 3.x, Django 6.1
- **Database**: SQLite3 (with atomic transactions)
- **Image Processing**: Pillow
- **Frontend**: HTML5, Bootstrap 5 CDN, Custom Vanilla CSS (`main.css`)
- **Icons & Typography**: Bootstrap Icons, Inter Font (Google Fonts)

---

## Project Structure

```
CodeAlpha_ECommerceStore/
├── config/
│   ├── settings.py         # Django settings, INSTALLED_APPS, Media/Static configs
│   ├── urls.py             # Root URL routing & media asset serving
│   ├── wsgi.py
│   └── asgi.py
├── store/
│   ├── migrations/         # Database migrations
│   ├── templates/store/    # Glassmorphism HTML templates
│   │   ├── base.html       # Base layout with navbar, messages, footer
│   │   ├── home.html       # Product catalog, hero banner, filters
│   │   ├── product_detail.html
│   │   ├── cart.html       # Shopping cart overview
│   │   ├── checkout.html   # Shipping form & checkout
│   │   ├── order_confirm.html # Invoice summary
│   │   ├── order_history.html # Past orders list
│   │   └── auth/           # Login & Register views
│   ├── admin.py            # Custom Django Admin portal registration
│   ├── forms.py            # Registration, Login, and Checkout forms
│   ├── models.py           # Category, Product, Cart, CartItem, Order, OrderItem
│   ├── tests.py            # Automated test suite (5 passing unit tests)
│   ├── urls.py             # App URL routes
│   └── views.py            # Business logic, cart merging, order placement
├── static/
│   └── css/main.css        # Glassmorphism styling, radial glow, cyan prices
├── media/
│   └── products/           # Product image uploads
├── db.sqlite3              # SQLite database
├── manage.py               # Django CLI utility
├── requirements.txt        # Frozen dependencies
└── README.md               # Project documentation
```

---

## Quick Start Setup Instructions

### 1. Clone & Navigate to Repository
```bash
git clone https://github.com/YourUsername/CodeAlpha_ECommerceStore.git
cd CodeAlpha_ECommerceStore
```

### 2. Set Up Virtual Environment & Install Dependencies
```bash
# Windows
python -m venv venv
venv\Scripts\activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Run Database Migrations & Seed Sample Data
```bash
python manage.py makemigrations store
python manage.py migrate
python scratch_seed.py
```

### 4. Start Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to:
- **Storefront**: `http://127.0.0.1:8000/`
- **Admin Panel**: `http://127.0.0.1:8000/admin/`

---

## Default Credentials (from Seed Script)

| Account Type | Username | Password | Access Level |
|---|---|---|---|
| **Admin Superuser** | `admin` | `admin123` | Full Admin Portal Access |
| **Demo Customer** | `demo` | `demo123` | Storefront & Checkout Access |

---

## Running Automated Tests

Run the Django unit test suite with:
```bash
python manage.py test store
```

---

## CodeAlpha Submission Deliverables

- [x] Local & remote GitHub repository: `CodeAlpha_ECommerceStore`
- [x] Environment & requirements frozen: `requirements.txt`
- [x] Database models: `Category`, `Product`, `Cart`, `CartItem`, `Order`, `OrderItem`
- [x] Admin panel setup with custom list displays, filters, inline orders
- [x] Auth views & session cart association
- [x] Responsive dark theme glassmorphism UI with cyan prices & gradient buttons
- [x] Cart CRUD & atomic checkout stock deduction
- [x] Unit test suite verified (5 passing tests)
- [x] Comprehensive `README.md` documentation
