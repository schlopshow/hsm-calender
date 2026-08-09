# HackSmarter Calendar 🚀

An interactive calendar and weekly schedule generator with multiple color themes, event management, and professional PNG output.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## Features ✨

- 🎨 **10 Color Themes** - Hacker Green, Cyberpunk Purple, Electric Blue, Hot Pink, Matrix Green, Orange Fire, Neon Yellow, Red Alert, Crimson Red, White Minimal
- 📅 **Monthly Calendar** - Full month grid view with events
- 📋 **Weekly Schedule** - Detailed day-by-day event list
- 🖼️ **PNG Output** - High-quality 300 DPI images
- 🌐 **Web Interface** - Interactive event management
- 🔒 **Security Focused** - Input validation, XSS protection, sanitization
- 📱 **Mobile Friendly** - Portrait weekly schedules perfect for phones

## Quick Install with pipx (Recommended) 🎯

```bash
# Install pipx if you don't have it
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install HackSmarter Calendar
pipx install /path/to/hacksmarter_calendar

# Run it!
hacksmarter-calendar
```

Then open your browser to `http://localhost:5000`

## Alternative Installation Methods

### Install with pip

```bash
pip install /path/to/hacksmarter_calendar
hacksmarter-calendar
```

### Install in Development Mode

```bash
cd hacksmarter_calendar
pip install -e .
hacksmarter-calendar --debug
```

### Run from Source

```bash
cd hacksmarter_calendar
python -m hacksmarter_calendar.cli
```

## Usage 📖

### Start the Web App

```bash
# Default (localhost:5000)
hacksmarter-calendar

# Custom port
hacksmarter-calendar --port 8080

# Accessible from network
hacksmarter-calendar --host 0.0.0.0

# Debug mode
hacksmarter-calendar --debug
```

### Web Interface

1. Open `http://localhost:5000` in your browser
2. Click on any day to add events
3. Fill in event details (title, time, description)
4. Select your preferred theme
5. Generate calendars:
   - **Monthly Calendar** - Full month grid view
   - **Weekly Schedule** - Detailed weekly list

### Programmatic Usage

```python
from hacksmarter_calendar import HackSmarterCalendar, WeeklySchedule
from datetime import datetime

# Create monthly calendar
events = {
    '2026-02-14': [
        {'title': 'Valentine\'s Day', 'time': '19:00', 'description': 'Dinner'}
    ]
}

cal = HackSmarterCalendar(
    month=2,
    year=2026,
    events=events,
    theme='cyberpunk_purple',
    logo_style='dark'
)

cal.create_calendar(
    'february_2026.png',
    logo_path_light='light_logo.png',
    logo_path_dark='dark_logo.png'
)

# Create weekly schedule
start_date = datetime(2026, 2, 10)
schedule = WeeklySchedule(start_date, events, theme='hacker_green')
schedule.create_schedule('week.png', 'logo.png')
```

## Available Themes 🎨

1. **Hacker Green** - Classic terminal aesthetic
2. **Cyberpunk Purple** - Futuristic neon vibes
3. **Electric Blue** - Professional tech look
4. **Hot Pink** - Bold and creative
5. **Matrix Green** - Retro 90s hacker style
6. **Orange Fire** - Warm and energetic
7. **Neon Yellow** - High visibility
8. **Red Alert** - Urgent and important
9. **Crimson Red** - Deep red aesthetic ⭐ NEW
10. **White Minimal** - Clean printable design

## System Requirements

### Python Version
- Python 3.9 or higher

### Dependencies
- Flask (web framework)
- Pillow (image processing)
- ReportLab (PDF generation)
- pdf2image (PNG conversion)

### System Packages (for pdf2image)

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

**Windows:**
Download and install Poppler from: https://github.com/oschwartz10612/poppler-windows/releases

## Configuration

### Default Logo Paths

Place your logos in these locations (or update in code):
- Light logo: `/mnt/user-data/uploads/3623.png`
- Dark logo: `/mnt/user-data/uploads/3625.png`

### Custom Port

```bash
export FLASK_RUN_PORT=8080
hacksmarter-calendar
```

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black hacksmarter_calendar/
```

### Linting

```bash
flake8 hacksmarter_calendar/
```

## Project Structure

```
hacksmarter_calendar/
├── pyproject.toml          # Package configuration
├── README.md               # This file
├── LICENSE                 # MIT License
└── hacksmarter_calendar/
    ├── __init__.py         # Package initialization
    ├── cli.py              # CLI entry point
    ├── calendar_app.py     # Main application
    └── templates/
        └── index.html      # Web interface
```

## Security Features 🔒

- ✅ Input validation and sanitization
- ✅ XSS protection (HTML escaping)
- ✅ CSRF headers
- ✅ File size limits (16MB max)
- ✅ Rate limiting (20 events per day)
- ✅ Secure file handling
- ✅ Error handling with generic messages

## CLI Options

```
usage: hacksmarter-calendar [-h] [--host HOST] [--port PORT] [--debug] [--version]

HackSmarter Calendar - Interactive calendar generator

optional arguments:
  -h, --help      show this help message and exit
  --host HOST     Host to bind to (default: 127.0.0.1)
  --port PORT     Port to bind to (default: 5000)
  --debug         Enable debug mode
  --version       show program's version number and exit
```

## Troubleshooting

### "Module not found" error

Make sure you've installed the package:
```bash
pipx install /path/to/hacksmarter_calendar
```

### PNG conversion fails

Install poppler-utils:
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler
```

### Port already in use

Use a different port:
```bash
hacksmarter-calendar --port 8080
```

### Permission denied

Try with user install:
```bash
pip install --user /path/to/hacksmarter_calendar
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/hacksmarter/calendar/issues
- Documentation: See THEMES.md, SECURITY.md, WEEKLY_SCHEDULE.md

## Changelog

### v1.0.0 (2026-02-02)
- Initial release
- 10 color themes
- Monthly calendar generation
- Weekly schedule generation
- Web interface with event management
- Security features
- PNG output with 300 DPI

## Acknowledgments

- Inspired by professional streaming schedules
- Built with Flask, ReportLab, and Pillow
- HackSmarter branding

---

**Made with ❤️ by HackSmarter**

Stay focused · Code smart · Hack smarter
# hsm-calender
# hsm-calender
# hsm-calender
# hsm-calender
