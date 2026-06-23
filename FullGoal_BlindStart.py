import tkinter as tk
from tkinter import messagebox
import heapq

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kịch bản 3: Mù toàn bộ Start")
        self.root.geometry("850x680")
        self.root.configure(bg="#fdf4ff")

        self.TILE_SIZE = 80
        self.GAP = 5
        self.goal_state = None
        self.true_start = [[1, 2, 3], [4, 0, 5], [7, 8, 6]]
        self.ai_knowledge = [[-1, -1, -1], [-1, -1, -1], [-1, -1, -1]] 
        self.is_running = False
        
        self.create_widgets()
        self.set_default_values()

    def create_widgets(self):
        title_lbl = tk.Label(self.root, text="MÙ HOÀN TOÀN START", font=("Helvetica", 14, "bold"), bg="#fdf4ff", fg="#701a75")
        title_lbl.pack(pady=10)

        input_frame = tk.Frame(self.root, bg="#fdf4ff")
        input_frame.pack(pady=5)

        goal_box = tk.LabelFrame(input_frame, text=" Nhập trạng thái Đích ", font=("Arial", 10, "bold"), bg="#fdf4ff", fg="#701a75")
        goal_box.pack(padx=20)
        self.goal_entries = []
        for i in range(3):
            row_entries = []
            for j in range(3):
                e = tk.Entry(goal_box, width=3, font=("Arial", 16), justify="center", bd=2)
                e.grid(row=i, column=j, padx=6, pady=6)
                row_entries.append(e)
            self.goal_entries.append(row_entries)

        main_layout = tk.Frame(self.root, bg="#fdf4ff")
        main_layout.pack(pady=10, fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_layout, bg="#fdf4ff")
        left_frame.pack(side=tk.LEFT, padx=30)
        tk.Label(left_frame, text="Bản đồ Xuất phát", font=("Arial", 11, "bold"), bg="#fdf4ff").pack()
        self.canvas_start = tk.Canvas(left_frame, width=3*self.TILE_SIZE+4*self.GAP, height=3*self.TILE_SIZE+4*self.GAP, bg="#fae8ff", highlightthickness=0)
        self.canvas_start.pack(pady=5)

        mid_frame = tk.Frame(main_layout, bg="#fdf4ff")
        mid_frame.pack(side=tk.LEFT, padx=30)
        tk.Label(mid_frame, text="Bản đồ Đích đến", font=("Arial", 11, "bold"), bg="#fdf4ff").pack()
        self.canvas_goal = tk.Canvas(mid_frame, width=3*self.TILE_SIZE+4*self.GAP, height=3*self.TILE_SIZE+4*self.GAP, bg="#fae8ff", highlightthickness=0)
        self.canvas_goal.pack(pady=5)

        right_frame = tk.Frame(main_layout, bg="#fdf4ff")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15)
        
        self.btn_solve = tk.Button(right_frame, text=" GIẢI ", font=("Arial", 12, "bold"), bg="#a21caf", fg="white", command=self.start_scanning, padx=8, pady=8)
        self.btn_solve.pack(fill=tk.X, pady=5)

        self.status_label = tk.Label(right_frame, text="Trạng thái: Đang đợi nhập Goal.", font=("Arial", 10, "italic"), bg="#fdf4ff", fg="#701a75", anchor="w")
        self.status_label.pack(fill=tk.X, pady=5)

        self.result_text = tk.Text(right_frame, width=30, height=12, font=("Consolas", 10), bd=2, relief=tk.SUNKEN)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def set_default_values(self):
        g_mat = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        for i in range(3):
            for j in range(3):
                self.goal_entries[i][j].insert(0, str(g_mat[i][j]))
        self.draw_puzzle(self.ai_knowledge, is_start=True)
        self.draw_puzzle(g_mat, is_start=False)

    def read_goal_matrix(self):
        return [[int(self.goal_entries[i][j].get().strip() or 0) for j in range(3)] for i in range(3)]

    def draw_puzzle(self, state, is_start=True, scanning_cell=None):
        canvas = self.canvas_start if is_start else self.canvas_goal
        canvas.delete("all")
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                x1 = j * self.TILE_SIZE + (j + 1) * self.GAP
                y1 = i * self.TILE_SIZE + (i + 1) * self.GAP
                
                is_scanning = (scanning_cell == (i, j))
                outline_color = "#22d3ee" if is_scanning else ("#475569" if val == -1 else "#d946ef")
                width = 4 if is_scanning else 2

                if val == -1:
                    canvas.create_rectangle(x1, y1, x1+self.TILE_SIZE, y1+self.TILE_SIZE, fill="#1e293b", outline=outline_color, width=width)
                    canvas.create_text(x1+self.TILE_SIZE/2, y1+self.TILE_SIZE/2, text="?", font=("Arial", 28, "bold"), fill="#94a3b8")
                elif val != 0:
                    canvas.create_rectangle(x1, y1, x1+self.TILE_SIZE, y1+self.TILE_SIZE, fill="#ffffff", outline=outline_color, width=width)
                    canvas.create_text(x1+self.TILE_SIZE/2, y1+self.TILE_SIZE/2, text=str(val), font=("Arial", 22, "bold"), fill="#4a044e")
                elif val == 0 and is_scanning:
                    canvas.create_rectangle(x1, y1, x1+self.TILE_SIZE, y1+self.TILE_SIZE, fill="#e0f2fe", outline=outline_color, width=width)

    def start_scanning(self):
        if self.is_running: return
        try:
            self.goal_state = self.read_goal_matrix()
            if sorted([n for r in self.goal_state for n in r]) != list(range(9)):
                raise ValueError("Ma trận Goal phải chứa đủ các số từ 0 đến 8")
        except ValueError as ve:
            messagebox.showerror("Lỗi dữ liệu", str(ve))
            return

        self.is_running = True
        self.btn_solve.config(state=tk.DISABLED)
        for i in range(3):
            for j in range(3): self.goal_entries[i][j].config(state=tk.DISABLED)
            
        self.ai_knowledge = [[-1,-1,-1],[-1,-1,-1],[-1,-1,-1]]
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "  quét ma trận xuất phát\n")
        
        self.scan_coords = [(i, j) for i in range(3) for j in range(3)]
        self.scan_index = 0
        self.process_scan()

    def process_scan(self):
        if self.scan_index >= len(self.scan_coords):
            self.result_text.insert(tk.END, "Quét xong\n Chạy thuật toán  A*\n")
            self.draw_puzzle(self.ai_knowledge, is_start=True)
            self.root.after(1000, self.run_astar)
            return

        r, c = self.scan_coords[self.scan_index]
        self.status_label.config(text=f"Đang quét ô ({r}, {c})...")
        self.ai_knowledge[r][c] = self.true_start[r][c]
        self.draw_puzzle(self.ai_knowledge, is_start=True, scanning_cell=(r, c))
        
        self.scan_index += 1
        self.root.after(300, self.process_scan)

    def heuristic(self, state):
        dist = 0
        goal_pos = {self.goal_state[r][c]: (r, c) for r in range(3) for c in range(3)}
        for r in range(3):
            for c in range(3):
                val = state[r][c]
                if val != 0: dist += abs(r - goal_pos[val][0]) + abs(c - goal_pos[val][1])
        return dist

    def find_zero(self, state):
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0: return i, j

    def run_astar(self):
        frontier = [(self.heuristic(self.ai_knowledge), 0, self.ai_knowledge, [])]
        visited = {tuple(tuple(row) for row in self.ai_knowledge)}
        
        while frontier:
            f, g, current, path = heapq.heappop(frontier)
            if current == self.goal_state:
                self.solution_path = path
                self.step_index = 0
                self.execute_step()
                return
            x, y = self.find_zero(current)
            for dx, dy, act in [(-1,0,"UP"), (1,0,"DOWN"), (0,-1,"LEFT"), (0,1,"RIGHT")]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 3 and 0 <= ny < 3:
                    new_state = [row[:] for row in current]
                    new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
                    tup = tuple(tuple(row) for row in new_state)
                    if tup not in visited:
                        visited.add(tup)
                        heapq.heappush(frontier, (g + 1 + self.heuristic(new_state), g + 1, new_state, path + [(new_state, act)]))

    def execute_step(self):
        if self.step_index >= len(self.solution_path):
            self.status_label.config(text="Thành công!")
            self.is_running = False
            self.btn_solve.config(state=tk.NORMAL)
            for i in range(3):
                for j in range(3): self.goal_entries[i][j].config(state=tk.NORMAL)
            return

        next_state, act = self.solution_path[self.step_index]
        self.ai_knowledge = next_state
        self.draw_puzzle(self.ai_knowledge, is_start=True)
        self.status_label.config(text=f"A* Thực thi: {act}")
        self.step_index += 1
        self.root.after(300, self.execute_step)

if __name__ == "__main__":
    app = PuzzleApp(tk.Tk())
    app.root.mainloop()