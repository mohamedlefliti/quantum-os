import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cirq
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os

class QuantumGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Advanced Quantum Computing Interface")
        self.root.geometry("1000x800")
        
        self.simulator = cirq.Simulator()
        self.current_circuit = []
        self.measurement_results = {}
        self.setup_gui()
        
    def setup_gui(self):
        # Create main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Circuit Designer Tab
        circuit_frame = ttk.Frame(self.notebook)
        self.notebook.add(circuit_frame, text='Circuit Designer')
        self.setup_circuit_designer(circuit_frame)
        
        # Results Viewer Tab
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text='Results Viewer')
        self.setup_results_viewer(results_frame)
        
        # Algorithm Library Tab
        algorithm_frame = ttk.Frame(self.notebook)
        self.notebook.add(algorithm_frame, text='Algorithm Library')
        self.setup_algorithm_library(algorithm_frame)
        
        # Noise Simulator Tab
        noise_frame = ttk.Frame(self.notebook)
        self.notebook.add(noise_frame, text='Noise Simulator')
        self.setup_noise_simulator(noise_frame)
        
        # Menu Bar
        self.setup_menu()
        
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Circuit", command=self.clear_circuit)
        file_menu.add_command(label="Save Circuit", command=self.save_circuit)
        file_menu.add_command(label="Load Circuit", command=self.load_circuit)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Circuit Analyzer", command=self.analyze_circuit)
        tools_menu.add_command(label="State Tomography", command=self.state_tomography)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Tutorial", command=self.show_tutorial)
        help_menu.add_command(label="About", command=self.show_about)
        
    def setup_circuit_designer(self, parent):
        # Left Panel - Gates
        gate_frame = ttk.LabelFrame(parent, text="Quantum Gates")
        gate_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        # Single Qubit Gates
        ttk.Label(gate_frame, text="Single Qubit Gates").pack(pady=5)
        single_gates = ['H', 'X', 'Y', 'Z', 'T', 'S']
        for gate in single_gates:
            btn = ttk.Button(
                gate_frame,
                text=gate,
                command=lambda g=gate: self.add_gate(g)
            )
            btn.pack(pady=2, padx=5, fill='x')
            
        ttk.Separator(gate_frame, orient='horizontal').pack(fill='x', pady=5)
            
        # Two Qubit Gates
        ttk.Label(gate_frame, text="Two Qubit Gates").pack(pady=5)
        two_gates = ['CNOT', 'SWAP', 'CZ']
        for gate in two_gates:
            btn = ttk.Button(
                gate_frame,
                text=gate,
                command=lambda g=gate: self.add_gate(g)
            )
            btn.pack(pady=2, padx=5, fill='x')
            
        # Qubit Selection
        ttk.Separator(gate_frame, orient='horizontal').pack(fill='x', pady=5)
        ttk.Label(gate_frame, text="Target Qubit").pack(pady=5)
        self.target_qubit = ttk.Spinbox(gate_frame, from_=0, to=4, width=5)
        self.target_qubit.pack(pady=2)
        
        # Right Panel - Circuit Display and Controls
        right_frame = ttk.Frame(parent)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # Circuit Display
        circuit_frame = ttk.LabelFrame(right_frame, text="Current Circuit")
        circuit_frame.pack(fill='both', expand=True, pady=5)
        
        self.circuit_text = tk.Text(circuit_frame, height=15)
        self.circuit_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Control Buttons
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            control_frame,
            text="Run Circuit",
            command=self.run_circuit
        ).pack(side='left', padx=5)
        
        ttk.Button(
            control_frame,
            text="Clear Circuit",
            command=self.clear_circuit
        ).pack(side='left', padx=5)
        
        ttk.Button(
            control_frame,
            text="Visualize Circuit",
            command=self.visualize_circuit
        ).pack(side='left', padx=5)
        
        # Number of Shots
        ttk.Label(control_frame, text="Shots:").pack(side='left', padx=5)
        self.shots_var = tk.StringVar(value="1000")
        ttk.Entry(
            control_frame,
            textvariable=self.shots_var,
            width=8
        ).pack(side='left', padx=5)
        
    def setup_algorithm_library(self, parent):
        # Algorithm List
        algorithms_frame = ttk.LabelFrame(parent, text="Quantum Algorithms")
        algorithms_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        algorithms = [
            "Bell State",
            "GHZ State",
            "Quantum Fourier Transform",
            "Grover's Algorithm",
            "Quantum Teleportation"
        ]
        
        for algo in algorithms:
            ttk.Button(
                algorithms_frame,
                text=algo,
                command=lambda a=algo: self.load_algorithm(a)
            ).pack(pady=2, padx=5, fill='x')
            
        # Algorithm Description
        desc_frame = ttk.LabelFrame(parent, text="Algorithm Description")
        desc_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        self.algo_desc = tk.Text(desc_frame, wrap=tk.WORD)
        self.algo_desc.pack(fill='both', expand=True, padx=5, pady=5)
        
    def setup_noise_simulator(self, parent):
        # Noise Parameters
        params_frame = ttk.LabelFrame(parent, text="Noise Parameters")
        params_frame.pack(fill='x', padx=5, pady=5)
        
        # Decoherence Time T1
        ttk.Label(params_frame, text="T1 (μs):").grid(row=0, column=0, padx=5, pady=5)
        self.t1_var = tk.StringVar(value="100")
        ttk.Entry(
            params_frame,
            textvariable=self.t1_var,
            width=10
        ).grid(row=0, column=1, padx=5, pady=5)
        
        # Dephasing Time T2
        ttk.Label(params_frame, text="T2 (μs):").grid(row=1, column=0, padx=5, pady=5)
        self.t2_var = tk.StringVar(value="50")
        ttk.Entry(
            params_frame,
            textvariable=self.t2_var,
            width=10
        ).grid(row=1, column=1, padx=5, pady=5)
        
        # Gate Error Rate
        ttk.Label(params_frame, text="Gate Error (%):").grid(row=2, column=0, padx=5, pady=5)
        self.error_var = tk.StringVar(value="0.1")
        ttk.Entry(
            params_frame,
            textvariable=self.error_var,
            width=10
        ).grid(row=2, column=1, padx=5, pady=5)
        
        # Apply Noise Button
        ttk.Button(
            params_frame,
            text="Apply Noise Model",
            command=self.apply_noise_model
        ).grid(row=3, column=0, columnspan=2, pady=10)
        
    def add_gate(self, gate_name):
        target = self.target_qubit.get()
        self.current_circuit.append((gate_name, int(target)))
        self.update_circuit_display()
        
    def update_circuit_display(self):
        self.circuit_text.delete('1.0', 'end')
        for gate, target in self.current_circuit:
            self.circuit_text.insert('end', f"{gate} on q{target}\n")
            
    def save_circuit(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".qc",
            filetypes=[("Quantum Circuit", "*.qc")]
        )
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(self.current_circuit, f)
                
    def load_circuit(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Quantum Circuit", "*.qc")]
        )
        if file_path:
            with open(file_path, 'r') as f:
                self.current_circuit = json.load(f)
                self.update_circuit_display()
                
    def analyze_circuit(self):
        if not self.current_circuit:
            messagebox.showinfo("Analysis", "No circuit to analyze")
            return
            
        analysis = {
            "Circuit Depth": len(self.current_circuit),
            "Gate Count": len(self.current_circuit),
            "Qubit Count": len(set(t for _, t in self.current_circuit))
        }
        
        msg = "Circuit Analysis:\n\n"
        for key, value in analysis.items():
            msg += f"{key}: {value}\n"
            
        messagebox.showinfo("Circuit Analysis", msg)
        
    def state_tomography(self):
        messagebox.showinfo(
            "State Tomography",
            "This feature will perform quantum state tomography on the current circuit."
        )
        
    def show_tutorial(self):
        tutorial = """
Quantum Circuit Designer Tutorial:

1. Select gates from the left panel
2. Choose target qubit(s)
3. Add gates to your circuit
4. Run the circuit to see results
5. Use the noise simulator to test circuit robustness
6. Save your circuits for later use

For more help, visit our documentation.
"""
        messagebox.showinfo("Tutorial", tutorial)
        
    def show_about(self):
        about_text = """
Quantum Computing Interface v1.0

A comprehensive quantum circuit design and simulation tool.
Created for educational and research purposes.

 2024 Quantum Computing Lab
"""
        messagebox.showinfo("About", about_text)
        
    def run_circuit(self):
        try:
            # Create qubits
            num_qubits = max(t for _, t in self.current_circuit) + 1
            qubits = cirq.LineQubit.range(num_qubits)
            
            # Create circuit
            circuit = cirq.Circuit()
            for gate_name, target in self.current_circuit:
                if gate_name == 'H':
                    circuit.append(cirq.H(qubits[target]))
                elif gate_name == 'X':
                    circuit.append(cirq.X(qubits[target]))
                elif gate_name == 'Y':
                    circuit.append(cirq.Y(qubits[target]))
                elif gate_name == 'Z':
                    circuit.append(cirq.Z(qubits[target]))
                elif gate_name == 'T':
                    circuit.append(cirq.T(qubits[target]))
                elif gate_name == 'S':
                    circuit.append(cirq.S(qubits[target]))
                elif gate_name == 'CNOT':
                    if target + 1 < num_qubits:
                        circuit.append(cirq.CNOT(qubits[target], qubits[target + 1]))
                elif gate_name == 'SWAP':
                    if target + 1 < num_qubits:
                        circuit.append(cirq.SWAP(qubits[target], qubits[target + 1]))
                elif gate_name == 'CZ':
                    if target + 1 < num_qubits:
                        circuit.append(cirq.CZ(qubits[target], qubits[target + 1]))
            
            # Add measurements
            circuit.append(cirq.measure(*qubits, key='result'))
            
            # Run simulation
            shots = int(self.shots_var.get())
            results = self.simulator.run(circuit, repetitions=shots)
            self.measurement_results = results.histogram(key='result')
            
            # Display results
            self.notebook.select(1)  # Switch to Results tab
            self.results_text.delete('1.0', 'end')
            self.results_text.insert('end', f"Circuit Results ({shots} shots):\n\n")
            
            total_shots = sum(self.measurement_results.values())
            for bitstring, count in self.measurement_results.items():
                binary = format(bitstring, f'0{num_qubits}b')
                probability = count / total_shots
                self.results_text.insert('end', f"|{binary}⟩: {count} times ({probability:.3f})\n")
            
            # Plot results
            for widget in self.plot_frame.winfo_children():
                widget.destroy()
            
            fig, ax = plt.subplots(figsize=(8, 6))
            states = [format(b, f'0{num_qubits}b') for b in self.measurement_results.keys()]
            probabilities = [count/total_shots for count in self.measurement_results.values()]
            
            ax.bar(states, probabilities)
            ax.set_title('Measurement Results')
            ax.set_xlabel('Quantum States')
            ax.set_ylabel('Probability')
            plt.xticks(rotation=45)
            
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def setup_results_viewer(self, parent):
        # Results Text Area
        self.results_text = tk.Text(parent, height=10)
        self.results_text.pack(fill='x', padx=5, pady=5)
        
        # Plot Frame
        self.plot_frame = ttk.Frame(parent)
        self.plot_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
    def visualize_circuit(self):
        if not self.current_circuit:
            messagebox.showinfo("Visualization", "No circuit to visualize")
            return
            
        # Create circuit for visualization
        num_qubits = max(t for _, t in self.current_circuit) + 1
        qubits = cirq.LineQubit.range(num_qubits)
        circuit = cirq.Circuit()
        
        for gate_name, target in self.current_circuit:
            if gate_name in ['H', 'X', 'Y', 'Z', 'T', 'S']:
                circuit.append(getattr(cirq, gate_name)(qubits[target]))
            elif gate_name in ['CNOT', 'SWAP', 'CZ'] and target + 1 < num_qubits:
                gate = getattr(cirq, gate_name)
                circuit.append(gate(qubits[target], qubits[target + 1]))
        
        # Create new window for circuit diagram
        window = tk.Toplevel(self.root)
        window.title("Circuit Visualization")
        window.geometry("600x400")
        
        # Display circuit as text
        text = tk.Text(window, wrap=tk.NONE)
        text.pack(fill='both', expand=True)
        text.insert('1.0', str(circuit))
        
    def clear_circuit(self):
        """Clear the current circuit and reset the display"""
        self.current_circuit = []
        self.circuit_text.delete('1.0', 'end')
        self.measurement_results = {}
        
        # Clear results if they exist
        if hasattr(self, 'results_text'):
            self.results_text.delete('1.0', 'end')
        
        # Clear plot if it exists
        if hasattr(self, 'plot_frame'):
            for widget in self.plot_frame.winfo_children():
                widget.destroy()
                
    def load_algorithm(self, algorithm_name):
        """Load a predefined quantum algorithm"""
        self.clear_circuit()
        
        if algorithm_name == "Bell State":
            # Create Bell State: H(0), CNOT(0,1)
            self.current_circuit = [
                ('H', 0),
                ('CNOT', 0)
            ]
            self.algo_desc.delete('1.0', 'end')
            self.algo_desc.insert('end', """Bell State:
A fundamental quantum state of two qubits that exhibits quantum entanglement.
Circuit steps:
1. Apply Hadamard (H) gate to first qubit
2. Apply CNOT gate between first and second qubit
Expected outcome: Equal superposition of |00⟩ and |11⟩""")
            
        elif algorithm_name == "GHZ State":
            # Create GHZ State: H(0), CNOT(0,1), CNOT(1,2)
            self.current_circuit = [
                ('H', 0),
                ('CNOT', 0),
                ('CNOT', 1)
            ]
            self.algo_desc.delete('1.0', 'end')
            self.algo_desc.insert('end', """GHZ State:
A maximally entangled state of three qubits.
Circuit steps:
1. Apply Hadamard (H) gate to first qubit
2. Apply CNOT gates to create three-qubit entanglement
Expected outcome: Equal superposition of |000⟩ and |111⟩""")
            
        elif algorithm_name == "Quantum Fourier Transform":
            # Simple 2-qubit QFT: H(0), S(1), CNOT(0,1), H(1)
            self.current_circuit = [
                ('H', 0),
                ('S', 1),
                ('CNOT', 0),
                ('H', 1)
            ]
            self.algo_desc.delete('1.0', 'end')
            self.algo_desc.insert('end', """Quantum Fourier Transform (2-qubit):
Quantum version of the classical discrete Fourier transform.
Circuit steps:
1. Apply Hadamard gates
2. Apply phase rotations
3. Apply controlled operations
Expected outcome: Quantum state representing the Fourier transform""")
            
        elif algorithm_name == "Grover's Algorithm":
            # Simple 2-qubit Grover: H(0), H(1), X(0), X(1), H(1), CNOT(0,1), H(1), X(0), X(1), H(0), H(1)
            self.current_circuit = [
                ('H', 0), ('H', 1),
                ('X', 0), ('X', 1),
                ('H', 1),
                ('CNOT', 0),
                ('H', 1),
                ('X', 0), ('X', 1),
                ('H', 0), ('H', 1)
            ]
            self.algo_desc.delete('1.0', 'end')
            self.algo_desc.insert('end', """Grover's Algorithm (2-qubit):
Quantum algorithm for searching an unsorted database.
Circuit steps:
1. Initialize superposition
2. Apply oracle (marked state phase flip)
3. Apply diffusion operator
Expected outcome: Amplified amplitude of marked state""")
            
        elif algorithm_name == "Quantum Teleportation":
            # Quantum Teleportation: H(1), CNOT(1,2), CNOT(0,1), H(0), measure
            self.current_circuit = [
                ('H', 1),
                ('CNOT', 1),
                ('CNOT', 0),
                ('H', 0)
            ]
            self.algo_desc.delete('1.0', 'end')
            self.algo_desc.insert('end', """Quantum Teleportation:
Protocol for transmitting quantum states using entanglement.
Circuit steps:
1. Create Bell pair (H + CNOT)
2. Interact source qubit with Bell pair
3. Measure and apply corrections
Expected outcome: State transferred from first to third qubit""")
            
        # Update circuit display
        self.update_circuit_display()
        
    def apply_noise_model(self):
        """Apply noise model to the quantum circuit simulation"""
        try:
            if not self.current_circuit:
                messagebox.showinfo("Noise Simulation", "No circuit to simulate")
                return
                
            # Get noise parameters
            t1 = float(self.t1_var.get())
            t2 = float(self.t2_var.get())
            error_rate = float(self.error_var.get()) / 100.0  # Convert percentage to decimal
            
            # Create noisy simulator
            noise_model = cirq.NoiseModel.from_noise_model_like(
                cirq.depolarize(p=error_rate)
            )
            noisy_simulator = cirq.DensityMatrixSimulator(noise=noise_model)
            
            # Create circuit for simulation
            num_qubits = max(t for _, t in self.current_circuit) + 1
            qubits = cirq.LineQubit.range(num_qubits)
            circuit = cirq.Circuit()
            
            # Add gates with noise
            for gate_name, target in self.current_circuit:
                if gate_name in ['H', 'X', 'Y', 'Z', 'T', 'S']:
                    circuit.append(getattr(cirq, gate_name)(qubits[target]))
                elif gate_name in ['CNOT', 'SWAP', 'CZ'] and target + 1 < num_qubits:
                    gate = getattr(cirq, gate_name)
                    circuit.append(gate(qubits[target], qubits[target + 1]))
                    
            # Add measurements
            circuit.append(cirq.measure(*qubits, key='result'))
            
            # Run noisy simulation
            shots = int(self.shots_var.get())
            results = noisy_simulator.run(circuit, repetitions=shots)
            self.measurement_results = results.histogram(key='result')
            
            # Display results
            self.notebook.select(1)  # Switch to Results tab
            self.results_text.delete('1.0', 'end')
            self.results_text.insert('end', f"Noisy Circuit Results ({shots} shots):\n")
            self.results_text.insert('end', f"T1: {t1} μs, T2: {t2} μs, Error Rate: {error_rate*100}%\n\n")
            
            total_shots = sum(self.measurement_results.values())
            for bitstring, count in self.measurement_results.items():
                binary = format(bitstring, f'0{num_qubits}b')
                probability = count / total_shots
                self.results_text.insert('end', f"|{binary}⟩: {count} times ({probability:.3f})\n")
            
            # Plot noisy results
            for widget in self.plot_frame.winfo_children():
                widget.destroy()
            
            fig, ax = plt.subplots(figsize=(8, 6))
            states = [format(b, f'0{num_qubits}b') for b in self.measurement_results.keys()]
            probabilities = [count/total_shots for count in self.measurement_results.values()]
            
            ax.bar(states, probabilities)
            ax.set_title('Noisy Measurement Results')
            ax.set_xlabel('Quantum States')
            ax.set_ylabel('Probability')
            plt.xticks(rotation=45)
            
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error in noise simulation: {str(e)}")
            
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    gui = QuantumGUI()
    gui.run()
