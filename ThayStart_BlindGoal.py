import tkinter as tk
from tkinter import messagebox
from collections import deque

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kịch bản 1: Thấy Start, Mù Goal ")
        self.root.geometry("850x680")
        self.root.configure(bg="#f8fafc")

        self.TILE_SIZE = 80
        self.GAP = 5
        self.current_state = None
        self.hidden_goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]] 
        self.is_running = False
        
        self.create_widgets()
        self.set_default_values()

    def create_widgets(self):
        title_lbl = tk.Label(self.root, text="THẤY START, MÙ GOAL ", font=("Helvetica", 14, "bold"), bg="#f8fafc", fg="#0f172a")
        title_lbl.pack(pady=10)
        input_frame = tk.Frame(self.root, bg="#f8fafc")
        input_frame.pack(pady=5)

        init_box = tk.LabelFrame(input_frame, text=" Nhập trạng thái ban đầu của bạn ", font=("Arial", 10, "bold"), bg="#f8fafc", fg="#475569")
        init_box.pack(padx=20)
        self.initial_entries = []
        for i in range(3):
            row_entries = []
            for j in range(3):
                e = tk.Entry(init_box, width=3, font=("Arial", 16), justify="center", bd=2)
                e.grid(row=i, column=j, padx=6, pady=6)
                row_entries.append(e)
            self.initial_entries.append(row_entries)

        main_layout = tk.Frame(self.root, bg="#f8fafc")
        main_layout.pack(pady=10, fill=tk.BOTH, expand=True)
        left_frame = tk.Frame(main_layout, bg="#f8fafc")
        left_frame.pack(side=tk.LEFT, padx=30)
        tk.Label(left_frame, text="Trạng thái Hiện tại", font=("Arial", 11, "bold"), bg="#f8fafc").pack()
        self.canvas_start = tk.Canvas(left_frame, width=3*self.TILE_SIZE+4*self.GAP, height=3*self.TILE_SIZE+4*self.GAP, bg="#e2e8f0", highlightthickness=0)
        self.canvas_start.pack(pady=5)
        mid_frame = tk.Frame(main_layout, bg="#f8fafc")
        mid_frame.pack(side=tk.LEFT, padx=30)
        tk.Label(mid_frame, text="Đích đến ", font=("Arial", 11, "bold"), bg="#f8fafc").pack()
        self.canvas_goal = tk.Canvas(mid_frame, width=3*self.TILE_SIZE+4*self.GAP, height=3*self.TILE_SIZE+4*self.GAP, bg="#1e293b", highlightthickness=0)
        self.canvas_goal.pack(pady=5)
        right_frame = tk.Frame(main_layout, bg="#f8fafc")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.btn_solve = tk.Button(right_frame, text=" TÌM KIẾM MÙ  ", font=("Arial", 12, "bold"), bg="#3b82f6", fg="white", command=self.start_solving, padx=8, pady=8)
        self.btn_solve.pack(fill=tk.X, pady=5)

        self.status_label = tk.Label(right_frame, text="Trạng thái: Sẵn sàng.", font=("Arial", 10, "italic"), bg="#f8fafc", fg="#64748b", anchor="w")
        self.status_label.pack(fill=tk.X, pady=5)

        self.result_text = tk.Text(right_frame, width=30, height=12, font=("Consolas", 10), bd=2, relief=tk.SUNKEN)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def set_default_values(self):
        start_matrix = [[1, 2, 3], [4, 0, 5], [7, 8, 6]]
        for i in range(3):
            for j in range(3):
                self.initial_entries[i][j].insert(0, str(start_matrix[i][j]))
        self.draw_puzzle(start_matrix, is_start=True)
        self.draw_goal_blind()

    def read_matrix(self):
        matrix = []
        for i in range(3):
            row = []
            for j in range(3):
                val = self.initial_entries[i][j].get().strip()
                row.append(int(val) if val else 0)
            matrix.append(row)
        return matrix

    def draw_puzzle(self, state, is_start=True):
        canvas = self.canvas_start if is_start else self.canvas_goal
        canvas.delete("all")
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                if val != 0:
                    x1 = j * self.TILE_SIZE + (j + 1) * self.GAP
                    y1 = i * self.TILE_SIZE + (i + 1) * self.GAP
                    canvas.create_rectangle(x1, y1, x1+self.TILE_SIZE, y1+self.TILE_SIZE, fill="#ffffff", outline="#94a3b8", width=2)
                    canvas.create_text(x1+self.TILE_SIZE/2, y1+self.TILE_SIZE/2, text=str(val), font=("Arial", 22, "bold"), fill="#1e293b")

    def draw_goal_blind(self):
        self.canvas_goal.delete("all")
        for i in range(3):
            for j in range(3):
                x1 = j * self.TILE_SIZE + (j + 1) * self.GAP
                y1 = i * self.TILE_SIZE + (i + 1) * self.GAP
                self.canvas_goal.create_rectangle(x1, y1, x1+self.TILE_SIZE, y1+self.TILE_SIZE, fill="#334155", outline="#0f172a", width=2)
                self.canvas_goal.create_text(x1+self.TILE_SIZE/2, y1+self.TILE_SIZE/2, text="?", font=("Arial", 28, "bold"), fill="#94a3b8")

    def find_zero(self, state):
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0: return i, j

    def is_solvable(self, state):
        flat = [num for row in state for num in row if num != 0]
        inversions = sum(1 for i in range(len(flat)) for j in range(i + 1, len(flat)) if flat[i] > flat[j])
        return inversions % 2 == 0

    def start_solving(self):
        if self.is_running: return
        try:
            self.current_state = self.read_matrix()
            all_nums = sorted([num for row in self.current_state for num in row])
            if all_nums != list(range(9)):
                raise ValueError("Ma trận nhập vào phải chứa đầy đủ các số từ 0 đến 8")
            if not self.is_solvable(self.current_state):
                raise ValueError("Ma trận này không có nghiệm giải! Hãy nhập ma trận khác.")
        except ValueError as ve:
            messagebox.showerror("Lỗi dữ liệu", str(ve))
            return

        self.is_running = True
        self.btn_solve.config(state=tk.DISABLED)
        for i in range(3):
            for j in range(3): self.initial_entries[i][j].config(state=tk.DISABLED)
        
        self.result_text.delete(1.0, tk.END)
        self.draw_goal_blind()

        # Chạy BFS tìm đường
        queue = deque([(self.current_state, [])])
        visited = {tuple(tuple(row) for row in self.current_state)}
        self.solution_path = []
        
        while queue:
            current, path = queue.popleft()
            if current == self.hidden_goal:
                self.solution_path = path
                break
            x, y = self.find_zero(current)
            for dx, dy, act in [(-1,0,"UP"), (1,0,"DOWN"), (0,-1,"LEFT"), (0,1,"RIGHT")]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 3 and 0 <= ny < 3:
                    new_state = [row[:] for row in current]
                    new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
                    tup = tuple(tuple(row) for row in new_state)
                    if tup not in visited:
                        visited.add(tup)
                        queue.append((new_state, path + [(new_state, act)]))
        
        self.step_index = 0
        self.result_text.insert(tk.END, f" đã thấy  đích ở độ sâu {len(self.solution_path)} \n")
        self.execute_step()

    def execute_step(self):
        if self.step_index >= len(self.solution_path):
            self.draw_puzzle(self.hidden_goal, is_start=False) #
            self.status_label.config(text="Đã tìm ra đích!")
            self.result_text.insert(tk.END, "\n Đã mở khóa hình ảnh đích đến!")
            self.is_running = False
            self.btn_solve.config(state=tk.NORMAL)
            for i in range(3):
                for j in range(3): self.initial_entries[i][j].config(state=tk.NORMAL)
            return

        next_state, act = self.solution_path[self.step_index]
        self.current_state = next_state
        self.draw_puzzle(self.current_state, is_start=True)
        self.status_label.config(text=f"Đang di chuyển: {act} (Bước {self.step_index+1})")
        self.step_index += 1
        self.root.after(300, self.execute_step)

if __name__ == "__main__":
    app = PuzzleApp(tk.Tk())
    app.root.mainloop()