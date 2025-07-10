# 📊 Figma API Data Extractor

A beginner-friendly tool to download and organize your Figma team data. This tool helps you extract information about your Figma teams, projects, and files, saving everything in a structured format that's easy to understand and use for backups or analysis.

## ✨ What This Tool Does

This tool connects to your Figma account and:
- 📋 Extracts all your team information
- 📁 Lists all projects within those teams
- 🎨 Gathers details about all your design files
- 💾 Organizes everything into a single, well-structured JSON file
- 🌈 Provides colorful, easy-to-read progress updates while it works

> **No programming knowledge required!** Just follow the step-by-step instructions below.

## 🚀 Step-by-Step Installation Guide

### 📥 Step 1: Download the Tool

#### Option 1: Download as [ZIP](https://github.com/ohbus/figma-file-detials-extractor/archive/refs/heads/master.zip) (Easiest) 👍
1. Click the green "Code" button at the top of this page
2. Select "[Download ZIP](https://github.com/ohbus/figma-file-detials-extractor/archive/refs/heads/master.zip)"
3. Find the downloaded ZIP file in your Downloads folder
4. Right-click the ZIP file and select "Extract All..." (Windows) or double-click (Mac)
5. Choose where you want to extract the files and click "Extract"

#### Option 2: For Advanced Users - Clone with Git 🧙‍♂️
```bash
git clone git@github.com:ohbus/figma-file-detials-extractor.git
cd figma-api-main
```

### 🐍 Step 2: Install Python

Python is the software needed to run this tool. Follow the instructions for your operating system:

#### Windows 🪟
1. Visit [python.org/downloads](https://www.python.org/downloads/)
2. Download the latest Python installer (e.g., Python 3.10 or newer)
3. Run the installer
4. ⚠️ **IMPORTANT**: Check the box that says "Add Python to PATH" before clicking Install
5. Click "Install Now"
6. When complete, click "Close"

#### macOS 🍎
1. Visit [python.org/downloads](https://www.python.org/downloads/)
2. Download the latest Python installer for macOS
3. Open the downloaded .pkg file and follow the installation instructions
4. Verify installation by opening Terminal (find it using Spotlight search) and typing:
   ```
   python3 --version
   ```

#### Linux 🐧 (Ubuntu/Debian)
1. Open Terminal
2. Update your package list:
   ```
   sudo apt update
   ```
3. Install Python and pip:
   ```
   sudo apt install python3 python3-pip
   ```
4. Verify installation:
   ```
   python3 --version
   ```

### 🧪 Step 3: Set Up a Virtual Environment

A virtual environment is like a clean, separate space for your project. It helps keep things organized and avoids conflicts with other software.

#### Windows 🪟
1. Open Command Prompt (search for "cmd" in the Start menu)
2. Navigate to the folder where you extracted the files:
   ```
   cd path\to\figma-api-main
   ```
   (Replace "path\to" with your actual path)
3. Create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   ```
   venv\Scripts\activate
   ```
   You should see `(venv)` appear at the beginning of your command prompt line

#### macOS/Linux 🍎🐧
1. Open Terminal
2. Navigate to the folder where you extracted the files:
   ```
   cd path/to/figma-api-main
   ```
   (Replace "path/to" with your actual path)
3. Create a virtual environment:
   ```
   python3 -m venv venv
   ```
4. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```
   You should see `(venv)` appear at the beginning of your terminal line

### 📦 Step 4: Install Required Packages

Once your virtual environment is activated (you should see `(venv)` at the beginning of your command line):

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
   This will install all the necessary components the tool needs to work.

## 🔑 Getting Your Figma Access Token

Before you can use the tool, you need to create an access token in Figma:

1. Log in to your Figma account on [figma.com](https://www.figma.com/)
2. Click on your profile picture in the top-right corner
3. Select "Settings" from the dropdown menu
4. Scroll down to "Personal access tokens" section
5. Click "Create a new personal access token"
6. Give it a name like "Data Extractor Tool"
7. Click "Create token"
8. ⚠️ **IMPORTANT**: Copy your token immediately and save it somewhere safe! You won't be able to see it again.

## 🏢 Setting Up Your Team IDs

You need to identify which Figma teams you want to extract data from:

1. Go to your Figma homepage after logging in
2. Click on a team in the left sidebar
3. Look at the URL in your browser. It will look something like:
   ```
   https://www.figma.com/files/team/1234567890123456789/Team-Name
   ```
4. The long number after `/team/` is your team ID (in this example: `1234567890123456789`)
5. Open the `team_ids` file in a text editor (Notepad, TextEdit, etc.)
6. Add one team ID per line (remove any existing example IDs)
7. Save the file

## ▶️ Running the Tool

Now you're ready to run the tool!

### 🔐 Step 1: Set Your Figma Token

#### Windows 🪟
In Command Prompt (with your virtual environment activated):
```
set FIGMA_ACCESS_TOKEN=your-token-here
```

#### macOS/Linux 🍎🐧
In Terminal (with your virtual environment activated):
```
export FIGMA_ACCESS_TOKEN="your-token-here"
```

### 🚀 Step 2: Run the Script

With your virtual environment still activated:

```
python figma-api.py
```

The tool will start running and show colorful progress updates. It will:
1. 🔄 Connect to Figma using your token
2. 📖 Read your team IDs from the file
3. 📥 Fetch information about each team
4. 📁 Download details about all projects in each team
5. 🎨 Gather information about all files in those projects
6. 💾 Save everything to a JSON file in a new `data` folder

### 📂 Step 3: Find Your Results

When the tool finishes:

1. Look for a new `data` folder in your figma-api-main directory
2. Inside, you'll find a file named `figma_consolidated_data_[timestamp].json`
3. This file contains all your Figma organization data in a structured format

## ❓ Troubleshooting Common Issues

### 🛠️ "Python is not recognized as a command"
- Windows: Make sure you checked "Add Python to PATH" during installation
- Try using `python3` instead of `python`

### 🛠️ "No module named requests"
- Make sure you've activated your virtual environment (you should see `(venv)` at the start of your command line)
- Try running `pip install -r requirements.txt` again

### 🛠️ "Could not find a version that satisfies the requirement"
- Try updating pip: `pip install --upgrade pip`
- Then try installing requirements again

### 🛠️ "Access denied" or "Permission error"
- Windows: Try running Command Prompt as Administrator
- macOS/Linux: Try adding `sudo` before commands that give permission errors

### 🛠️ "Token not found" or API errors
- Double-check that you've set your Figma token correctly
- Verify your token has access to the teams you're trying to extract

## 📊 What's Inside the JSON File?

The tool creates a JSON file that contains:

- 📝 A summary of what was extracted (number of teams, projects, files)
- 👥 Details about each team
- 📁 All projects within each team
- 🎨 All design files within each project
- ⏱️ Timestamps and other metadata

> **This information can be useful for:**
> - 💾 Creating backups of your Figma organization structure
> - 📈 Analyzing how your design files are organized
> - 📝 Keeping track of file changes over time
> - 🔧 Building custom tools that work with your Figma data

## 💬 Need Help?

If you encounter any issues not covered in the troubleshooting section:
1. 🔍 Check the colored output in your command line for specific error messages
2. ✅ Make sure you've followed all the steps exactly as described
3. 🌐 Try searching online for any specific error messages you see

## 💻 System Requirements

- 🪟 Windows 10 or newer, 🍎 macOS 10.13 or newer, or 🐧 Linux (Ubuntu, Debian, etc.)
- 🌐 Internet connection
- 🐍 Python 3.7 or newer
- 💾 Approximately 100MB of free disk space
- 🔑 A valid Figma account with an access token
