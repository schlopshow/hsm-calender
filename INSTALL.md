# Quick Installation Guide 🚀

## Prerequisites

### 1. Install Python 3.9+

Check your Python version:
```bash
python3 --version
```

### 2. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv poppler-utils
```

**macOS:**
```bash
brew install python poppler
```

**Windows:**
1. Install Python from python.org
2. Download Poppler from: https://github.com/oschwartz10612/poppler-windows/releases
3. Add Poppler to PATH

## Installation Methods

### Method 1: pipx (Recommended) ⭐

pipx installs the app in an isolated environment:

```bash
# Install pipx
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Restart your terminal, then:
pipx install /path/to/hacksmarter_calendar
```

### Method 2: pip

```bash
pip install /path/to/hacksmarter_calendar
```

### Method 3: Development Install

```bash
cd hacksmarter_calendar
pip install -e .
```

## Running the App

```bash
# Start the web interface
hacksmarter-calendar

# Open browser to http://localhost:5000
```

## Common Issues

### "Command not found"

After pipx install, restart your terminal or run:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### "No module named 'pdf2image'"

Install system dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler
```

### Port already in use

```bash
hacksmarter-calendar --port 8080
```

## Testing the Installation

```bash
# Run the app
hacksmarter-calendar

# In another terminal
curl http://localhost:5000
```

Should see the HTML response!

## Updating

```bash
# With pipx
pipx upgrade hacksmarter-calendar

# Or reinstall
pipx install --force /path/to/hacksmarter_calendar
```

## Uninstalling

```bash
# With pipx
pipx uninstall hacksmarter-calendar

# With pip
pip uninstall hacksmarter-calendar
```

## Next Steps

1. Start the app: `hacksmarter-calendar`
2. Open browser: `http://localhost:5000`
3. Add events by clicking on days
4. Select a theme
5. Generate your calendar!

## Getting Help

- Check README.md for full documentation
- See THEMES.md for theme information
- Read SECURITY.md for security details
- View WEEKLY_SCHEDULE.md for weekly features

---

**Need help?** Open an issue on GitHub or check the documentation!
