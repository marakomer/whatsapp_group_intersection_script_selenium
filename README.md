# WhatsApp Group Member Intersection Analyzer

A Python tool to find members that are common across multiple WhatsApp groups.

## Features

- 🔐 Secure WhatsApp Web authentication via QR code
- 📋 List all your WhatsApp groups with friendly display names
- ✅ Easy group selection interface (supports ranges like 1-5)
- 🔍 Find members shared across selected groups
- 📊 Export detailed results to CSV
- 💾 Persistent session (won't ask to login every time)

## Requirements

- Python 3.7+
- Google Chrome browser
- ChromeDriver (automatically managed)
- Active WhatsApp account

## Installation

**Quick Setup (Recommended):**
```bash
./setup.sh
```

The setup script will automatically:
- Check for Python 3 and pip3
- Install all required dependencies
- Configure the environment

**Manual Installation (Alternative):**
If you prefer manual setup:
```bash
pip install -r requirements.txt
```

**Using Virtual Environment (Optional):**
For isolated dependency management:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

1. **First time setup:**
   ```bash
   ./setup.sh
   ```

2. **Run the script:**
   ```bash
   python3 whatsapp_group_analyzer.py
   ```

3. **Authenticate:**
   - A Chrome window will open with WhatsApp Web
   - Scan the QR code with your WhatsApp mobile app
   - Wait for the page to load completely

4. **Select groups:**
   - The script will list all your groups
   - Enter group numbers to analyze (e.g., `1,3,5` or `1-3,7-9`)
   - Confirm your selection

5. **View results:**
   - Common members will be displayed in the terminal
   - A detailed CSV report will be generated with:
     - List of selected groups
     - Common members
     - Detailed membership matrix

## CSV Output Format

The generated CSV file includes:
- **Summary section:** Selected groups and member counts
- **Common members:** List of all shared members
- **Detailed matrix:** All members with checkmarks (✓/✗) showing group membership

Example filename: `whatsapp_group_intersection_20231204_143022.csv`

## Selection Syntax

You can select groups using:
- Individual numbers: `1,3,5`
- Ranges: `1-5` (selects groups 1, 2, 3, 4, 5)
- Mixed: `1-3,7,9-11`

## Troubleshooting

### "ChromeDriver not found"
Install ChromeDriver automatically:
```bash
pip install webdriver-manager
```

### "Login timeout"
- Ensure your internet connection is stable
- Make sure you scan the QR code within 2 minutes
- Check if WhatsApp Web is accessible in your browser

### "No groups found"
- Wait a few more seconds for groups to load
- Check if you have any groups in your WhatsApp
- Try refreshing by restarting the script

### Script closes browser immediately
- The script keeps the browser open until you press Enter
- Check the terminal for any error messages

## Privacy & Security

- All processing happens locally on your machine
- No data is sent to external servers
- Session data is stored in `/tmp/whatsapp_session`
- You can delete this folder to clear saved sessions

## Limitations

- Requires active WhatsApp Web session
- Group names must be unique for best results
- Very large groups (500+ members) may take longer to process
- Requires manual QR code scan for first-time authentication

## Tips

- Keep the browser window visible while the script runs
- Don't interact with WhatsApp Web manually during analysis
- For better performance, close unnecessary browser tabs
- The session persists, so subsequent runs won't require QR scanning

## License

Free to use and modify for personal purposes.

## Disclaimer

This tool uses WhatsApp Web automation and is not officially supported by WhatsApp. Use at your own discretion.
