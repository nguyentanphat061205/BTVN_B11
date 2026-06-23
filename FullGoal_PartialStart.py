import tkinter as tk
from tkinter import messagebox
import heapq
import random

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kịch bản 2: Start bị mờ 1 phần ")
        self.root.geometry("850x680")
        self.root.configure(bg="#fffbeb")

        self.TILE_SIZE = 80
        self.GAP = 5
        self.goal_state = None
        self.current_state = None
        self.is_running = False
        
        self.create_widgets()
        self.set_default_values()

    def create_widgets(self):
        title_lbl = tk.Label(self.root, text="THẤY GOAL, START BỊ MỜ 1 PHẦN ", font=("Helvetica", 14, "bold"), bg="#fffbeb", fg="#92400e")
        title_lbl.pack(pady=10)

        input_frame = tk.Frame(self.root, bg="#fffbeb")
        input_frame.pack(pady=5)

        init_box = tk.LabelFrame(input_frame, text=" Trạng thái xuất phát ", font=("Arial", 10, "bold"), bg="#fffbeb", fg="#92400e")
        init_box.grid(row=0, column=0, padx=15)
        self.start_entries = []
        for i in range(3):
            row_e = []
            for j in range(3):
                e = tk.Entry(init_box, width=3, font=("Arial", 14), justify="center")
                e.grid(row=i, column=j, padx=4, pady=4)
                row_e.append(e)
            self.start_entries.append(row_e)

        goal_box = tk.LabelFrame(input_frame, text=" Trạng thái đích đến ", font=("Arial", 10, "bold"), bg="#fffbeb", fg="#92400e")
        goal_box.grid(row=0, column=1, padx=15)
        self.goal_entries = []
        for i in range(3):
            row_e = []
            for j in range(3):
                e = tk.Entry(goal_box, width=3, font=("Arial", 14), justify="center")
                e.grid(row=i, column=j, padx=4, pady=4)
                row_e.append(e)
            self.goal_entries.append(row_e)

        main_layout = tk.Frame(self.root, bg="#fffbeb")
        main_layout.pack(pady=10, fill=tk.BOTH, expand=True)
        container_start = tk.Frame(main_layout, bg="#fef3c7", padx=4, pady=4)
        container_start.pack(side=tk.LEFT, padx=35)
        self.canvas_start = tk.Canvas(container_start, width=3*self.TILE_SIZE+4*self.GAP, height=3*self.TILE_SIZE+4*self.GAP, bg="#fff7ed", highlightthickness=0)
        self.canvas_start.pack()

        container_goal = tk.Frame(main_layout, bg="#fef3c7", padx=4, pady=4)
        container_goal.pack(side=tk.LEFT, padx=35)
        self.canvas_goal = tk.Canvas(container_goal, width=3*self.TILE_SIZE+4*self.GAP, height=3*self.TILE_SIZE+4*self.GAP, bg="#fff7ed", highlightthickness=0)
        self.canvas_goal.pack()

        right_frame = tk.Frame(main_layout, bg="#fffbeb")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15)
        
        self.btn_solve = tk.Button(
            right_frame, text=" GIẢI ", font=("Arial", 11, "bold"), 
            bg="#d97706", fg="white", activebackground="#15803d", activeforeground="white",
            command=self.trigger_blur_phase, padx=5, pady=5
        )
        self.btn_solve.pack(fill=tk.X, pady=5)

        self.status_label = tk.Label(right_frame, text="Trạng thái: Sẵn sàng.", font=("Arial", 10, "italic"), bg="#fffbeb", fg="#92400e", anchor="w")
        self.status_label.pack(fill=tk.X, pady=5)

        self.result_text = tk.Text(right_frame, width=30, height=12, font=("Consolas", 10), bd=2, relief=tk.SUNKEN)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def set_default_values(self):
        s_mat = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        g_mat = [[1, 2, 3], [4, 5, 0], [7, 8, 6]]
        for i in range(3):
            for j in range(3):
                self.start_entries[i][j].insert(0, str(s_mat[i][j]))
                self.goal_entries[i][j].insert(0, str(g_mat[i][j]))
        self.draw_puzzle(s_mat, is_start=True)
        self.draw_puzzle(g_mat, is_start=False)

    def read_matrices(self):
        s_mat = [[int(self.start_entries[i][j].get().strip() or 0) for j in range(3)] for i in range(3)]
        g_mat = [[int(self.goal_entries[i][j].get().strip() or 0) for j in range(3)] for i in range(3)]
        return s_mat, g_mat

    def draw_puzzle(self, state, is_start=True):
        canvas = self.canvas_start if is_start else self.canvas_goal
        canvas.delete("all")
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                x1 = j * self.TILE_SIZE + (j + 1) * self.GAP
                y1 = i * self.TILE_SIZE + (i + 1) * self.GAP
                x2 = x1 + self.TILE_SIZE
                y2 = y1 + self.TILE_SIZE
                
                if val == -1: 
                    canvas.create_rectangle(x1, y1, x2, y2, fill="#6b7280", outline="#374151", width=2)
                    canvas.create_text((x1 + x2)/2, (y1 + y2)/2, text="?", font=("Arial", 28, "bold"), fill="#ffffff")
                elif val != 0:
                    canvas.create_rectangle(x1, y1, x2, y2, fill="#ffffff", outline="#f59e0b", width=2)
                    canvas.create_text((x1 + x2)/2, (y1 + y2)/2, text=str(val), font=("Arial", 22, "bold"), fill="#92400e")

    def is_solvable(self, start, goal):
        def count_inv(st):
            flat = [num for row in st for num in row if num != 0]
            return sum(1 for i in range(len(flat)) for j in range(i + 1, len(flat)) if flat[i] > flat[j])
        return (count_inv(start) % 2) == (count_inv(goal) % 2)

    def trigger_blur_phase(self):
        
        if self.is_running: return
        try:
            s_mat, g_mat = self.read_matrices()
            if sorted([n for r in s_mat for n in r]) != list(range(9)) or sorted([n for r in g_mat for n in r]) != list(range(9)):
                raise ValueError("Cả hai ma trận phải chứa đủ các số từ 0 đến 8")
        except ValueError as ve:
            messagebox.showerror("Lỗi dữ liệu", str(ve))
            return

        self.is_running = True
        self.btn_solve.config(state=tk.DISABLED)
        self.goal_state = g_mat
        self.draw_puzzle(self.goal_state, is_start=False)

        non_zero_coords = [(i,j) for i in range(3) for j in range(3) if s_mat[i][j] != 0]
        self.hidden_coords = random.sample(non_zero_coords, 2)
        self.hidden_numbers = [s_mat[r][c] for r, c in self.hidden_coords]
        self.blurred_start = [row[:] for row in s_mat]
        for r, c in self.hidden_coords: 
            self.blurred_start[r][c] = -1
        
        self.draw_puzzle(self.blurred_start, is_start=True)
        self.canvas_start.config(bg="#e5e7eb") 
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, " Đã che ngẫu nhiên 2 ô.\n")
        self.status_label.config(text="Trạng thái: Đang phân tích ô bị che")

        self.root.after(1500, self.start_deduction)

    def start_deduction(self):
        self.result_text.insert(tk.END, " bắt đầu khôi phục Belief State\n")
        state_A = [row[:] for row in self.blurred_start]
        state_A[self.hidden_coords[0][0]][self.hidden_coords[0][1]] = self.hidden_numbers[0]
        state_A[self.hidden_coords[1][0]][self.hidden_coords[1][1]] = self.hidden_numbers[1]

        if self.is_solvable(state_A, self.goal_state):
            self.current_state = state_A
        else:
            state_B = [row[:] for row in self.blurred_start]
            state_B[self.hidden_coords[0][0]][self.hidden_coords[0][1]] = self.hidden_numbers[1]
            state_B[self.hidden_coords[1][0]][self.hidden_coords[1][1]] = self.hidden_numbers[0]
            self.current_state = state_B

        self.canvas_start.config(bg="#fff7ed") 
        self.result_text.insert(tk.END, "-> Khôi phục  trạng thái  dựa trên tính Parity\n")
        self.root.after(1000, self.run_astar)

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
        frontier = [(self.heuristic(self.current_state), 0, self.current_state, [])]
        visited = {tuple(tuple(row) for row in self.current_state)}
        
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
            self.status_label.config(text="Đã giải xog!")
            self.is_running = False
            self.btn_solve.config(state=tk.NORMAL)
            return
        next_state, act = self.solution_path[self.step_index]
        self.current_state = next_state
        self.draw_puzzle(self.current_state, is_start=True)
        self.status_label.config(text=f"A* Di chuyển: {act} (Bước {self.step_index + 1})")
        self.step_index += 1
        self.root.after(400, self.execute_step)

if __name__ == "__main__":
    app = PuzzleApp(tk.Tk())
    app.root.mainloop()