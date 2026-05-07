# hash.all - Secure Password Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Stars](https://img.shields.io/github/stars/Pinfoxxx/hash.all.svg)](https://github.com/Pinfoxxx/hash.all/stargazers)

> **Universal cross-platform password manager** with a modern interface, reliable encryption, and protection from hacking.

**Advantages:**
- 🔒 AES-128 encryption (Fernet) with PBKDF2 key derivation
- ⚡ Fast and intuitive password management
- 🌍 Support for Russian and English languages (with the possibility of adding others)
- 🛡️ Brute-force protection (rate limiting)
- 🔍 Checking passwords via the HIBP and Yandex APIs
- 🎨 Black theme with cool design
- 💾 Secure storage with atomic persistence
- 🖥️ Cross-platform (Windows, macOS, Linux)

## 🚀 Fast start

### System requirements
- **Python**: 3.12 or higher
- **OC**: Windows 7+, macOS 10.14+, GNU/Linux 5.10+
- **RAM**: 256 MB
- **HDD/SSD**: 100 MB

### Install from releases or from source code

#### On Windows (PowerShell)
```PowerShell
# Cloning
git clone https://github.com/Pinfoxxx/hash.all.git
cd hash.all

# Creating a virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

#### On macOS / GNU/Linux (bash, zsh)
```bash
# Cloning
git clone https://github.com/Pinfoxxx/hash.all.git
cd hash.all

# Creating a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```
