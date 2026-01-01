# CSV SQL Engine Pro

A powerful SQL engine for analyzing CSV files with an intuitive Streamlit-based interface.

## Features

- **Smart CSV Ingestion**: Automatically detect and parse CSV files
- **SQL Query Interface**: Run SQL queries directly on your CSV data
- **Schema Management**: Track and version your table schemas
- **Performance Optimized**: Built on DuckDB for fast querying of large datasets
- **Auto-Updates**: Built-in update mechanism to keep your app current
- **User-Friendly UI**: Modern, intuitive interface built with Streamlit

## Installation

### macOS

1. Download the `CSV SQL Engine Pro.dmg` file
2. Open the DMG and drag the app to your Applications folder
3. Launch the application from Applications

## Usage

1. Launch the application
2. Upload or select CSV files from your system
3. Write SQL queries to analyze your data
4. View results in a clean, formatted table

## Auto-Update System

The application includes an automatic update system that:

- Checks for updates when you launch the app
- Shows you what's new in each version
- Allows you to:
  - **Update Now**: Download and install the latest version
  - **Skip This Version**: Don't show this update again
  - **Remind Me Later**: Skip for now, but check again next time

Your data and preferences are preserved during updates.

## Development

### Requirements

- Python 3.9+
- See `requirements.txt` for dependencies

### Setup

```bash
# Clone the repository
git clone https://github.com/int-meetmovaliya-jpg/Csv_Sql_Engine_Pro.git
cd Csv_Sql_Engine_Pro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running from Source

```bash
python bootstrap.py
```

### Building DMG

```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Build the application
pyinstaller "CSV SQL Engine Pro.spec"

# Create DMG (requires dmgbuild)
pip install dmgbuild
# Then create DMG manually or use a script
```

## Version History

See `version.json` for the current version and changelog.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license here]

## Support

For issues and questions, please open an issue on GitHub.

