import tkinter as tk
from tkinter import messagebox, ttk
import re
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from itertools import permutations

class BDDNode:
    def __init__(self, var=None, low=None, high=None, value=None):
        self.var = var
        self.low = low
        self.high = high
        self.value = value

    def is_terminal(self):
        return self.value is not None

    def __eq__(self, other):
        if not isinstance(other, BDDNode):
            return False
        return (self.var == other.var and
                self.low == other.low and
                self.high == other.high and
                self.value == other.value)

    def __hash__(self):
        return hash((self.var, self.low, self.high, self.value))

class BDDBuilder:
    def __init__(self):
        self.node_cache = {}
        self.NODE_RADIUS = 10
        self.TERMINAL_RADIUS = 8
        self.VERTICAL_SPACING = 80
        self.HORIZONTAL_SPACING = 20
        self.EDGE_TEXT_OFFSET_X = 5
        self.EDGE_TEXT_OFFSET_Y = 2

    def build_bdd(self, expression, variables, assignment={}):
        if not variables:
            value = self.evaluate_expression(expression, assignment)
            return BDDNode(value=value)

        current_var = variables[0]
        assignment_false = assignment.copy()
        assignment_false[current_var] = 0
        assignment_true = assignment.copy()
        assignment_true[current_var] = 1

        low_branch = self.build_bdd(expression, variables[1:], assignment_false)
        high_branch = self.build_bdd(expression, variables[1:], assignment_true)

        node = BDDNode(var=current_var, low=low_branch, high=high_branch)
        return node

    def build_robdd(self, bdd_root):
        if bdd_root is None:
            return None

        if bdd_root.is_terminal():
            if bdd_root.value not in self.node_cache:
                self.node_cache[bdd_root.value] = bdd_root
            return self.node_cache[bdd_root.value]

        bdd_root.low = self.build_robdd(bdd_root.low)
        bdd_root.high = self.build_robdd(bdd_root.high)

        if bdd_root.low == bdd_root.high:
            return bdd_root.low

        if bdd_root in self.node_cache:
            return self.node_cache[bdd_root]

        self.node_cache[bdd_root] = bdd_root
        return bdd_root

    def evaluate_expression(self, expression, assignment):
        try:
            eval_expr = expression
            for var, val in assignment.items():
                eval_expr = eval_expr.replace(var, str(val))
            return int(bool(eval(eval_expr)))

        except Exception as e:
            raise ValueError(f"Invalid expression evaluation: {e}")

    def draw_bdd(self, canvas, root, x, y, dx=50, level=0):
        if root is None:
            return

        if root.is_terminal():
            if root.value == 0:
                canvas.create_oval(x - self.TERMINAL_RADIUS, y - self.TERMINAL_RADIUS,
                                    x + self.TERMINAL_RADIUS, y + self.TERMINAL_RADIUS, fill="red")
            else:
                canvas.create_oval(x - self.TERMINAL_RADIUS, y - self.TERMINAL_RADIUS,
                                x + self.TERMINAL_RADIUS, y + self.TERMINAL_RADIUS, fill="lightgreen")
            canvas.create_text(x, y, text=str(int(root.value)))
            return

        canvas.create_oval(x - self.NODE_RADIUS, y - self.NODE_RADIUS, x + self.NODE_RADIUS,
                            y + self.NODE_RADIUS, fill="lightblue")
        canvas.create_text(x, y, text=root.var)

        next_y = y + self.VERTICAL_SPACING
        if root.low:
            canvas.create_line(x, y + self.NODE_RADIUS, x - dx, next_y - self.NODE_RADIUS, arrow=tk.LAST, dash=(2, 2))
            text_x = x - dx/2
            text_y = (y+self.NODE_RADIUS+ next_y - self.NODE_RADIUS)/2
            canvas.create_text(text_x - self.EDGE_TEXT_OFFSET_X, text_y - self.EDGE_TEXT_OFFSET_Y, text="0")
            self.draw_bdd(canvas, root.low, x - dx, next_y, dx // 2, level + 1)
        if root.high:
            canvas.create_line(x, y + self.NODE_RADIUS, x + dx, next_y - self.NODE_RADIUS, arrow=tk.LAST)
            text_x = x + dx / 2
            text_y = (y + self.NODE_RADIUS + next_y - self.NODE_RADIUS) / 2
            canvas.create_text(text_x + self.EDGE_TEXT_OFFSET_X, text_y - self.EDGE_TEXT_OFFSET_Y, text="1")
            self.draw_bdd(canvas, root.high, x + dx, next_y, dx // 2, level + 1)

    def create_networkx_graph(self, root, graph_type):
        graph = nx.DiGraph()
        node_queue = [(root, 0)]  # Include the level as part of the queue
        visited = {}

        while node_queue:
            node, level = node_queue.pop(0)

            if node in visited:
                continue
            visited[node] = level

            # Determine the node color (blue for regular, red or green for terminal nodes)
            if node.low is None and node.high is None:  # Terminal node
                color = 'red' if node.value == 0 else 'green'
                label = str(node.value)  # Explicitly set label as "0" or "1"
            else:
                color = 'lightblue'
                label = node.var if node.var else str(node.value)

            # Add the node with color and level as attributes
            graph.add_node(
                node, 
                subset_key=level, 
                label=label,  # Assign label for nodes
                color=color
            )

            if node.low is not None:
                # Add an edge for the low branch
                graph.add_edge(node, node.low, label='0', color='red')
                node_queue.append((node.low, level + 1))

            if node.high is not None:
                # Add an edge for the high branch
                graph.add_edge(node, node.high, label='1', color='green')
                node_queue.append((node.high, level + 1))
        
        return graph

            



class BDDGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BDD and ROBDD Visualizer")
        root.configure(bg="gray25")
        self.builder = BDDBuilder()
        self.nx_graph = None
        self.fig = None
        self.toplevel = None

        # Variables for storing expressions and selected orders
        self.expression1_var = tk.StringVar()
        self.expression2_var = tk.StringVar()
        self.selected_order1 = tk.StringVar()
        self.selected_order2 = tk.StringVar()

        # Input for boolean expressions
        tk.Label(root, text="Boolean Expression 1 (e.g., A & B | ~C):", bg="black", fg="white").pack()
        self.expression1_entry = tk.Entry(root, width=50, textvariable=self.expression1_var)
        self.expression1_entry.pack()

        tk.Label(root, text="Boolean Expression 2 (e.g., A & B | ~C):", bg="black", fg="white").pack()
        self.expression2_entry = tk.Entry(root, width=50, textvariable=self.expression2_var)
        self.expression2_entry.pack()

        # Frame for dropdown 1
        dropdown1_frame = tk.Frame(root, bg="gray25")
        dropdown1_frame.pack(pady=5)

        # Label for the first dropdown list
        tk.Label(dropdown1_frame, text="Variable Order 1:", bg="black", fg="white").pack(side="left", padx=5)

        # Dropdown menu for variable ordering of expression 1 
        self.order_options1 = ttk.Combobox(root, textvariable=self.selected_order1, state="readonly", width=47)
        self.order_options1.pack(pady=5)  

        # Frame for dropdown 2
        dropdown2_frame = tk.Frame(root, bg="gray25")
        dropdown2_frame.pack(pady=5)

        # Label for the second dropdown list
        tk.Label(dropdown2_frame, text="Variable Order 2:", bg="black", fg="white").pack(side="left", padx=5)

        # Dropdown menu for variable ordering of expression 2 
        self.order_options2 = ttk.Combobox(root, textvariable=self.selected_order2, state="readonly", width=47)
        self.order_options2.pack(pady=5)  

        # Bind event to update dropdown when expressions change
        self.expression1_var.trace("w", self.update_dropdowns)
        self.expression2_var.trace("w", self.update_dropdowns)

        # Buttons
        tk.Button(root, text="Build BDDs", bg="black", fg="white", activebackground="#D25A3E", command=self.build_bdds).pack(pady=5)
        tk.Button(root, text="Check Equivalence and Build ROBDD", bg="black", fg="white", activebackground="#D25A3E", command=self.check_equivalence).pack(pady=5)
        tk.Button(root, text="Quit", bg="maroon", fg="white", command=root.quit).pack(pady=5)

        # Frames and canvases for BDDs
        self.frame1 = tk.Frame(root)
        self.frame1.pack(side="left", padx=10)
        self.frame2 = tk.Frame(root)
        self.frame2.pack(side="right", padx=10)

        self.canvas1 = tk.Canvas(self.frame1, width=750, height=700, bg="gray", highlightbackground="gray24")
        self.canvas1.pack()
        self.canvas2 = tk.Canvas(self.frame2, width=750, height=700, bg="gray", highlightbackground="gray24")
        self.canvas2.pack()

        # Frame and canvas for ROBDD
        self.robdd_frame = tk.Frame(root)
        self.robdd_frame.pack(side="left", padx=10)
        self.robdd_canvas = tk.Canvas(self.robdd_frame, width=800, height=800, bg="black")
        self.robdd_canvas.pack()

        self.bdd1_root = None
        self.bdd2_root = None
        self.robdd1_root = None
        self.robdd2_root = None

    def extract_variables(self, expression):
        expression = self.normalize_expression(expression)
        return sorted(set(re.findall(r'\b[a-zA-Z_]\w*\b', expression)) - {"and", "or", "not", "True", "False"})

    def normalize_expression(self, expression):
        expression = expression.replace("~", "not ").replace("&", " and ").replace("|", " or ")
        return expression

    def update_dropdowns(self, *args):
        expression1 = self.expression1_entry.get().upper()
        expression2 = self.expression2_entry.get().upper()

        variables1 = self.extract_variables(expression1)
        variables2 = self.extract_variables(expression2)

        self.update_order_options(self.order_options1, variables1)
        self.update_order_options(self.order_options2, variables2)

    def update_order_options(self, combobox, variables):
        if variables:
            orders = [" ".join(perm) for perm in permutations(variables)]
            combobox['values'] = orders
            combobox.current(0)  # Select the first permutation by default
        else:
            combobox['values'] = []
            combobox.set('')

    def build_bdds(self):
        expression1 = self.expression1_entry.get().upper()
        expression2 = self.expression2_entry.get().upper()
        selected_order1 = self.selected_order1.get().split()
        selected_order2 = self.selected_order2.get().split()

        if not expression1 or not expression2:
            messagebox.showerror("Error", "Please enter two Boolean expressions.")
            return

        normalized_expression1 = self.normalize_expression(expression1)
        normalized_expression2 = self.normalize_expression(expression2)

        variables1 = self.extract_variables(normalized_expression1)
        variables2 = self.extract_variables(normalized_expression2)

        if not variables1 or not variables2:
            messagebox.showerror("Error", "No variables found in one or both of the expressions.")
            return

        # Use the selected order for building BDDs
        variables1 = selected_order1 if selected_order1 else variables1
        variables2 = selected_order2 if selected_order2 else variables2

        try:
            # Build the BDDs with the selected variable order
            self.bdd1_root = self.builder.build_bdd(normalized_expression1, variables1)
            self.bdd2_root = self.builder.build_bdd(normalized_expression2, variables2)

            # Clear existing drawings
            self.canvas1.delete("all")
            self.canvas2.delete("all")
            self.robdd_canvas.delete("all")

            # Draw the BDDs
            self.builder.draw_bdd(self.canvas1, self.bdd1_root, 400, 50, dx=150)
            self.builder.draw_bdd(self.canvas2, self.bdd2_root, 400, 50, dx=150)

            messagebox.showinfo("Success", "BDDs Built and Displayed with selected variable order.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def check_equivalence(self):
        if not self.bdd1_root or not self.bdd2_root:
            messagebox.showerror("Error", "Please build the BDDs first.")
            return

        try:
            # Reset the builder's cache and build ROBDDs
            self.builder.node_cache = {}
            self.robdd1_root = self.builder.build_robdd(self.bdd1_root)
            self.builder.node_cache = {}
            self.robdd2_root = self.builder.build_robdd(self.bdd2_root)

            # Convert ROBDDs to NetworkX graphs
            graph1 = self.builder.create_networkx_graph(self.robdd1_root, 1)
            graph2 = self.builder.create_networkx_graph(self.robdd2_root, 2)

            # Compare equivalence
            def compare_nodes(node1, node2):
                if node1 is None and node2 is None:
                    return True
                if node1 is None or node2 is None:
                    return False
                if node1.is_terminal() and node2.is_terminal():
                    return node1.value == node2.value
                return compare_nodes(node1.low, node2.low) and compare_nodes(node1.high, node2.high)

            if compare_nodes(self.robdd1_root, self.robdd2_root):
                messagebox.showinfo("Equivalence Check", "The two boolean functions are equivalent.")
            else:
                messagebox.showinfo("Equivalence Check", "The two boolean functions are not equivalent.")

            # Visualize the graphs
            self.show_matplotlib_graph(graph1, graph2)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to build ROBDDs or check equivalence: {e}")

    def show_matplotlib_graph(self, nx_graph1, nx_graph2, graph_type="Default_Type"):
        try:
            pos1 = nx.multipartite_layout(nx_graph1, subset_key="subset_key")
            pos2 = nx.multipartite_layout(nx_graph2, subset_key="subset_key")
        except Exception as e:
            print(f"Layout Error: {e}")
            pos1 = nx.spring_layout(nx_graph1)
            pos2 = nx.spring_layout(nx_graph2)

        if self.fig:
            plt.close(self.fig)

        self.fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        self.fig.canvas.manager.set_window_title("ROBDD Graphs Display")

        # Extract node attributes for labels and ensure they are correct
        labels1 = {node: data['label'] for node, data in nx_graph1.nodes(data=True)}
        labels2 = {node: data['label'] for node, data in nx_graph2.nodes(data=True)}

        # Draw Graph 1
        node_colors1 = [data['color'] for _, data in nx_graph1.nodes(data=True)]
        edge_colors1 = [data['color'] for _, _, data in nx_graph1.edges(data=True)]

        nx.draw(
            nx_graph1,
            pos=pos1,
            with_labels=True,
            ax=ax1,
            labels=labels1,  # Ensure the correct labels are passed
            node_color=node_colors1,
            edge_color=edge_colors1,
            edge_cmap=plt.cm.Reds
        )
        ax1.set_title(f"ROBDD of Boolean expression 1")

        # Draw Graph 2
        node_colors2 = [data['color'] for _, data in nx_graph2.nodes(data=True)]
        edge_colors2 = [data['color'] for _, _, data in nx_graph2.edges(data=True)]

        nx.draw(
            nx_graph2,
            pos=pos2,
            with_labels=True,
            ax=ax2,
            labels=labels2,  # Ensure the correct labels are passed
            node_color=node_colors2,
            edge_color=edge_colors2,
            edge_cmap=plt.cm.Greens
        )
        ax2.set_title(f"ROBDD of Boolean expression 2")

        plt.show()
        canvas = FigureCanvasTkAgg(self.fig, master=self.robdd_canvas)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()
        canvas.draw()
        plt.show(block=False)  # Kept to avoid problems with canvas refresh

if __name__ == "__main__":
    root = tk.Tk()
    app = BDDGUI(root)
    root.mainloop()