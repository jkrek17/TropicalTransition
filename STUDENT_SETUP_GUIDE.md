# Setup Guide: Tropical Cyclone and Ship Track Visualization Project

## Getting Started

This guide provides step-by-step instructions for setting up the Tropical Cyclone and Ship Track Visualization Project. Please follow these steps in order to ensure a successful installation.

> **💡 Need detailed environment setup?** For comprehensive environment setup instructions for different operating systems, see [`ENVIRONMENT_SETUP.md`](ENVIRONMENT_SETUP.md)

---

## Prerequisites

Before beginning the installation process, please ensure you have:
- A computer running Windows, macOS, or Linux
- Internet connection for downloading required software
- Basic familiarity with computer operations

---

## 1. Installing Python

### Step 1: Download Python
1. Go to [python.org](https://www.python.org/downloads/)
2. Click the big yellow "Download Python" button
3. Choose the latest version (Python 3.11 or 3.12)

### Step 2: Install Python
**Windows:**
1. Run the downloaded `.exe` file
2. **IMPORTANT**: Check the box that says "Add Python to PATH"
3. Click "Install Now"
4. Wait for installation to complete

**macOS:**
1. Run the downloaded `.pkg` file
2. Follow the installation wizard
3. Python should be automatically added to your PATH

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Step 3: Verify Installation
Open a terminal/command prompt and type:
```bash
python --version
```
You should see output similar to "Python 3.11.0"

---

## 2. Installing Visual Studio Code

### Step 1: Download VS Code
1. Go to [code.visualstudio.com](https://code.visualstudio.com/)
2. Click the big blue "Download" button
3. Choose the version for your operating system

### Step 2: Install VS Code
**Windows:**
1. Run the downloaded `.exe` file
2. Follow the installation wizard
3. Make sure to check "Add to PATH" if prompted

**macOS:**
1. Drag the downloaded `.app` file to your Applications folder
2. Open VS Code from Applications

**Linux:**
```bash
sudo apt install code
```

### Step 3: Install Python Extension
1. Open VS Code
2. Click the Extensions icon on the left sidebar (looks like four squares)
3. Search for "Python"
4. Install the official Python extension by Microsoft
5. Restart VS Code

### Step 4: Install Recommended Extensions for Data Science
The following extensions are highly recommended for Python development and data science work:

**Essential Extensions:**
- **Python** (Microsoft) - Core Python language support
- **Pylance** (Microsoft) - Advanced Python language server with enhanced IntelliSense
- **Python Indent** (Kevin Rose) - Intelligent Python indentation

**Data Science Extensions:**
- **Jupyter** (Microsoft) - Jupyter notebook integration
- **Python Docstring Generator** (Nils Werner) - Automatic docstring generation
- **Python Type Hint** (njpwerner) - Type hint support and validation

**Code Quality Extensions:**
- **Python Preview** (Microsoft) - Visual Python code execution
- **Python Test Explorer** (Little Fox Team) - Test discovery and execution
- **autoDocstring** (Eric Anholt) - Automated docstring generation

**Data Visualization Extensions:**
- **Rainbow CSV** (mechatroner) - Color-coded CSV file viewing
- **Excel Viewer** (GrapeCity) - Excel file viewing within VS Code
- **Markdown All in One** (Yu Zhang) - Enhanced Markdown editing

**Installation Instructions:**
1. Open the VS Code Extensions panel (`Ctrl+Shift+X`)
2. Search for each extension by name
3. Click "Install" for each extension
4. Restart VS Code after installation

---

## 3. Setting Up the Project

### Step 1: Download the Project
1. Download the project files (from your course materials or GitHub)
2. Extract the files to a folder on your computer
3. Open VS Code

### Step 2: Open the Project in VS Code
1. In VS Code, go to `File` → `Open Folder`
2. Navigate to the project folder you extracted
3. Click "Select Folder"
4. You should see the project files in the left sidebar

### Step 3: Set Up Virtual Environment (Recommended)
A virtual environment helps isolate project dependencies and avoid conflicts:

1. **Create a virtual environment**:
```bash
python -m venv .venv
```

2. **Activate the virtual environment**:
   - **Windows (Command Prompt)**:
   ```bash
   .venv\Scripts\activate
   ```
   - **Windows (PowerShell)**:
   ```bash
   .venv\Scripts\Activate.ps1
   ```
   - **macOS/Linux**:
   ```bash
   source .venv/bin/activate
   ```

3. **Verify activation** (you should see `(.venv)` at the beginning of your terminal prompt):
```bash
which python  # macOS/Linux
where python   # Windows
```

### Step 4: Install Project Dependencies
1. Open a terminal in VS Code: `Terminal` → `New Terminal`
2. Make sure you're in the project folder and your virtual environment is activated
3. Run this command:
```bash
pip install -r requirements.txt
```

**Note**: If you encounter permission errors, you may need to upgrade pip first:
```bash
python -m pip install --upgrade pip
```

---

## 4. Running the Project

### Step 1: Verify Your Setup
1. In the VS Code terminal, run:
```bash
python --version
pip list
```
2. You should see Python installed and several packages listed

### Step 2: Execute the Project
1. In the VS Code terminal, run:
```bash
python main.py
```
2. You should see output similar to:
```
🌊 Tropical Cyclone and Ship Track Visualization Project
============================================================
Creating both interactive and static maps...
📊 Processing ship track data...
🚢 Using real ship track data...
```

### Step 3: Examine the Results
1. Navigate to the `output` folder in VS Code
2. You should see the following generated files:
   - `tropical_cyclone_map.html` (interactive map)
   - `tropical_cyclone_map_static.png` (static map)
   - `data_table.png` (data summary)

---

## 5. Examining the Results

### Interactive Map
1. Right-click on `tropical_cyclone_map.html` in VS Code
2. Select "Reveal in File Explorer" (Windows) or "Reveal in Finder" (macOS)
3. Double-click the file to open it in your web browser
4. Explore the interactive features:
   - Click on ship markers for detailed information
   - Use the layer controls to show/hide data layers
   - Experiment with different map background styles

### Static Map
1. Open `tropical_cyclone_map_static.png` in any image viewer
2. This high-quality map is suitable for presentations and reports

### Data Table
1. Open `data_table.png` to view a comprehensive summary of the ship and storm data

### Interactive Jupyter Notebook
The project includes an interactive Jupyter notebook for learning about dateline crossing:
- **File**: `dateline_demo.ipynb`
- **Purpose**: Demonstrates dateline crossing challenges and solutions
- **Usage**: See [JUPYTER_NOTEBOOK_GUIDE.md](JUPYTER_NOTEBOOK_GUIDE.md) for detailed instructions

---

## 6. Troubleshooting Common Issues

### "Python is not recognized"
- **Solution**: Reinstall Python and ensure "Add to PATH" is selected during installation
- **Alternative**: Use `python3` instead of `python` in commands

### "pip is not recognized"
- **Solution**: Install pip separately or use `python -m pip` instead

### "Module not found" errors
- **Solution**: Ensure you have executed `pip install -r requirements.txt`
- **Alternative**: Install missing packages individually:
```bash
pip install pandas geopandas folium matplotlib cartopy
```

### VS Code doesn't show Python
- **Solution**: Install the Python extension and restart VS Code
- **Alternative**: Select Python interpreter manually: `Ctrl+Shift+P` → "Python: Select Interpreter"

### Map files don't appear
- **Solution**: Verify that the script executed without errors
- **Alternative**: Check the `output` folder for any error messages



### Virtual environment issues
- **Solution**: Make sure you've activated your virtual environment before installing packages
- **Check**: Look for `(.venv)` at the beginning of your terminal prompt
- **Deactivate**: Type `deactivate` to exit the virtual environment

### Permission errors when installing packages
- **Solution**: Use `python -m pip install --upgrade pip` to upgrade pip first
- **Alternative**: Use `pip install --user` to install packages for your user only
- **Note**: On some systems, you may need to use `python3` instead of `python`

### Import errors or module not found
- **Solution**: Ensure you're in the correct directory and virtual environment is activated
- **Check**: Verify all files are in the correct folders as shown in the project structure
- **Alternative**: Try running `python -m pip install -r requirements.txt` instead

### Cartopy installation issues
- **Solution**: Cartopy can be tricky to install. Try: `conda install -c conda-forge cartopy` if you have conda
- **Alternative**: Install dependencies first: `pip install numpy matplotlib shapely`
- **Note**: Some systems may require additional system-level dependencies

### Memory or performance issues
- **Solution**: Close other applications while running the visualization
- **Alternative**: Try reducing the data size or map resolution in `config.py`
- **Note**: Large datasets may require more RAM

---

## 7. Next Steps

### Explore the Code
1. Open `main.py` in VS Code
2. Review the code to understand the functionality of each component
3. Experiment with modifying settings in `config.py` to observe their effects on the maps

### Experiment with Your Own Data
1. Add your own ship track CSV files to the `data` folder
2. Execute the project again to visualize your data on the maps
3. Test different map configuration settings

### Further Learning
- Review the `TUTORIAL.md` file for comprehensive project explanations
- Examine the `README.md` for project overview
- Explore online Python and data science tutorials

---

## Completion

You have successfully set up and executed a comprehensive geospatial data science project. This project demonstrates:
- Processing real NOAA storm data
- Analyzing ship tracking information
- Generating interactive and static visualizations
- Utilizing modern Python data science methodologies

