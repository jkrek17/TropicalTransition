# Jupyter Notebook Guide: Dateline Crossing Demo

This guide provides comprehensive instructions for using the interactive Jupyter notebook that demonstrates dateline crossing challenges and solutions in geospatial data mapping.

## Overview

The `dateline_demo.ipynb` notebook is an interactive educational tool that demonstrates:
- **Dateline crossing challenges** and why they occur
- **Interactive examples** showing correct vs. incorrect handling
- **0-360° coordinate system** approach and its benefits
- **Advanced mapping techniques** for global data visualization
- **Real-world applications** in weather data and shipping

## Prerequisites

Before using the notebook, ensure you have:
- ✅ Python environment set up (see [STUDENT_SETUP_GUIDE.md](STUDENT_SETUP_GUIDE.md))
- ✅ Project dependencies installed: `pip install -r requirements.txt`
- ✅ Jupyter notebook dependencies installed
- ✅ Basic understanding of Python and mapping concepts

## Quick Start

### Option 1: Using VS Code (Recommended)
1. **Open the notebook**: Click on `dateline_demo.ipynb` in the VS Code file explorer
2. **Select kernel**: Choose your project's Python interpreter when prompted
3. **Run cells**: Click the play button next to each cell, or use `Shift + Enter`
4. **View outputs**: Interactive maps and visualizations will display below each cell

### Option 2: Using Jupyter in Browser
1. **Start Jupyter**: In your terminal, run `jupyter notebook`
2. **Navigate**: In the browser interface, click on `dateline_demo.ipynb`
3. **Select kernel**: Choose the appropriate Python kernel
4. **Run cells**: Use `Shift + Enter` or the Run button

## Notebook Structure

The notebook is organized into the following sections:

### 1. Introduction and Problem Statement
- **What is dateline crossing?**
- **Why is it challenging for mapping applications?**
- **Real-world examples** where this occurs

### 2. The Problem with -180/+180 Data
- **Interactive demonstration** of broken tracks
- **Visual examples** of discontinuous lines
- **Code examples** showing the issue

### 3. The Solution: 0-360° System
- **Coordinate system conversion**
- **Benefits of the 0-360° approach**
- **Interactive comparison** between approaches

### 4. Implementation Examples
- **Working code** you can run and modify
- **Step-by-step explanations** of the solution
- **Visual comparisons** of results

### 5. Advanced Techniques
- **Professional mapping approaches**
- **Integration with real data**
- **Best practices** for global mapping

## How to Use This Notebook

### Running the Notebook
1. **Start from the top**: Run cells in order from top to bottom
2. **Read the explanations**: Each cell includes detailed comments
3. **Experiment**: Modify the code to see how changes affect the output
4. **Compare approaches**: Pay attention to the before/after examples

### Interactive Features
- **Folium maps**: Interactive maps you can zoom and pan
- **Code modifications**: Change coordinates and see immediate results
- **Visual comparisons**: Side-by-side examples of correct vs. incorrect approaches

### Learning Objectives
By the end of this notebook, you will understand:
- ✅ **Why dateline crossing is challenging** in geospatial mapping
- ✅ **How coordinate systems affect** map visualization
- ✅ **The 0-360° solution** and when to use it
- ✅ **Implementation techniques** for handling global data
- ✅ **Best practices** for professional mapping applications

## Key Concepts Demonstrated

### Dateline Crossing Issues
```python
# Example of problematic data
track_180 = [
    [170, 30],   # 170°E
    [179, 32],   # 179°E
    [-179, 33],  # 179°W (sudden jump!)
    [-170, 35]   # 170°W
]
```

### The 0-360° Solution
```python
# Convert to 0-360° system
track_360 = [
    [170, 30],   # 170°E
    [179, 32],   # 179°E
    [181, 33],   # 181°E (no jump!)
    [190, 35]    # 190°E
]
```

### Memory Reference
[[memory:3127017]] The notebook demonstrates that Folium/Leaflet.js can handle 0-360° longitude coordinates directly without conversion to -180/+180 range. The conversion examples often shown are unnecessary legacy code.

## Common Workflows

### 1. Learning the Concepts
- Run cells 1-4 to understand the problem
- Focus on the visual comparisons
- Read the explanatory text carefully

### 2. Experimenting with Code
- Modify coordinate values in the examples
- Run cells to see how changes affect visualization
- Try different coordinate ranges

### 3. Applying to Your Data
- Replace sample data with your own coordinates
- Test different coordinate systems
- Observe which approach works best

### 4. Understanding the Theory
- Read the technical explanations
- Study the coordinate transformation code
- Learn about projection systems

## Advanced Usage

### Modifying the Examples
You can customize the notebook by:
- **Changing coordinates**: Replace sample data with your own
- **Adjusting map settings**: Modify zoom levels, center points, styling
- **Adding new examples**: Create additional demonstration cases
- **Testing edge cases**: Try extreme coordinate values

### Creating Your Own Demos
Use the notebook as a template to:
- **Demonstrate other geospatial concepts**
- **Test different mapping libraries**
- **Create educational materials**
- **Develop new visualization techniques**

## Troubleshooting

### Notebook Won't Open
- **Check Jupyter installation**: Run `pip install jupyter notebook ipywidgets`
- **Verify kernel**: Ensure the correct Python interpreter is selected
- **Try VS Code**: Use VS Code's built-in Jupyter support instead

### Maps Don't Display
- **Check widget installation**: Run `pip install ipywidgets`
- **Enable widgets**: In Jupyter, go to Widgets → Enable
- **Restart kernel**: Try restarting the notebook kernel

### Code Errors
- **Run cells in order**: Start from the top and run cells sequentially
- **Check imports**: Ensure all required libraries are imported
- **Reset kernel**: If needed, restart the kernel and run all cells

### Performance Issues
- **Reduce data size**: Use smaller coordinate arrays for testing
- **Close other applications**: Free up system memory
- **Restart notebook**: Clear outputs and restart if sluggish

## Educational Value

This notebook serves as:
- **Interactive tutorial** for geospatial programming
- **Practical demonstration** of coordinate system challenges
- **Code repository** for mapping techniques
- **Learning resource** for data science students
- **Professional reference** for handling global data

## Integration with Project

The notebook connects to the main project by:
- **Demonstrating concepts** used in the main mapping code
- **Providing examples** of the techniques implemented
- **Serving as documentation** for the dateline handling approach
- **Offering educational context** for the project's solutions

## Best Practices

When using this notebook:
1. **Read explanations** before running code
2. **Run cells sequentially** to maintain context
3. **Experiment with modifications** to deepen understanding
4. **Compare visual outputs** to see differences
5. **Apply concepts** to your own data projects

## Next Steps

After completing this notebook:
- ✅ **Run the main project**: Execute `python main.py` to see the concepts in action
- ✅ **Explore the codebase**: Study the implementation in `src/` files
- ✅ **Test with your data**: Use your own coordinates and datasets
- ✅ **Read technical documentation**: Review [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)
- ✅ **Follow the tutorial**: Work through [TUTORIAL.md](TUTORIAL.md)

## Related Documentation

- **[STUDENT_SETUP_GUIDE.md](STUDENT_SETUP_GUIDE.md)** - Environment setup and installation
- **[TUTORIAL.md](TUTORIAL.md)** - Project usage and learning guide
- **[TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)** - Detailed technical implementation
- **[ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)** - Cross-platform setup instructions
- **[CONFIG_GUIDE.md](CONFIG_GUIDE.md)** - Configuration and customization

---

## Summary

The `dateline_demo.ipynb` notebook is a comprehensive educational tool that demonstrates one of the most challenging aspects of geospatial data visualization. Through interactive examples and clear explanations, it provides both theoretical understanding and practical implementation techniques for handling dateline crossing in mapping applications.

**Key takeaway**: [[memory:3127015]] When converting longitudes to a 0-360 system, ensure resulting coordinates are strictly between 0 and 360, with no negative values.

This notebook serves as both a learning resource and a reference guide for implementing robust global mapping solutions in your own projects. 