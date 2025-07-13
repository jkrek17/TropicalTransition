# Environment Setup Guide

This guide provides detailed instructions for setting up the development environment for the Tropical Cyclone and Ship Track Visualization Project on different operating systems.

## Table of Contents
- [Windows Setup](#windows-setup)
- [macOS Setup](#macos-setup)
- [Linux Setup](#linux-setup)
- [Virtual Environment Best Practices](#virtual-environment-best-practices)
- [IDE Setup](#ide-setup)
- [Common Issues and Solutions](#common-issues-and-solutions)

---

## Windows Setup

### Python Installation
1. **Download Python**:
   - Go to [python.org](https://www.python.org/downloads/)
   - Download Python 3.8+ (recommended: Python 3.11)
   - **IMPORTANT**: Check "Add Python to PATH" during installation

2. **Verify Installation**:
   ```cmd
   python --version
   pip --version
   ```

### PowerShell Execution Policy (if needed)
If you encounter PowerShell execution policy errors:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Virtual Environment Setup
```cmd
# Create virtual environment
python -m venv .venv

# Activate (Command Prompt)
.venv\Scripts\activate

# Activate (PowerShell)
.venv\Scripts\Activate.ps1

# Verify activation
where python
```

### Install Dependencies
```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## macOS Setup

### Python Installation
1. **Option 1: Using Homebrew (Recommended)**:
   ```bash
   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install Python
   brew install python@3.11
   ```

2. **Option 2: Download from python.org**:
   - Download the macOS installer from [python.org](https://www.python.org/downloads/)
   - Run the installer

### Virtual Environment Setup
```bash
# Create virtual environment
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Verify activation
which python
```

### Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS-Specific Dependencies
If you encounter issues with cartopy or other geospatial libraries:
```bash
# Install PROJ and GEOS using Homebrew
brew install proj geos
```

---

## Linux Setup

### Python Installation

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### CentOS/RHEL/Fedora:
```bash
# CentOS/RHEL
sudo yum install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip
```

### Virtual Environment Setup
```bash
# Create virtual environment
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Verify activation
which python
```

### Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Linux-Specific Dependencies
For geospatial libraries, you may need system packages:
```bash
# Ubuntu/Debian
sudo apt install libproj-dev libgeos-dev libspatialindex-dev

# CentOS/RHEL
sudo yum install proj-devel geos-devel spatialindex-devel
```

---

## Virtual Environment Best Practices

### Why Use Virtual Environments?
- **Isolation**: Keep project dependencies separate
- **Reproducibility**: Ensure consistent environments across systems
- **Conflict Prevention**: Avoid version conflicts between projects
- **Clean Uninstall**: Easy to remove by deleting the folder

### Managing Virtual Environments

#### Creating and Activating
```bash
# Create
python -m venv .venv

# Activate
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows

# Deactivate
deactivate
```

#### Checking Environment Status
```bash
# Check if virtual environment is active
echo $VIRTUAL_ENV            # Linux/macOS
echo %VIRTUAL_ENV%           # Windows

# List installed packages
pip list

# Export current environment
pip freeze > requirements.txt
```

#### Removing Virtual Environment
```bash
# Deactivate first
deactivate

# Remove directory
rm -rf .venv                 # Linux/macOS
rmdir /s .venv               # Windows
```

---

## IDE Setup

### Visual Studio Code (Recommended)
1. **Install VS Code**: Download from [code.visualstudio.com](https://code.visualstudio.com/)

2. **Install Python Extension**:
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "Python" by Microsoft
   - Install the Python extension

3. **Configure Python Interpreter**:
   - Open project folder in VS Code
   - Press Ctrl+Shift+P
   - Type "Python: Select Interpreter"
   - Choose the interpreter from your virtual environment

4. **Recommended Extensions**:
   - **Python** - Core Python support
   - **Jupyter** - Notebook support
   - **Python Docstring Generator** - Auto-generate docstrings
   - **GitLens** - Git integration
   - **autoDocstring** - Documentation helper

### Jupyter Notebook Setup
```bash
# Install Jupyter
pip install jupyter notebook ipywidgets ipykernel

# Create project kernel
python -m ipykernel install --user --name=tropical_cyclone_project

# Start Jupyter
jupyter notebook
```

### PyCharm (Alternative)
1. Download PyCharm from [jetbrains.com](https://www.jetbrains.com/pycharm/)
2. Open project folder
3. Configure Python interpreter to use virtual environment
4. Install required plugins for geospatial development

---

## Common Issues and Solutions

### Python Command Not Found
**Issue**: `python` command not recognized
**Solutions**:
- Windows: Reinstall Python with "Add to PATH" checked
- macOS/Linux: Use `python3` instead of `python`
- Add Python to PATH manually

### Permission Errors
**Issue**: Permission denied when installing packages
**Solutions**:
```bash
# Use --user flag
pip install --user package_name

# Or use virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### Virtual Environment Won't Activate
**Issue**: Virtual environment activation fails
**Solutions**:
- Check file permissions
- Use full path to activation script
- On Windows, try both Command Prompt and PowerShell

### Cartopy Installation Issues
**Issue**: Cartopy fails to install
**Solutions**:
```bash
# Option 1: Use conda (if available)
conda install -c conda-forge cartopy

# Option 2: Install dependencies first
pip install numpy matplotlib shapely
pip install cartopy

# Option 3: Use wheels
pip install --upgrade pip wheel
pip install cartopy
```

### Jupyter Kernel Issues
**Issue**: Jupyter can't find the right Python environment
**Solutions**:
```bash
# Install kernel for virtual environment
python -m ipykernel install --user --name=project_name

# Check available kernels
jupyter kernelspec list

# Remove old kernel
jupyter kernelspec remove project_name
```

### Memory Issues
**Issue**: Out of memory errors during processing
**Solutions**:
- Close other applications
- Reduce data size in config.py
- Use batch processing for large datasets
- Increase virtual memory/swap space

### Network Issues
**Issue**: Cannot download NOAA data
**Solutions**:
- Check internet connection
- Use VPN if behind firewall
- Set `AUTO_DOWNLOAD_STORM_DATA = False` in config.py
- Use sample data instead

---

## Testing Your Setup

### Basic Test
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Test Python
python --version

# Test packages
python -c "import pandas, geopandas, folium, matplotlib; print('All packages imported successfully')"

# Run the project
python main.py
```

### Advanced Test
```bash
# Test global mapping
python test_global_mapping.py

# Test Jupyter notebook
jupyter notebook dateline_demo.ipynb
```

### Expected Results
After successful setup, you should see:
- No import errors
- Generated maps in the `output/` folder
- Jupyter notebook opens and runs without errors
- All dependencies installed without conflicts

---

## Getting Help

If you encounter issues not covered here:
1. Check the [STUDENT_SETUP_GUIDE.md](STUDENT_SETUP_GUIDE.md) for detailed instructions
2. Review the troubleshooting section in the setup guide
3. Ensure your system meets the minimum requirements
4. Try creating a fresh virtual environment
5. Check Python and pip versions are compatible

## System Requirements

### Minimum Requirements
- Python 3.8+
- 4GB RAM
- 2GB free disk space
- Internet connection (for data download)

### Recommended Requirements
- Python 3.11+
- 8GB RAM
- 5GB free disk space
- Fast internet connection
- SSD storage for better performance

---

## Summary

This guide covers environment setup for:
- ✅ Windows, macOS, and Linux
- ✅ Virtual environment management
- ✅ IDE configuration
- ✅ Jupyter notebook setup
- ✅ Common troubleshooting
- ✅ Best practices for Python development

For project-specific instructions, see the [STUDENT_SETUP_GUIDE.md](STUDENT_SETUP_GUIDE.md). 