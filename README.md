# Pharmacy Management System

**Author:** Sonam Bamotra  
**Course:** B.Tech in Computer Science & Engineering (Cybersecurity)  
**Institution:** Model Institute of Engineering & Technology (Autonomous)  
**Semester:** 7th Semester  
**Project Type:** Summer School Internship Project at TechnoSolutions, Jammu (End of 6th Semester)  

---

## 📌 Project Overview
The **Pharmacy Management System** is a desktop software application designed to streamline and automate daily pharmacy operations. It provides an intuitive graphical interface for pharmacists to efficiently manage medicine inventory, track stock levels, record customer sales, and generate real-time analytical reports.

This project was developed as part of a summer internship, focusing on building a robust, lightweight, and secure application that runs natively on Linux systems (specifically tested on Kali Linux) without relying on heavy third-party libraries.

## ✨ Features
- **Role-Based Authentication:** Secure login system for staff and administrators using SHA-256 password hashing.
- **Inventory Management:** Add, view, delete, and search for medicines. Track batch numbers, expiry dates, and stock levels.
- **Low Stock Alerts:** Automatic visual warnings (row highlighting) and alerts for medicines that need restocking.
- **Sales Processing:** Transactional sales recording that automatically deducts stock and logs the customer details.
- **Analytics & Reports:** Real-time KPI dashboard (Total Revenue, Sales Count, etc.) and interactive bar charts for top-selling medicines and daily revenue.
- **Zero Dependencies:** Built entirely using the Python Standard Library (Tkinter, SQLite3, hashlib) for maximum performance, portability, and zero setup delays.

## 🛠️ Technology Stack
- **Language:** Python 3
- **GUI Framework:** Tkinter (Standard Library)
- **Database:** SQLite3 (Standard Library)
- **Security:** SHA-256 Hashing (`hashlib` module)

## 📂 Project Structure
```text
PharmacyManagementSystem/
├── assets/                 # Static assets (icons, images)
├── database/
│   ├── __init__.py
│   ├── db_setup.py         # Database schema and initialization
│   └── pharmacy.db         # SQLite database (auto-generated at runtime)
├── modules/
│   ├── __init__.py
│   ├── auth.py             # Login and password hashing
│   ├── chart.py            # Custom Tkinter Canvas bar chart
│   ├── inventory.py        # Medicine CRUD operations
│   ├── reports.py          # Analytics and KPI generation
│   └── sales.py            # Sales recording and stock deduction
├── main.py                 # Main application entry point
├── requirements.txt        # Project dependencies (None required)
└── README.md               # Project documentation
