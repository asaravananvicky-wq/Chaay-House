# Chaay House — Full-Stack Tea Shop Web Application

A production-style, full-stack e-commerce web application for a premium tea shop, built with Django, Django REST Framework, and MySQL (SQLite for zero-config local development).

![Status](https://img.shields.io/badge/status-portfolio--ready-1F4D3A)

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Screenshots](#screenshots)
5. [Project Structure](#project-structure)
6. [Installation](#installation)
7. [Database Setup](#database-setup)
8. [Running the Server](#running-the-server)
9. [Admin / Dashboard Access](#admin--dashboard-access)
10. [REST API](#rest-api)
11. [Running Tests](#running-tests)
12. [Deployment](#deployment)
13. [Future Improvements](#future-improvements)

---

## Overview

Chaay House is a fictional premium tea brand. This project implements a complete customer-facing storefront (browse, search, cart, checkout, order tracking) plus a separate staff-only admin dashboard (product/category/order/customer management with sales stats and charts), backed by a relational database and a documented REST API.

## Features

**Customer-facing**
- Home, Menu (search/filter/sort/pagination), Product Detail, Cart, Checkout, Order Confirmation
- Registration, Login/Logout, Profile management, Order history & order detail
- Contact form
- Cash on Delivery / Pay at Shop checkout flow
- Fully responsive (desktop, tablet, mobile)

**Admin dashboard** (`/dashboard/`, staff accounts only)
- Overview: total orders, today's orders, total customers, total products, total sales, 7-day order chart, popular products chart, recent orders
- Product management: add / edit / delete / enable-disable / image upload / stock
- Category management: add / delete
- Order management: search, filter by status, view details, update status
- Customer list

**REST API** (`/api/`) — see [REST API](#rest-api) below.

## Tech Stack

- **Backend:** Python 3, Django 6, Django REST Framework, django-filter
- **Database:** MySQL (via PyMySQL, no compiled drivers needed) — SQLite by default for local dev
- **Frontend:** HTML5, CSS3 (custom tea-themed design system), Bootstrap 5, Font Awesome, Chart.js
- **Auth:** Django's built-in auth system (hashed passwords, sessions), role-based access via `is_staff`
- **Dev tools:** Python venv, Git

## Screenshots

_Add screenshots of the Home page, Menu page, Cart, Checkout, and Dashboard here once you run the app locally._

## Project Structure

```
tea_shop/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── config/                  # Project settings & root URLs
│   ├── settings.py
│   ├── urls.py
│   ├── api_urls.py          # /api/ routes
│   ├── views_errors.py      # 404/403/500 handlers
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                 # Registration, login, profile, order history
│   ├── models.py             # CustomerProfile
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── products/                  # Catalog
│   ├── models.py              # Category, Product, Review
│   ├── views.py                # home, menu, product detail
│   ├── serializers.py / api_views.py   # REST API
│   ├── context_processors.py   # nav category list
│   └── management/commands/seed_shop.py  # sample data
│
├── cart/                      # Shopping cart (DB-backed, per logged-in user)
│   ├── models.py               # Cart, CartItem
│   ├── views.py
│   ├── serializers.py / api_views.py
│   └── context_processors.py   # navbar cart badge count
│
├── orders/                    # Checkout & order lifecycle
│   ├── models.py               # Order, OrderItem, status workflow
│   ├── forms.py / views.py
│   └── serializers.py / api_views.py
│
├── contact/                   # Contact form + stored messages
│
├── dashboard/                 # Staff-only admin dashboard (separate from /django-admin/)
│   ├── views.py
│   ├── forms.py
│   └── decorators.py           # staff_required
│
├── templates/
│   ├── base.html
│   ├── partials/ (navbar, footer, product_card)
│   ├── products/, cart/, orders/, accounts/, contact/, dashboard/
│   └── errors/ (404, 403, 500)
│
├── static/
│   ├── css/theme.css           # Tea-inspired design system
│   └── js/main.js
│
└── media/                     # Uploaded product images
```

## Installation

### 1. Prerequisites
- Python 3.10+
- pip
- (Optional, for production DB) MySQL Server 8+

### 2. Clone & set up a virtual environment

```bash
git clone <your-repo-url> tea_shop
cd tea_shop
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set a real `SECRET_KEY`. For local development you can leave `DB_ENGINE=sqlite` — the app will just work with zero database setup.

## Database Setup

### Option A — SQLite (default, zero config)
Nothing to do. `DB_ENGINE=sqlite` in `.env` is already the default.

### Option B — MySQL (production-style)
1. Create a database and user in MySQL:
   ```sql
   CREATE DATABASE tea_shop CHARACTER SET utf8mb4;
   CREATE USER 'tea_shop_user'@'localhost' IDENTIFIED BY 'your-password';
   GRANT ALL PRIVILEGES ON tea_shop.* TO 'tea_shop_user'@'localhost';
   FLUSH PRIVILEGES;
   ```
2. In `.env`, set:
   ```
   DB_ENGINE=mysql
   DB_NAME=tea_shop
   DB_USER=tea_shop_user
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=3306
   ```

### Apply migrations

```bash
python manage.py migrate
```

### Create an admin (staff) account

```bash
python manage.py createsuperuser
```

### (Optional) Seed sample categories & products

```bash
python manage.py seed_shop
```

This adds 7 categories (Tea, Coffee, Milkshakes, Snacks, Biscuits, Cool Drinks, Combos) and 18 sample products so the storefront isn't empty on first run.

## Running the Server

```bash
python manage.py collectstatic --noinput   # only needed once DEBUG=False
python manage.py runserver
```

Visit:
- Storefront: http://127.0.0.1:8000/
- Django built-in admin: http://127.0.0.1:8000/django-admin/
- Staff dashboard: http://127.0.0.1:8000/dashboard/ (requires an `is_staff` account)
- REST API root: http://127.0.0.1:8000/api/

## Admin / Dashboard Access

Any user with `is_staff=True` (e.g. the superuser you created) can log in through the normal `/accounts/login/` page and will see a "Dashboard" link in the navbar, or can go directly to `/dashboard/`.

## REST API

Base path: `/api/`

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/products/` | List products (filter by `category__slug`, `is_available`, `is_bestseller`; search via `?search=`) | Public |
| GET | `/api/products/<id>/` | Product detail | Public |
| POST/PUT/DELETE | `/api/products/<id>/` | Manage products | Staff only |
| GET | `/api/categories/` | List categories | Public |
| POST/PUT/DELETE | `/api/categories/<id>/` | Manage categories | Staff only |
| GET | `/api/cart/` | Current user's cart | Logged-in |
| POST | `/api/cart/items/` | Add item to cart (`product_id`, `quantity`) | Logged-in |
| PATCH | `/api/cart/items/<id>/` | Update quantity | Logged-in (owner) |
| DELETE | `/api/cart/items/<id>/` | Remove item | Logged-in (owner) |
| GET | `/api/orders/` | Current user's orders | Logged-in |
| POST | `/api/orders/` | Create order from current cart | Logged-in |
| GET | `/api/orders/<id>/` | Order detail | Logged-in (owner or staff) |
| GET | `/api/admin/orders/` | All orders (filter by `?status=`) | Staff only |
| PATCH | `/api/admin/orders/<id>/status/` | Update order status | Staff only |
| \* | `/api/auth/` | DRF browsable-API login/logout | — |

All endpoints use Django's session authentication, so log in via the website first (or via `/api/auth/login/`) before calling authenticated endpoints from a browser or a tool like Postman with cookies enabled.

## Running Tests

```bash
python manage.py test accounts products cart orders
```

Covers: registration (success/validation failure), login (success/failure), product listing/search/availability, cart add/update/remove and login-required guard, checkout (order creation, empty-cart guard, default status), and dashboard staff-only access control.

## Deployment

This project is deployment-ready in structure, though you'll need to provision infrastructure yourself:

1. Set `DEBUG=False` and a real `SECRET_KEY` and `ALLOWED_HOSTS` in `.env`.
2. Switch `DB_ENGINE=mysql` and point it at your production MySQL instance.
3. Run `python manage.py collectstatic --noinput` and serve `/staticfiles/` and `/media/` via Nginx (or a CDN/object storage for media in production).
4. Run the app with Gunicorn behind Nginx, e.g.:
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
   ```
5. Never commit `.env`, `db.sqlite3`, or `media/` uploads to git — `.gitignore` already excludes these.
6. Consider Docker/Nginx/HTTPS (via Let's Encrypt) for a full production setup — not included here to keep the codebase focused, but the environment-variable-driven settings make it straightforward to containerize.

## Future Improvements

- Real payment gateway integration (Razorpay/Stripe) alongside Cash on Delivery
- Guest checkout (currently requires an account)
- Product reviews submission UI (models exist; add a review form)
- Order status email/SMS notifications
- Wishlist / favorites
- Coupon codes and discounts
- Multi-image product galleries
- Full Docker Compose setup (Django + MySQL + Nginx)
- CI pipeline (GitHub Actions) running the test suite on push

---

Built as a full-stack portfolio project demonstrating Django, DRF, MySQL, responsive frontend design, REST API design, authentication, and testing.
