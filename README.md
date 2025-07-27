# Wallpaper Engine Workshop Downloader

A clean, modern desktop application for downloading Steam Workshop wallpapers for Wallpaper Engine using DepotDownloader. Built with Flask and PyWebView for a native desktop experience.

## Features

- **🖥️ Desktop Application**: Native desktop window using PyWebView
- **🎨 Clean Interface**: Modern, responsive design using Bootstrap
- **🔍 Steam Workshop Browser**: Browse trending wallpapers directly from Steam
- **⚡ Real-time Downloads**: Live progress tracking with WebSocket connections
- **🔗 Workshop Parser**: Easy input of Steam Workshop URLs or IDs  
- **📋 Queue Management**: Track multiple downloads simultaneously
- **⚙️ Configuration Management**: Save your Steam credentials securely
- **🚀 One-Click Setup**: Simple batch file to install and run

## Setup Instructions

### Prerequisites

1. **Python 3.7+** installed on your system
2. **DepotDownloader** (included in the `DepotDownloaderMod` folder)
3. **Steam Account** with valid credentials
4. **Wallpaper Engine** installed (optional, for using downloaded wallpapers)

### Installation

#### Option 1: Easy Setup (Recommended)
1. **Clone/Download** this repository
2. **Navigate** to the project folder
3. **Double-click** `start.bat` - This will:
   - Automatically install all dependencies
   - Launch the desktop application

#### Option 2: Manual Setup
1. **Clone/Download** this repository
2. **Navigate** to the project folder:
   ```bash
   cd "Glitcheds WallPaper Engine Downloader"
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the desktop application**:
   ```bash
   python app.py
   ```

The application will open in a native desktop window. If the desktop window fails to open, it will automatically fallback to your browser at `http://127.0.0.1:5000`.

## Configuration

1. **Navigate to Settings** in the web interface
2. **Enter your Steam credentials**:
   - Steam Username
   - Steam Password
3. **Configure paths**:
   - Wallpaper Engine projects path (default: `C:/Program Files (x86)/Steam/steamapps/common/wallpaper_engine/projects/myprojects`)
   - DepotDownloader path (default: `./DepotDownloaderMod/DepotDownloaderMod.exe`)
4. **Save settings**

## Usage

### Method 1: Direct URL/ID Input
1. **Copy a Steam Workshop URL** (e.g., `https://steamcommunity.com/sharedfiles/filedetails/?id=3510729512`)
2. **Paste it into the input field** or just enter the ID number
3. **Click "Parse & Preview"** to see the wallpaper details
4. **Click "Download Wallpaper"** to start the download

### Method 2: Browse Workshop
1. **Click "Browse Trending"** in the Workshop Browser section
2. **Use filters** to find wallpapers by:
   - Sort: Trending, Most Recent, Most Subscribed, Most Favorited
   - Time period: Today, This Week, This Month, Last 3 Months, This Year
3. **Click on any wallpaper** to select it
4. **Click "Download Wallpaper"** to start the download

## Features Explained

### Workshop Browser
- Automatically fetches trending wallpapers from Steam Workshop
- Displays preview images and titles
- Filter by popularity and time period
- Click to select any wallpaper for download

### Real-time Progress
- Live output from DepotDownloader
- Progress bars for download status
- Status badges (Initializing, Running, Completed, Error)
- Toast notifications for important events

### Download Queue
- Track multiple downloads simultaneously
- View detailed logs for each download
- Monitor progress in real-time

## File Structure

```
Glitcheds WallPaper Engine Downloader/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── config.json           # Configuration file (created automatically)
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   └── config.html
├── static/               # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── DepotDownloaderMod/   # DepotDownloader executable and dependencies
```

## Security Notes

- Your Steam credentials are stored locally in `config.json`
- Credentials are only used to authenticate with Steam's servers
- Consider using Steam Guard for additional security
- For maximum security, create a dedicated Steam account for downloading

## Troubleshooting

### Common Issues

1. **"Steam credentials not configured"**
   - Go to Settings and enter your Steam username and password

2. **"DepotDownloader not found"**
   - Ensure the DepotDownloader path is correct in Settings
   - Check that `DepotDownloaderMod.exe` exists in the specified location

3. **"Error parsing workshop URL"**
   - Ensure the URL is a valid Steam Workshop link
   - Try using just the workshop ID number instead

4. **Downloads failing**
   - Check your Steam credentials
   - Ensure you have a stable internet connection
   - Verify the workshop item exists and is public

### Error Logs

Check the console output where you ran `python app.py` for detailed error messages.

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your Steam credentials are correct
3. Ensure all dependencies are installed
4. Check that DepotDownloader is working independently

## Credits

- **DepotDownloader**: SteamDB team
- **Flask**: Web framework
- **Bootstrap**: UI framework
- **Socket.IO**: Real-time communication
- **Ai**: For Making The README.md because I am very lazy
