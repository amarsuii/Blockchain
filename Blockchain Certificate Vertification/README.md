# Blockchain-Based Certificate Verification System for Online Learning Certificates

A complete, working, tamper-resistant web application for registering and verifying online course certificates (e.g., *Infosys Springboard* sample certificates) using **SHA-256 Cryptographic Hashing**, an **Ethereum-compatible Blockchain (Ganache)**, **Solidity Smart Contracts**, **Python Flask**, **SQLAlchemy ORM**, **Bootstrap 5**, and **QR Code generation**.

---

## 📌 Project Overview

Traditional online learning certificates are susceptible to tampering or forgery. This system establishes a tamper-proof verification architecture:
1. **Canonical Formatting & SHA-256 Hashing**: Certificate metadata (`student_id|certificate_id|course_name|issuer|completion_date`) is converted into a deterministic 256-bit hash.
2. **Blockchain Commitment**: The SHA-256 hash and unique Certificate ID are recorded on the Ethereum blockchain via a Solidity smart contract.
3. **Public & QR Code Verification**: Verifiers scan a QR code or enter a Certificate ID. The system recalculates the canonical SHA-256 digest and compares it directly against the immutable smart contract record on-chain.

---

## 🛠️ Technology Stack

* **Frontend**: HTML5, CSS3 (Vanilla CSS), JavaScript, Bootstrap 5, Bootstrap Icons, HTML5 QR Scanner
* **Backend**: Python 3.13, Flask, Flask-CORS, Flask Session Auth
* **Database**: MySQL with SQLAlchemy ORM (Automatic zero-config SQLite fallback for offline demo testing)
* **Blockchain**: Ethereum-compatible local testnet (Ganache GUI or `ganache-cli`), Solidity (`CertificateVerification.sol`), Web3.py
* **Cryptography**: SHA-256 (`hashlib`)
* **QR Code**: Python `qrcode` + `Pillow`

---

## 🏛️ System Architecture

```text
                    ┌─────────────────────┐
                    │      USER           │
                    │ Student / Verifier  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      FRONTEND       │
                    │ HTML/CSS/JS/Bootstrap│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     FLASK API       │
                    │      BACKEND        │
                    └──────┬────────┬─────┘
                           │        │
                  ┌────────┘        └─────────┐
                  ▼                           ▼
          ┌───────────────┐          ┌────────────────┐
          │     MySQL     │          │   Blockchain   │
          │   Database    │          │ Ethereum/      │
          │               │          │ Ganache        │
          └───────────────┘          └───────┬────────┘
                                             │
                                             ▼
                                    ┌────────────────┐
                                    │ Smart Contract │
                                    │    Solidity    │
                                    └────────────────┘
```

---

## 🚀 Installation & Setup Guide

### Step 1: Clone & Setup Environment

```bash
git clone <repository_url>
cd "Blockchain Certificate Vertification"

# Create virtual environment
python -m venv venv

# Activate Virtual Environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

---

### Step 2: Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Ensure `.env` contains:

```env
SECRET_KEY=blockchain_certificate_verification_secret_key_2026
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=cert_verification_db
BLOCKCHAIN_RPC_URL=http://127.0.0.1:7545
CONTRACT_ADDRESS=
BLOCKCHAIN_PRIVATE_KEY=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d
```

---

### Step 3: Start Local Blockchain Node & Deploy Smart Contract

You can start the local blockchain using **either** option below:

#### Option A: Project Built-in Simulator (Instant - No Downloads Required)
Run the included Python Ethereum simulator in a separate terminal:
```bash
python start_local_node.py
```

#### Option B: Ganache GUI
Open **Ganache GUI** and ensure server port is set to `7545`.

---

#### Deploy the Smart Contract:
In a new terminal window, run:
```bash
python blockchain/deploy.py
```
*This automatically deploys `CertificateVerification.sol` and updates `CONTRACT_ADDRESS` in `.env`.*

---

### Step 4: Setup Database & Seed Demo Data

```bash
# Initialize database tables and admin/student accounts
python setup_database.py

# Seed sample certificate (CERT001 / Infosys Springboard demo)
python seed_demo_data.py
```

---

### Step 5: Start the Flask Application

```bash
python run.py
```

Access the application in your browser:
* **Home / Public Verifier**: `http://localhost:5000`
* **Public Direct Verification**: `http://localhost:5000/verify/CERT001`
* **Admin Login**: `http://localhost:5000/login`

---

## 🔑 Demo Login Credentials

| Role | Email | Password |
|---|---|---|
| **Administrator** | `admin@certverify.org` | `admin123` |
| **Student** | `student@certverify.org` | `student123` |

---

## 🎬 Step-by-Step Demonstration Guide

### Demo 1: Admin Login
1. Navigate to `http://localhost:5000/login`.
2. Login with `admin@certverify.org` / `admin123`.
3. View Admin Dashboard displaying real-time metrics (Total Certs, Verified, Students, Verification Audit Logs).

### Demo 2: Register Certificate
1. Go to **Register Certificate** (`/admin/certificates/register`).
2. Fill out details:
   * **Student Name**: Demo Student
   * **Student ID**: STU001
   * **Certificate ID**: CERT002
   * **Course Name**: Cloud Computing
   * **Issuer**: Infosys Springboard
   * **Completion Date**: 2026-08-10
3. Observe the **Canonical String Preview**: `STU001|CERT002|Cloud Computing|Infosys Springboard|2026-08-10`.
4. Click **Submit & Register on Blockchain**.
5. The system generates SHA-256 hash, commits it to Ganache smart contract, stores transaction hash in MySQL, and creates a QR Code.

### Demo 3: Public Verification (Genuine Certificate)
1. Open `http://localhost:5000/verify` (or scan QR code).
2. Enter Certificate ID: `CERT001` or `CERT002`.
3. System recalculates canonical hash and compares it against on-chain smart contract record.
4. **Result**: `✓ CERTIFICATE VERIFIED` (Status: Match, Blockchain Status: Confirmed).

### Demo 4: Tampering & Hash Mismatch Demonstration
1. Open MySQL database (or SQLite `instance/cert_verification.db`) or modify certificate data in database manually (e.g. change course name to *Fake Course*).
2. Open `http://localhost:5000/verify/CERT001`.
3. System recalculates SHA-256 hash from database -> resulting in a different hash digest.
4. System compares newly calculated hash against immutable smart contract hash.
5. **Result**: `✕ VERIFICATION FAILED` ("The certificate information does not match the blockchain record. Data tampering detected!").

---

## 🧪 Automated Testing

Run unit & integration tests:

```bash
pytest tests/test_app.py
```

---

## 📁 Project Folder Structure

```text
Blockchain Certificate Vertification/
│
├── app.py                      # Flask Application Factory
├── config.py                   # Centralized Configuration & DB Fallbacks
├── requirements.txt            # Python Dependencies
├── .env                        # Environment Configuration
├── .env.example                # Sample Environment Template
├── setup_database.py           # Database Schema Setup Script
├── seed_demo_data.py           # Seed Script for Demo Certificates
├── run.py                      # Application Starter
├── README.md                   # Complete Documentation
│
├── contracts/
│   └── CertificateVerification.sol   # Solidity Smart Contract
│
├── blockchain/
│   ├── deploy.py               # Web3.py Smart Contract Deployment Script
│   └── contract_abi.json       # Compiled Contract ABI
│
├── models/
│   ├── database.py             # SQLAlchemy Instance
│   ├── user.py                 # User & Password Hashing Model
│   ├── student.py              # Student Model
│   ├── certificate.py          # Certificate Model
│   └── verification.py         # Verification Audit Log Model
│
├── services/
│   ├── hashing.py              # SHA-256 Canonical Hashing Engine
│   ├── blockchain.py           # Web3.py Ganache Integration Service
│   └── qr_code.py              # QR Code Generator Service
│
├── routes/
│   ├── auth.py                 # Login / Logout & Session Decorators
│   ├── admin.py                # Admin Dashboard & Certificate Management
│   ├── student.py              # Student Portfolio Portal
│   └── verification.py         # Public Verification & Audit Trails
│
├── templates/
│   ├── base.html               # Main Navigation & Bootstrap Layout
│   ├── index.html              # Landing Page
│   ├── login.html              # Login Page
│   ├── admin/                  # Dashboard, Form & Audit Log Views
│   ├── student/                # Student Dashboard Views
│   └── verification/           # Public Search & Match/Mismatch Result Views
│
├── static/
│   ├── css/style.css           # Custom Corporate Design Stylesheet
│   ├── js/main.js              # Interactive UI Scripts
│   └── uploads/                # Certificates & QR Code Images
│
└── tests/
    └── test_app.py             # Pytest Automated Test Suite
```
