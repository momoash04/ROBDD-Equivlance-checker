# 🧠 ROBDD Visual Checker – Boolean Function Equivalence using BDD & ROBDD

This project is a graphical tool to build and compare Boolean expressions using Binary Decision Diagrams (BDDs) and Reduced Ordered Binary Decision Diagrams (ROBDDs). It allows users to input Boolean expressions, visualize their BDD/ROBDD structures, and determine whether the expressions are logically equivalent.

Designed and implemented using Python, Tkinter, NetworkX, and Matplotlib.

---

## 🧩 Project Overview

🔷 Goal:  
Build and compare BDDs and ROBDDs from Boolean expressions.  
✅ Visualize the structure  
✅ Optimize using ROBDD  
✅ Compare for logical equivalence

📘 Technologies Used:
- Python (3.x)
- tkinter (GUI)
- NetworkX (graph modeling)
- Matplotlib (graph rendering)
- re (regular expressions)

---

## 🔐 Key Concepts

- BDD: A graph representation of Boolean logic, where nodes are decision points and edges represent binary values.
- ROBDD: A reduced form of BDD that:
  - Maintains a fixed variable ordering
  - Merges identical subgraphs
  - Removes redundant nodes
- Variable ordering significantly affects the structure of the diagram.

---

## 🧰 Features

✔️ Build BDDs and ROBDDs from two Boolean expressions  
✔️ Customize variable ordering  
✔️ Interactive GUI with canvas-based visualization  
✔️ Side-by-side NetworkX graph display of ROBDDs  
✔️ Error handling for syntax and logic errors  
✔️ Equivalence checker with success/failure messages

---

## 🖥️ GUI Walkthrough

| Component            | Description |
|----------------------|-------------|
| Expression Inputs     | Two fields to enter Boolean expressions |
| Variable Order Input  | Comma-separated custom variable order (optional) |
| Buttons               | Build BDDs, Build ROBDDs, Check Equivalence, Visualize |
| Canvases              | Display BDD1, BDD2, and ROBDDs |
| Matplotlib Toolbar    | Zoom, Pan, Save, and more for ROBDD plots |

✅ Colors:
- Light Blue = Variable Nodes  
- Green = Terminal Node (1)  
- Red = Terminal Node (0)  
- Dashed lines = "Low" branches (0)

---

## 🧠 Architecture

🧱 Core Classes:

- BDDNode
  - Represents a single node (variable, 0, or 1)
- BDDBuilder
  - Builds and reduces BDDs to ROBDDs
  - Supports drawing and evaluation
- BDDGUI
  - Controls the graphical interface
  - Manages canvas and interaction logic

---

## ⚙️ Core Functions

| Function             | Description |
|----------------------|-------------|
| build_bdd()          | Recursively builds BDD from expression |
| build_robdd()        | Optimizes BDD into ROBDD |
| evaluate_expression()| Evaluates logic for a variable assignment |
| draw_bdd()           | Renders BDD on GUI canvas |
| create_networkx_graph() | Converts structure to a NetworkX graph |
| check_equivalence()  | Compares two ROBDDs for logical equivalence |

---

## ✅ How It Works

1. Enter two Boolean expressions (e.g., A & B | ~C)
2. (Optional) Specify variable order (e.g., A, B, C)
3. Click “Build BDDs” → visual BDDs are shown
4. Click “Check Equivalence & Build ROBDD”  
   → ROBDDs are built and compared  
   → Result displayed

If equivalent: “✔️ Expressions are equivalent”  
If not: “❌ Expressions are not equivalent”

---

## 🧪 Example Use Cases

- Logic optimization  
- Teaching digital design  
- Functional equivalence checking  
- Visual understanding of decision diagrams  
- Verification in EDA and circuit synthesis

---

## 📷 Screenshots

- ✅ Successful BDD/ROBDD display

  ![image](https://github.com/user-attachments/assets/e3cb3c18-848d-4d31-907c-35c3a7614612)
  
- ❌ Error messages for invalid expressions

  ![image](https://github.com/user-attachments/assets/f6e7ebf9-d0c1-4498-8196-679c8fef2bcf)

- 🧩 Interactive ROBDD plot with zoom & save

  ![image](https://github.com/user-attachments/assets/ac57ede9-6043-4557-b2b5-b0e8e2419867)

---

## 📦 How to Run

1. Make sure Python 3.x is installed.
2. Install dependencies:
```bash
pip install matplotlib networkx
