# sweepKart — Premium E-Commerce Store

**sweepKart** is a full-featured, modern Django e-commerce platform built as part of the **CodeAlpha** Web Development Internship roadmap. It features a dark-themed glassmorphism visual interface, full shopping cart mechanics, atomic checkout processing, customer account management, and a comprehensive Django Admin portal.

---

## Key Features

### 🛒 Customer Storefront
- **Flipkart-Inspired Modern Light UI**: Clean white product cards, blue header banner, yellow star rating badges, and orange primary action buttons.
- **Product Reviews & Star Rating System**: Verified buyer review cards, star ratings (1–5 ★), average rating calculations, and interactive customer review submission.
- **AJAX Cart & Floating Toast Notifications**: Asynchronous add-to-cart fetch submissions (`fetch('/cart/add/...')`), floating glassmorphic toast notification in bottom-right corner ("✓ Added to cart!"), and animated navbar cart badge counter bounce.
- **Downloadable PDF Invoices**: Instant ReportLab PDF tax invoice generation for completed orders with tabular itemized breakdown, shipping info, and order timestamp.
- **Product Browsing & Search**: Real-time category filtering, search keyword query, and price range filtering.
- **Shopping Cart System**: Session-based cart that automatically merges with user account upon login.
- **Atomic Checkout & Order Confirmation**: Transactional checkout with row-locking (`select_for_update()`) that validates stock limits, decrements inventory, and records order invoices.
- **Order History**: User dashboard tracking past order status (`Pending`, `Processing`, `Shipped`, `Completed`, `Cancelled`).

### ⚙️ Admin Management Portal
- **Inventory & Stock CRUD**: Inline price and stock editing (`list_editable`), active status toggles, and auto-generated slug fields.
- **Category & Review Management**: Product category management and moderation of customer reviews.
- **Order Lifecycle Fulfillment**: Update order statuses and inspect inline order items (`OrderItemInline`).

---

## Tech Stack

- **Backend**: Python 3.x, Django 6.1
- **PDF Generation**: ReportLab 5.0
- **Database**: SQLite3 (with atomic transactions & row locking)
- **Image Processing**: Pillow
- **Frontend**: HTML5, Bootstrap 5 CDN, Custom Vanilla CSS (`main.css`), Vanilla JS (`main.js`)
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
