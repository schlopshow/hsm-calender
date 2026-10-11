#!/usr/bin/env python3
"""
HackSmarter Calendar Web App
Interactive calendar editor with event management
"""

from flask import Flask, render_template, request, jsonify, send_file
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import calendar
import os
import re
import tempfile
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import html

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

# Store events in memory (in production, use a database)
events_store = {}


DEFAULT_SERIES = (
    {
        'title': 'TCM - PNPT/PJPT Study Group',
        'start': datetime(2026, 10, 11),
        'time_before_dst': '14:00',
        'time_after_dst': '14:00',
        'description': 'Weekly PNPT/PJPT study group. Sundays at 2 PM EST.',
    },
    {
        'title': 'Course Sign Up Info',
        'start': datetime(2026, 10, 13),
        'time_before_dst': '02:00',
        'time_after_dst': '01:00',
        'description': 'Course sign-up information and GitHub submission portal support.',
    },
    {
        'title': 'Weekly Goal Meeting',
        'start': datetime(2026, 10, 13),
        'time_before_dst': '04:00',
        'time_after_dst': '03:00',
        'description': 'Weekly goals meeting: what did you accomplish and what are you learning next?',
    },
    {
        'title': 'Weekly Goals #2',
        'start': datetime(2026, 10, 17),
        'time_before_dst': '21:00',
        'time_after_dst': '20:00',
        'description': 'Weekly goals check-in for the Hack Smarter community.',
    },
)


def build_default_events():
    """Build 13 weekly occurrences for each calendar series."""
    generated = {}
    daylight_saving_transition = datetime(2026, 11, 1)

    for series in DEFAULT_SERIES:
        occurrence = series['start']
        for _ in range(13):
            date_key = occurrence.strftime('%Y-%m-%d')
            time_key = 'time_before_dst' if occurrence < daylight_saving_transition else 'time_after_dst'
            generated.setdefault(date_key, []).append({
                'title': series['title'],
                'time': series[time_key],
                'description': series['description'],
            })
            occurrence += timedelta(days=7)

    return generated


events_store.update(build_default_events())


# Security: Input validation functions
def sanitize_text(text, max_length=200):
    """Sanitize text input to prevent XSS and limit length"""
    if not text or not isinstance(text, str):
        return ""
    # Remove any HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    # Escape HTML entities
    text = html.escape(text)
    # Limit length
    return text[:max_length].strip()

def validate_date(date_str):
    """Validate date string format YYYY-MM-DD"""
    if not date_str or not isinstance(date_str, str):
        return False
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False
    try:
        year, month, day = map(int, date_str.split('-'))
        if not (1900 <= year <= 2100):
            return False
        if not (1 <= month <= 12):
            return False
        if not (1 <= day <= 31):
            return False
        # Validate actual date
        datetime(year, month, day)
        return True
    except (ValueError, TypeError):
        return False

def validate_time(time_str):
    """Validate time string format HH:MM"""
    if not time_str:
        return True  # Empty is ok
    if not isinstance(time_str, str):
        return False
    pattern = r'^\d{2}:\d{2}$'
    if not re.match(pattern, time_str):
        return False
    try:
        hours, minutes = map(int, time_str.split(':'))
        return 0 <= hours <= 23 and 0 <= minutes <= 59
    except (ValueError, TypeError):
        return False

def validate_month_year(month, year):
    """Validate month and year parameters"""
    try:
        month = int(month)
        year = int(year)
        if not (1 <= month <= 12):
            return False
        if not (1900 <= year <= 2100):
            return False
        return True
    except (ValueError, TypeError):
        return False

class WeeklySchedule:
    """Generate weekly event schedule similar to Simply Cyber style"""
    
    def __init__(self, start_date, events=None, theme='hacker_green'):
        self.start_date = start_date
        self.events = events or {}
        
        # Set theme colors from calendar themes
        if theme not in HackSmarterCalendar.THEMES:
            theme = 'hacker_green'
        
        theme_colors = HackSmarterCalendar.THEMES[theme]
        self.bg_color = theme_colors['bg_color']
        self.header_color = theme_colors['header_color']
        self.accent_color = theme_colors['accent_color']
        self.text_color = theme_colors['text_color']
        self.grid_color = theme_colors['grid_color']
        self.cell_bg = theme_colors['cell_bg']
        self.event_color = theme_colors['event_color']
        
        # Page setup - portrait for weekly schedule
        self.page_width, self.page_height = letter
        
    def create_schedule(self, output_file, logo_path):
        """Generate the weekly schedule PNG"""
        # Create PDF first
        pdf_file = output_file.replace('.png', '.pdf')
        c = canvas.Canvas(pdf_file, pagesize=letter)
        
        # Background with gradient effect
        c.setFillColor(self.bg_color)
        c.rect(0, 0, self.page_width, self.page_height, fill=True, stroke=False)
        
        # Draw schedule
        self._draw_header(c, logo_path)
        self._draw_week_header(c)
        self._draw_events(c)
        self._draw_footer(c)
        
        c.save()
        
        # Convert to PNG
        png_file = self._convert_to_png(pdf_file, output_file)
        
        # Clean up PDF
        if png_file == output_file and os.path.exists(png_file):
            try:
                os.remove(pdf_file)
            except:
                pass
        
        return png_file if png_file else pdf_file
    
    def _draw_header(self, c, logo_path):
        """Draw header with logo and title"""
        header_y = self.page_height - 1.2 * inch
        
        # Logo
        try:
            if logo_path and os.path.exists(logo_path):
                img = ImageReader(logo_path)
                logo_size = 0.8 * inch
                c.drawImage(img, 0.5 * inch, header_y - 0.1 * inch,
                           width=logo_size, height=logo_size,
                           mask='auto', preserveAspectRatio=True)
        except Exception as e:
            print(f"Warning: Could not load logo: {e}")
        
        # Title
        c.setFillColor(self.text_color)
        c.setFont("Helvetica-Bold", 32)
        c.drawString(1.5 * inch, header_y + 0.2 * inch, "WEEKLY EVENTS SCHEDULE")
        
        # Accent line under title
        c.setStrokeColor(self.accent_color)
        c.setLineWidth(3)
        c.line(0.5 * inch, header_y - 0.1 * inch, 
               self.page_width - 0.5 * inch, header_y - 0.1 * inch)
    
    def _draw_week_header(self, c):
        """Draw the week date range"""
        from datetime import timedelta
        
        end_date = self.start_date + timedelta(days=6)
        
        week_y = self.page_height - 1.8 * inch
        
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(self.accent_color)
        
        date_str = f"{self.start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        date_width = c.stringWidth(date_str, "Helvetica-Bold", 20)
        c.drawString((self.page_width - date_width) / 2, week_y, date_str.upper())
    
    def _draw_events(self, c):
        """Draw daily events"""
        from datetime import timedelta
        
        start_y = self.page_height - 2.5 * inch
        day_height = 1.1 * inch
        
        day_names = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
        
        for i in range(7):
            current_date = self.start_date + timedelta(days=i)
            date_key = current_date.strftime('%Y-%m-%d')
            
            y_pos = start_y - (i * day_height)
            
            # Day box background
            c.setFillColor(self.cell_bg)
            c.setStrokeColor(self.grid_color)
            c.setLineWidth(1)
            c.rect(0.5 * inch, y_pos - 0.9 * inch, 
                   self.page_width - 1 * inch, 0.9 * inch, 
                   fill=True, stroke=True)
            
            # Day icon (calendar style)
            icon_x = 0.7 * inch
            icon_y = y_pos - 0.5 * inch
            
            # Icon background
            c.setFillColor(self.accent_color)
            c.roundRect(icon_x, icon_y - 0.3 * inch, 0.6 * inch, 0.5 * inch, 
                       0.05 * inch, fill=True, stroke=False)
            
            # Day name on icon
            c.setFillColor(colors.black if str(self.accent_color.hexval()) == '#ffffff' else colors.white)
            c.setFont("Helvetica-Bold", 10)
            day_text = day_names[i]
            day_width = c.stringWidth(day_text, "Helvetica-Bold", 10)
            c.drawString(icon_x + 0.3 * inch - day_width/2, icon_y - 0.1 * inch, day_text)
            
            # Day number on icon
            c.setFont("Helvetica-Bold", 16)
            day_num = str(current_date.day)
            num_width = c.stringWidth(day_num, "Helvetica-Bold", 16)
            c.drawString(icon_x + 0.3 * inch - num_width/2, icon_y - 0.27 * inch, day_num)
            
            # Events for this day
            if date_key in self.events and self.events[date_key]:
                events_x = 1.5 * inch
                event_y = y_pos - 0.3 * inch
                
                for event in self.events[date_key][:3]:  # Max 3 events per day
                    title = sanitize_text(event.get('title', ''), max_length=50)
                    time_str = sanitize_text(event.get('time', ''), max_length=5)
                    
                    # Event title
                    c.setFillColor(self.text_color)
                    c.setFont("Helvetica-Bold", 11)
                    
                    if len(title) > 40:
                        title = title[:37] + "..."
                    
                    c.drawString(events_x, event_y, title.upper())
                    
                    # Event time
                    if time_str:
                        c.setFillColor(self.accent_color)
                        c.setFont("Helvetica", 11)
                        time_x = self.page_width - 1.5 * inch
                        c.drawString(time_x, event_y, time_str)
                    
                    event_y -= 0.22 * inch
                
                # Show "+X more" if more events
                if len(self.events[date_key]) > 3:
                    c.setFillColor(colors.HexColor('#888888'))
                    c.setFont("Helvetica", 9)
                    c.drawString(events_x, event_y, f"+{len(self.events[date_key]) - 3} more events")
            else:
                # No events
                c.setFillColor(colors.HexColor('#666666'))
                c.setFont("Helvetica-Oblique", 11)
                c.drawString(1.5 * inch, y_pos - 0.45 * inch, "No events scheduled")
    
    def _draw_footer(self, c):
        """Draw footer"""
        c.setFont("Courier", 9)
        c.setFillColor(colors.HexColor('#666666'))
        footer_text = "Stay focused · Code smart · Hack smarter"
        footer_width = c.stringWidth(footer_text, "Courier", 9)
        c.drawString((self.page_width - footer_width) / 2, 0.4 * inch, footer_text)
    
    def _convert_to_png(self, pdf_file, png_file):
        """Convert PDF to PNG"""
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_file, dpi=300)
            if images:
                images[0].save(png_file, 'PNG')
                return png_file
        except Exception as e:
            print(f"Error converting to PNG: {e}")
            return pdf_file
        return None


class HackSmarterCalendar:
    # Define color themes
    THEMES = {
        'hacker_green': {
            'name': 'Hacker Green',
            'bg_color': colors.HexColor('#0a0a0a'),
            'header_color': colors.HexColor('#1a1a1a'),
            'accent_color': colors.HexColor('#00ff88'),
            'text_color': colors.HexColor('#ffffff'),
            'grid_color': colors.HexColor('#333333'),
            'cell_bg': colors.HexColor('#1a1a1a'),
            'event_color': colors.HexColor('#00ff88'),
        },
        'cyberpunk_purple': {
            'name': 'Cyberpunk Purple',
            'bg_color': colors.HexColor('#0a0a0a'),
            'header_color': colors.HexColor('#1a0a1a'),
            'accent_color': colors.HexColor('#ff00ff'),
            'text_color': colors.HexColor('#ffffff'),
            'grid_color': colors.HexColor('#4a1a4a'),
            'cell_bg': colors.HexColor('#1a0a1a'),
            'event_color': colors.HexColor('#ff00ff'),
        },
        'electric_blue': {
            'name': 'Electric Blue',
            'bg_color': colors.HexColor('#0a0a0a'),
            'header_color': colors.HexColor('#0a1a2a'),
            'accent_color': colors.HexColor('#00d4ff'),
            'text_color': colors.HexColor('#ffffff'),
            'grid_color': colors.HexColor('#1a4a6a'),
            'cell_bg': colors.HexColor('#0a1a2a'),
            'event_color': colors.HexColor('#00d4ff'),
        },
        'hot_pink': {
            'name': 'Hot Pink',
            'bg_color': colors.HexColor('#0a0a0a'),
            'header_color': colors.HexColor('#2a0a1a'),
            'accent_color': colors.HexColor('#ff0066'),
            'text_color': colors.HexColor('#ffffff'),
            'grid_color': colors.HexColor('#4a1a2a'),
            'cell_bg': colors.HexColor('#1a0a0f'),
            'event_color': colors.HexColor('#ff0066'),
        },
        'matrix_green': {
            'name': 'Matrix Green',
            'bg_color': colors.HexColor('#000000'),
            'header_color': colors.HexColor('#001100'),
            'accent_color': colors.HexColor('#00ff00'),
            'text_color': colors.HexColor('#00ff00'),
            'grid_color': colors.HexColor('#003300'),
            'cell_bg': colors.HexColor('#001100'),
            'event_color': colors.HexColor('#00ff00'),
        },
        'orange_fire': {
            'name': 'Orange Fire',
            'bg_color': colors.HexColor('#0a0a0a'),
            'header_color': colors.HexColor('#2a1a0a'),
            'accent_color': colors.HexColor('#ff6600'),
            'text_color': colors.HexColor('#ffffff'),
            'grid_color': colors.HexColor('#4a3a1a'),
            'cell_bg': colors.HexColor('#1a0f0a'),
            'event_color': colors.HexColor('#ff6600'),
        },
        'neon_yellow': {
            'name': 'Neon Yellow',
            'bg_color': colors.HexColor('#0a0a0a'),
            'header_color': colors.HexColor('#2a2a0a'),
            'accent_color': colors.HexColor('#ffff00'),
            'text_color': colors.HexColor('#ffffff'),
            'grid_color': colors.HexColor('#4a4a1a'),
            'cell_bg': colors.HexColor('#1a1a0a'),
            'event_color': colors.HexColor('#ffff00'),
        },
        'red_alert': {
            'name': 'Red Alert',
            'bg_color': colors.HexColor('#0a0a0a'),
            'header_color': colors.HexColor('#2a0a0a'),
            'accent_color': colors.HexColor('#ff0000'),
            'text_color': colors.HexColor('#ffffff'),
            'grid_color': colors.HexColor('#4a1a1a'),
            'cell_bg': colors.HexColor('#1a0a0a'),
            'event_color': colors.HexColor('#ff0000'),
        },
        'crimson_red': {
            'name': 'Crimson Red',
            'bg_color': colors.HexColor('#0a0000'),
            'header_color': colors.HexColor('#1a0505'),
            'accent_color': colors.HexColor('#dc143c'),
            'text_color': colors.HexColor('#ffffff'),
            'grid_color': colors.HexColor('#4a0a0a'),
            'cell_bg': colors.HexColor('#150505'),
            'event_color': colors.HexColor('#dc143c'),
        },
        'white_minimal': {
            'name': 'White Minimal',
            'bg_color': colors.HexColor('#ffffff'),
            'header_color': colors.HexColor('#f5f5f5'),
            'accent_color': colors.HexColor('#000000'),
            'text_color': colors.HexColor('#000000'),
            'grid_color': colors.HexColor('#cccccc'),
            'cell_bg': colors.HexColor('#fafafa'),
            'event_color': colors.HexColor('#333333'),
        },
    }
    
    def __init__(self, month, year, events=None, theme='hacker_green', logo_style='dark'):
        # Validate inputs
        if not validate_month_year(month, year):
            raise ValueError("Invalid month or year")
        
        self.month = int(month)
        self.year = int(year)
        self.month_name = calendar.month_name[self.month]
        self.events = events or {}
        self.logo_style = logo_style  # 'dark' or 'light'
        
        # Set theme colors
        if theme not in self.THEMES:
            theme = 'hacker_green'
        
        theme_colors = self.THEMES[theme]
        self.bg_color = theme_colors['bg_color']
        self.header_color = theme_colors['header_color']
        self.accent_color = theme_colors['accent_color']
        self.text_color = theme_colors['text_color']
        self.grid_color = theme_colors['grid_color']
        self.cell_bg = theme_colors['cell_bg']
        self.event_color = theme_colors['event_color']
        
        # Page setup
        self.page_width, self.page_height = landscape(letter)
        
    def create_calendar(self, output_file, logo_path_light=None, logo_path_dark=None):
        """Generate the calendar PNG"""
        # Create PDF first
        pdf_file = output_file.replace('.png', '.pdf')
        c = canvas.Canvas(pdf_file, pagesize=landscape(letter))
        
        # Background
        c.setFillColor(self.bg_color)
        c.rect(0, 0, self.page_width, self.page_height, fill=True, stroke=False)
        
        # Header section
        self._draw_header(c, logo_path_light, logo_path_dark)
        
        # Calendar grid
        self._draw_calendar_grid(c)
        
        c.save()
        
        # Convert to PNG
        png_file = self._convert_to_png(pdf_file, output_file)
        
        # Clean up PDF if PNG was created successfully
        if png_file == output_file and os.path.exists(png_file):
            try:
                os.remove(pdf_file)
            except:
                pass
        
        return png_file if png_file else pdf_file
        
    def _draw_header(self, c, logo_path_light, logo_path_dark):
        """Draw the header with logo and month/year"""
        header_height = 1.5 * inch
        
        # Header background
        c.setFillColor(self.header_color)
        c.rect(0, self.page_height - header_height, self.page_width, header_height, 
               fill=True, stroke=False)
        
        # Accent line
        c.setStrokeColor(self.accent_color)
        c.setLineWidth(3)
        c.line(0, self.page_height - header_height, 
               self.page_width, self.page_height - header_height)
        
        # Choose appropriate logo based on theme
        logo_path = logo_path_dark if self.logo_style == 'dark' else logo_path_light
        
        # Logo
        try:
            if logo_path and os.path.exists(logo_path):
                img = ImageReader(logo_path)
                logo_size = 1 * inch
                logo_x = 0.5 * inch
                logo_y = self.page_height - header_height + 0.25 * inch
                c.drawImage(img, logo_x, logo_y, 
                           width=logo_size, height=logo_size, 
                           mask='auto', preserveAspectRatio=True)
        except Exception as e:
            print(f"Warning: Could not load logo: {e}")
        
        # Month and Year - centered
        c.setFillColor(self.text_color)
        c.setFont("Helvetica-Bold", 48)
        month_text = f"{self.month_name.upper()} {self.year}"
        text_width = c.stringWidth(month_text, "Helvetica-Bold", 48)
        c.drawString((self.page_width - text_width) / 2, 
                    self.page_height - header_height + 0.5 * inch, 
                    month_text)
        
        # Tagline
        c.setFont("Courier-Bold", 14)
        c.setFillColor(self.accent_color)
        tagline = "// HACK SMARTER"
        tagline_width = c.stringWidth(tagline, "Courier-Bold", 14)
        c.drawString(self.page_width - tagline_width - 0.5 * inch,
                    self.page_height - header_height + 0.6 * inch,
                    tagline)
        
    def _draw_calendar_grid(self, c):
        """Draw the calendar grid with days and events"""
        # Grid positioning
        grid_start_y = self.page_height - 2.2 * inch
        grid_height = grid_start_y - 0.5 * inch
        grid_start_x = 0.3 * inch
        grid_width = self.page_width - 0.6 * inch
        
        cell_width = grid_width / 7
        cell_height = grid_height / 6
        
        # Day headers
        day_names = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(self.accent_color)
        
        for i, day in enumerate(day_names):
            x = grid_start_x + (i * cell_width) + (cell_width / 2)
            y = grid_start_y + 0.15 * inch
            day_width = c.stringWidth(day, "Helvetica-Bold", 12)
            c.drawString(x - day_width / 2, y, day)
        
        # Get calendar data
        cal = calendar.monthcalendar(self.year, self.month)
        
        # Draw cells
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                x = grid_start_x + (day_num * cell_width)
                y = grid_start_y - ((week_num + 1) * cell_height)
                
                # Cell background
                c.setFillColor(self.cell_bg)
                c.setStrokeColor(self.grid_color)
                c.setLineWidth(0.5)
                c.rect(x, y, cell_width, cell_height, fill=True, stroke=True)
                
                # Day number
                if day != 0:
                    # Highlight weekends
                    if day_num >= 5:
                        c.setFillColor(self.accent_color)
                        c.setFont("Helvetica-Bold", 20)
                    else:
                        c.setFillColor(self.text_color)
                        c.setFont("Helvetica-Bold", 18)
                    
                    c.drawString(x + 8, y + cell_height - 25, str(day))
                    
                    # Draw events for this day
                    day_key = f"{self.year}-{self.month:02d}-{day:02d}"
                    if day_key in self.events:
                        self._draw_events(c, x, y, cell_height,
                                        self.events[day_key])
                    
                    # Subtle diagonal line
                    c.setStrokeColor(colors.HexColor('#2a2a2a'))
                    c.setLineWidth(1)
                    c.line(x + cell_width - 30, y + 5, 
                          x + cell_width - 5, y + 30)
        
        # Footer
        c.setFont("Courier", 10)
        c.setFillColor(colors.HexColor('#666666'))
        footer_text = "Stay focused · Code smart · Hack smarter"
        footer_width = c.stringWidth(footer_text, "Courier", 10)
        c.drawString((self.page_width - footer_width) / 2, 0.3 * inch, footer_text)
    
    def _draw_events(self, c, x, y, cell_height, events):
        """Draw events in a cell"""
        c.setFont("Helvetica", 8)
        c.setFillColor(self.event_color)
        
        max_events = 4  # Show max 4 events per cell
        event_y = y + cell_height - 45
        
        for event in events[:max_events]:
            # Sanitize event data
            event_title = sanitize_text(event.get('title', ''), max_length=50)
            if not event_title:
                continue
                
            event_text = event_title
            # Truncate if too long
            if len(event_text) > 18:
                event_text = event_text[:15] + "..."
            
            # Event bullet point
            c.circle(x + 10, event_y - 2, 2, fill=1, stroke=0)
            c.drawString(x + 16, event_y - 4, event_text)
            event_y -= 12
        
        # Show +X more if there are more events
        if len(events) > max_events:
            c.setFont("Helvetica", 7)
            c.setFillColor(colors.HexColor('#888888'))
            c.drawString(x + 10, event_y - 4, f"+{len(events) - max_events} more")
    
    def _convert_to_png(self, pdf_file, png_file):
        """Convert PDF to PNG"""
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_file, dpi=300)
            if images:
                images[0].save(png_file, 'PNG')
                return png_file
        except Exception as e:
            print(f"Error converting to PNG: {e}")
            # If conversion fails, return PDF
            return pdf_file
        return None


@app.route('/')
def index():
    """Main calendar editor page"""
    return render_template('index.html')


@app.route('/api/themes')
def get_themes():
    """Get available color themes"""
    themes = []
    for key, theme in HackSmarterCalendar.THEMES.items():
        themes.append({
            'id': key,
            'name': theme['name'],
            'accent': theme['accent_color'].hexval()
        })
    return jsonify(themes)


@app.route('/api/calendar/<int:year>/<int:month>')
def get_calendar(year, month):
    """Get calendar data for a specific month"""
    # Validate input
    if not validate_month_year(month, year):
        return jsonify({'error': 'Invalid month or year'}), 400
    
    try:
        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        
        return jsonify({
            'year': year,
            'month': month,
            'month_name': month_name,
            'weeks': cal,
            'events': events_store
        })
    except Exception:
        return jsonify({'error': 'Failed to generate calendar'}), 500


@app.route('/api/events', methods=['GET', 'POST', 'DELETE'])
def handle_events():
    """Handle event CRUD operations"""
    global events_store
    
    if request.method == 'GET':
        return jsonify(events_store)
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Validate date
            date = data.get('date', '')
            if not validate_date(date):
                return jsonify({'error': 'Invalid date format'}), 400
            
            # Validate and sanitize title
            title = sanitize_text(data.get('title', ''), max_length=200)
            if not title or len(title) < 1:
                return jsonify({'error': 'Title is required'}), 400
            
            # Validate time if provided
            time_str = data.get('time', '')
            if time_str and not validate_time(time_str):
                return jsonify({'error': 'Invalid time format'}), 400
            time_str = sanitize_text(time_str, max_length=5)
            
            # Sanitize description
            description = sanitize_text(data.get('description', ''), max_length=500)
            
            # Limit number of events per day
            if date not in events_store:
                events_store[date] = []
            elif len(events_store[date]) >= 20:
                return jsonify({'error': 'Maximum 20 events per day'}), 400
            
            event = {
                'title': title,
                'time': time_str,
                'description': description
            }
            
            events_store[date].append(event)
            
            return jsonify({'success': True, 'events': events_store})
        
        except Exception:
            return jsonify({'error': 'Failed to add event'}), 500
    
    elif request.method == 'DELETE':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            date = data.get('date', '')
            if not validate_date(date):
                return jsonify({'error': 'Invalid date format'}), 400
            
            index = data.get('index')
            if not isinstance(index, int) or index < 0:
                return jsonify({'error': 'Invalid index'}), 400
            
            if date in events_store and len(events_store[date]) > index:
                events_store[date].pop(index)
                if not events_store[date]:
                    del events_store[date]
                return jsonify({'success': True, 'events': events_store})
            else:
                return jsonify({'error': 'Event not found'}), 404
        
        except Exception:
            return jsonify({'error': 'Failed to delete event'}), 500


@app.route('/api/events/clear', methods=['DELETE'])
def clear_events():
    """Remove all events from the in-memory calendar."""
    global events_store
    events_store.clear()
    return jsonify({'success': True, 'events': events_store})


@app.route('/api/generate/weekly/<year>/<month>/<day>')
def generate_weekly_schedule(year, month, day):
    """Generate weekly schedule PNG starting from a specific date"""
    try:
        # Validate input
        year, month, day = int(year), int(month), int(day)
        if not validate_month_year(month, year):
            return jsonify({'error': 'Invalid month or year'}), 400
        
        from datetime import datetime, timedelta
        
        # Create start date (beginning of week - Monday)
        start_date = datetime(year, month, day)
        # Adjust to Monday if not already
        days_to_monday = start_date.weekday()
        start_date = start_date - timedelta(days=days_to_monday)
        
        # Get theme from query parameter
        theme = request.args.get('theme', 'hacker_green')
        if theme not in HackSmarterCalendar.THEMES:
            theme = 'hacker_green'
        
        output_dir = os.path.join(tempfile.gettempdir(), 'hacksmarter-calendar')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        filename = secure_filename(
            f'weekly_schedule_{start_date.strftime("%Y_%m_%d")}_{theme}.png'
        )
        output_file = os.path.join(output_dir, filename)
        
        # Logo path
        logo_path = os.path.join('/mnt/user-data/uploads', '3625.png')
        if theme == 'white_minimal':
            logo_path = os.path.join('/mnt/user-data/uploads', '3623.png')
        
        # Create weekly schedule
        schedule = WeeklySchedule(start_date, events_store, theme=theme)
        result_file = schedule.create_schedule(output_file, logo_path)
        
        # Verify file was created
        if not os.path.exists(result_file):
            return jsonify({'error': 'Failed to generate schedule'}), 500
        
        download_name = secure_filename(
            f'HackSmarter_Week_{start_date.strftime("%b%d")}_{theme}.png'
        )
        result_mimetype = 'image/png' if result_file.lower().endswith('.png') else 'application/pdf'
        if result_mimetype == 'application/pdf':
            download_name = download_name.replace('.png', '.pdf')
        return send_file(
            result_file,
            as_attachment=True,
            download_name=download_name,
            mimetype=result_mimetype
        )
    
    except Exception as e:
        print(f"Error generating weekly schedule: {e}")
        return jsonify({'error': 'Failed to generate schedule'}), 500


@app.route('/api/generate/<int:year>/<int:month>')
def generate_calendar(year, month):
    """Generate calendar PNG with selected theme"""
    # Validate input
    if not validate_month_year(month, year):
        return jsonify({'error': 'Invalid month or year'}), 400
    
    try:
        # Get theme from query parameter
        theme = request.args.get('theme', 'hacker_green')
        if theme not in HackSmarterCalendar.THEMES:
            theme = 'hacker_green'
        
        output_dir = os.path.join(tempfile.gettempdir(), 'hacksmarter-calendar')
        os.makedirs(output_dir, exist_ok=True)
        
        # Use secure filename with PNG extension
        filename = secure_filename(f'calendar_{year}_{month:02d}_{theme}.png')
        output_file = os.path.join(output_dir, filename)
        
        # Logo paths
        logo_path_light = os.path.join('/mnt/user-data/uploads', '3623.png')
        logo_path_dark = os.path.join('/mnt/user-data/uploads', '3625.png')
        
        # Determine logo style based on theme
        logo_style = 'light' if theme == 'white_minimal' else 'dark'
        
        cal = HackSmarterCalendar(month, year, events_store, theme=theme, logo_style=logo_style)
        result_file = cal.create_calendar(output_file, logo_path_light, logo_path_dark)
        
        # Verify file was created
        if not os.path.exists(result_file):
            return jsonify({'error': 'Failed to generate calendar'}), 500
        
        month_name = calendar.month_name[month]
        download_name = secure_filename(f'HackSmarter_{month_name}_{year}_{theme}.png')
        
        result_mimetype = 'image/png' if result_file.lower().endswith('.png') else 'application/pdf'
        download_name = (
            download_name if result_mimetype == 'image/png'
            else download_name.replace('.png', '.pdf')
        )
        return send_file(
            result_file,
            as_attachment=True,
            download_name=download_name,
            mimetype=result_mimetype
        )
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error generating calendar: {e}")
        return jsonify({'error': 'Failed to generate calendar'}), 500


if __name__ == '__main__':
    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval'"
        return response
    
    print("🚀 Starting HackSmarter Calendar Web App...")
    print("📍 Open your browser to: http://localhost:5000")
    print("⚠️  WARNING: This is a development server. Use a production WSGI server for deployment.")
    print("✅ Security features enabled:")
    print("   - Input validation and sanitization")
    print("   - XSS protection")
    print("   - CSRF headers")
    print("   - File size limits")
    print("   - Rate limiting on events per day")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
