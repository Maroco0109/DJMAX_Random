import tkinter as tk
from tkinter import messagebox
import requests
import random

# API에서 곡 데이터 가져오기
def fetch_songs():
    url = "https://v-archive.net/db/songs.json"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        messagebox.showerror("Error", "API 호출 실패")
        return []

# 필터링된 곡 리스트 반환
def filter_songs(songs, min_level, max_level, selected_patterns, sc_only, selected_dlcs):
    filtered_songs = []

    for song in songs:
        # DLC 필터링
        if song["dlc"] not in selected_dlcs:
            continue

        for pattern, difficulties in song.get("patterns", {}).items():
            # 선택된 패턴만 필터링
            if pattern in selected_patterns:
                for difficulty, details in difficulties.items():
                    # SC 필터
                    if sc_only and difficulty == "SC" and min_level <= details["level"] <= max_level:
                        filtered_songs.append((song, pattern, difficulty, details["level"]))
                    # SC를 제외한 NM, HD, MX
                    elif not sc_only and difficulty in ["NM", "HD", "MX"] and min_level <= details["level"] <= max_level:
                        filtered_songs.append((song, pattern, difficulty, details["level"]))

    return filtered_songs

# 랜덤 곡 선택 버튼 클릭 이벤트
def select_song():
    try:
        # 최소/최대 난이도 가져오기
        min_level = int(min_level_entry.get())
        max_level = int(max_level_entry.get())
    except ValueError:
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, "Error: 난이도는 숫자로 입력해주세요.")
        return

    # 선택된 패턴 및 SC 여부 가져오기
    selected_patterns = [pattern for pattern, var in pattern_vars.items() if var.get()]
    sc_only = sc_var.get()

    # 선택된 DLC 가져오기
    selected_dlcs = [dlc for dlc, var in dlc_vars.items() if var.get()]
    if not selected_dlcs:
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, "Error: 최소 하나의 DLC를 선택해주세요.")
        return

    if not selected_patterns:
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, "Error: 최소 하나의 패턴을 선택해주세요.")
        return

    # 곡 필터링
    songs = fetch_songs()
    filtered_songs = filter_songs(songs, min_level, max_level, selected_patterns, sc_only, selected_dlcs)

    # 랜덤 곡 선택
    selected_data = random.choice(filtered_songs) if filtered_songs else None

    result_text.delete("1.0", tk.END)
    if selected_data:
        song, pattern, difficulty, level = selected_data
        song_info = (
            f"제목: {song['name']}\n"
            f"아티스트: {song['composer']}\n"
            f"DLC: {song['dlc']}\n"
            f"버튼: {pattern}\n"
            f"난이도: {difficulty} {level}"
        )
        result_text.insert(tk.END, song_info)  # 결과를 Text 위젯에 출력
    else:
        result_text.insert(tk.END, "결과: 조건에 맞는 곡이 없습니다.")

# DLC 체크박스 동적으로 생성
def create_dlc_checkboxes(songs):
    dlcs = sorted({song["dlc"] for song in songs})  # DLC 목록 추출 및 정렬
    num_columns = 5  # 한 줄에 표시할 DLC 체크박스 개수
    num_rows = -(-len(dlcs) // num_columns)  # DLC를 표시할 행 수 계산

    for idx, dlc in enumerate(dlcs):
        dlc_vars[dlc] = tk.BooleanVar()
        tk.Checkbutton(dlc_frame, text=dlc, variable=dlc_vars[dlc]).grid(
            row=idx % num_rows, column=idx // num_rows, sticky="w", padx=5
        )

    # 창 크기 동적으로 조정
    new_width = max(800, 200 + len(dlcs) // num_rows * 150)  # 최소 800px 이상, DLC 수에 따라 확장
    new_height = max(450, 200 + num_rows * 30)  # 최소 400px 이상, 행 수에 따라 확장
    root.geometry(f"{new_width}x{new_height}")

# GUI 구성
root = tk.Tk()
root.title("DJMax Respect V 랜덤 선택기")

# 레이아웃 설정
root.geometry("800x400")  # 기본 창 크기
root.resizable(True, True)  # 창 크기 조정 가능

# 난이도 입력 필드
difficulty_frame = tk.Frame(root)
difficulty_frame.pack(pady=10)
tk.Label(difficulty_frame, text="최소 난이도").grid(row=0, column=0, padx=5)
min_level_entry = tk.Entry(difficulty_frame, width=5)
min_level_entry.grid(row=0, column=1, padx=5)

tk.Label(difficulty_frame, text="최대 난이도").grid(row=0, column=2, padx=5)
max_level_entry = tk.Entry(difficulty_frame, width=5)
max_level_entry.grid(row=0, column=3, padx=5)

# 패턴 및 DLC 선택 체크박스
options_frame = tk.Frame(root)
options_frame.pack(pady=10)

# 패턴 체크박스 (좌측)
pattern_frame = tk.LabelFrame(options_frame, text="패턴 선택", padx=10, pady=10)
pattern_frame.grid(row=0, column=0, padx=10)

patterns = ["4B", "5B", "6B", "8B"]
pattern_vars = {pattern: tk.BooleanVar() for pattern in patterns}

for idx, pattern in enumerate(patterns):
    tk.Checkbutton(pattern_frame, text=pattern, variable=pattern_vars[pattern]).grid(row=idx, column=0, sticky="w")

# DLC 체크박스 (우측)
dlc_frame = tk.LabelFrame(options_frame, text="DLC 선택", padx=10, pady=10)
dlc_frame.grid(row=0, column=1, padx=10)
dlc_vars = {}
songs = fetch_songs()
create_dlc_checkboxes(songs)

# SC 난이도 체크박스
sc_frame = tk.Frame(root)
sc_frame.pack(pady=10)
sc_var = tk.BooleanVar()
tk.Checkbutton(sc_frame, text="SC 난이도만", variable=sc_var).pack()

# 랜덤 선택 버튼
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
select_button = tk.Button(button_frame, text="랜덤 곡 선택", command=select_song, width=20)
select_button.pack()

# 결과 표시 텍스트 위젯
result_frame = tk.Frame(root)
result_frame.pack(fill="both", padx=10, pady=10)

result_text = tk.Text(
    result_frame,
    height=15,  # 기본 세로 길이 (더 크게 설정)
    wrap="word",
    font=("Arial", 10),
    bg="#f9f9f9",
    fg="#333"
)
result_text.pack(fill="both", expand=True, padx=5, pady=5)

scrollbar = tk.Scrollbar(result_frame, command=result_text.yview)
scrollbar.pack(side="right", fill="y")
result_text.config(yscrollcommand=scrollbar.set)
root.mainloop()