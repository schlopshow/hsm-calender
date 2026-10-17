#!/usr/bin/env python3
"""
CLI entry point for HackSmarter Calendar
"""

import sys
import os
import argparse
from pathlib import Path


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="HackSmarter Calendar - Interactive calendar generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start the web interface (default)
  hacksmarter-calendar

  # Start on a custom port
  hacksmarter-calendar --port 8080

  # Start on all interfaces
  hacksmarter-calendar --host 0.0.0.0

  # Enable debug mode
  hacksmarter-calendar --debug

For more information: https://github.com/hacksmarter/calendar
        """
    )

    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to bind to (default: 5000)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    # Import the Flask app
    from .calendar_app import app

    # Print startup message
    print(f"📍 Open your browser to: http://{args.host}:{args.port}")
    print("⚠️  Press CTRL+C to stop the server")

    try:
        app.run(
            debug=args.debug,
            host=args.host,
            port=args.port
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down HackSmarter Calendar...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
