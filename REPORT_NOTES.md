# Ghi chú viết báo cáo — Griductive Solver (CSC14003 Project 2)

File này gom sẵn công thức, số liệu thật và các điểm **phải giải thích** trong
báo cáo PDF. Mỗi mục dưới đây ánh xạ trực tiếp sang một gạch đầu dòng bắt buộc
của mục **4.6 Report** trong đề bài.

Mọi con số trong file đều lấy từ `output/experiments.csv` và
`output/pure_literal_ablation.csv`, sinh ra bằng `python run_experiments.py`.
Chạy lại lệnh đó trước khi chốt báo cáo để số liệu khớp máy của nhóm.

---

## 1. Problem formulation

### 1.1 Biến mệnh đề

Với mỗi nhân vật `i` đúng **một** biến Boolean sơ cấp:

```
C_i = True   nếu i là Criminal
C_i = False  nếu i là Innocent
```

Ánh xạ biến là **tất định**, duyệt theo thứ tự row-major (`core/regions.py`,
`logic/cnf_encoder.py`):

```
index(cell) = (row - 1) * N + col + 1        # A1 -> 1, B1 -> 2, ..., C3 -> 9
```

Ví dụ thật trên bàn 3×3 của `case_01`:

| ô | A1 | B1 | C1 | A2 | B2 | C2 | A3 | B3 | C3 |
|---|----|----|----|----|----|----|----|----|----|
| biến | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |

Không có biến phụ trợ (xem mục 5.1 để giải thích).

### 1.2 Ngữ nghĩa clue

Vùng `R` (region) có 6 dạng: `ROW`, `COLUMN`, `NEIGHBORS` (8 ô kề, không tính
chính nó), `EXPLICIT`, và hai dạng nâng cao `CORNERS`, `BOUNDARY`.

| Clue | Ý nghĩa logic |
|---|---|
| `FACT(i, s)` | `C_i` hoặc `¬C_i` |
| `SAME(i, j)` | `C_i ↔ C_j` |
| `DIFFERENT(i, j)` | `C_i ⊕ C_j` |
| `EXACTLY(k, R)` | `Σ_{i∈R} C_i = k` |
| `AT_LEAST(k, R)` | `Σ_{i∈R} C_i ≥ k` |
| `AT_MOST(k, R)` | `Σ_{i∈R} C_i ≤ k` |
| `PARITY(p, R)` *(mở rộng 1)* | `Σ_{i∈R} C_i ≡ p (mod 2)` |
| `IMPLIES(i, j)` *(mở rộng 2)* | `C_i → C_j` |

`NO(R)` được biểu diễn bằng `EXACTLY(0, R)` đúng như đề bài yêu cầu.

**Hai extension bắt buộc của nhóm:** `PARITY` (ràng buộc chẵn/lẻ) và `IMPLIES`
(compound clue). Ngoài ra còn hai *advanced region expression* là `CORNERS` và
`BOUNDARY` — tính là phần vượt yêu cầu.

### 1.3 Knowledge base tại bước t

```
KB_t = CNF(các clue đã lật)  ∧  các unit clause của verdict đã chứng minh
```

`KB_t` **không bao giờ** chứa nhãn ẩn hay clue chưa lật. Điều này được bảo đảm
về mặt kiến trúc: `GameEngine` giữ `Puzzle` (đáp án + toàn bộ clue), còn
`LogicAgent` chỉ nhận một bản sao `PublicState` gồm `revealed_clues` và
`proved_statuses`. `LogicAgent` không có tham chiếu nào tới `Puzzle` hay
`GameEngine`.

### 1.4 Reveal protocol

1. Thẻ face-up ban đầu công khai **cả status lẫn clue** (đề bài mục 2.1).
2. Chọn một nhân vật chưa giải mà status bị `KB_t` kéo theo; nếu có nhiều, chọn
   theo thứ tự row-major (tất định).
3. Verdict được chấp nhận → lật thẻ, thêm status (unit clause) và clue của thẻ
   đó vào để tạo `KB_{t+1}`.
4. Verdict không được kéo theo → **không** lật thẻ, không đổi trạng thái.

Bốn kết quả trả về: `ACCEPTED`, `NOT_PROVABLE`, `CONTRADICTED`, `INCONSISTENT`.

---

## 2. CNF encoding

> Đề bài yêu cầu **ít nhất một binary clue và một counting clue phải có dẫn
> giải**. Hai mục 2.1 và 2.2 dưới đây dùng clue thật của `case_01`, có thể chép
> thẳng vào báo cáo.

### 2.1 Dẫn giải binary clue — `SAME` (clue N03 của case_01)

Clue N03: *"Casey (C1) và Emery (B2) có cùng trạng thái."* → `C_3 ↔ C_5`.

```
C_3 ↔ C_5
  ≡ (C_3 → C_5) ∧ (C_5 → C_3)          (định nghĩa tương đương)
  ≡ (¬C_3 ∨ C_5) ∧ (¬C_5 ∨ C_3)        (luật implication)
```

CNF sinh ra bởi chương trình: `[[-3, 5], [3, -5]]` — khớp chính xác.

Tương tự `DIFFERENT(i, j) ≡ C_i ⊕ C_j ≡ (C_i ∨ C_j) ∧ (¬C_i ∨ ¬C_j)`; clue N04
cho ra `[[5, 4], [-5, -4]]`.

`IMPLIES(i, j) ≡ C_i → C_j ≡ (¬C_i ∨ C_j)` — đúng 1 mệnh đề.

### 2.2 Dẫn giải counting clue — `EXACTLY` (clue N06 của case_01)

Clue N06: *"Đúng 2 criminal nằm ở hàng 3."* → `R = {A3, B3, C3} = {7, 8, 9}`,
`k = 2`, `n = |R| = 3`.

Nhóm dùng **direct combinatorial encoding**:

```
AT_LEAST(k, R):  mọi tập con kích thước (n - k + 1) phải chứa ít nhất một biến True
                 →  ⋀ ( ⋁_{i∈S} C_i )   với mọi S ⊆ R, |S| = n - k + 1

AT_MOST(k, R):   mọi tập con kích thước (k + 1) không thể toàn True
                 →  ⋀ ( ⋁_{i∈S} ¬C_i )  với mọi S ⊆ R, |S| = k + 1

EXACTLY(k, R) = AT_LEAST(k, R) ∧ AT_MOST(k, R)
```

Thay số `n = 3, k = 2`:

- `AT_LEAST(2)`: kích thước tập con `3 - 2 + 1 = 2` → `{7,8}, {7,9}, {8,9}`
  → `(C_7 ∨ C_8) ∧ (C_7 ∨ C_9) ∧ (C_8 ∨ C_9)`
- `AT_MOST(2)`: kích thước tập con `2 + 1 = 3` → `{7,8,9}`
  → `(¬C_7 ∨ ¬C_8 ∨ ¬C_9)`

CNF sinh ra bởi chương trình: `[[7, 8], [7, 9], [8, 9], [-7, -8, -9]]` — 4 mệnh
đề, khớp chính xác với dẫn giải tay.

**Số mệnh đề:** `|AT_LEAST(k,R)| = C(n, n-k+1)`, `|AT_MOST(k,R)| = C(n, k+1)`.

`PARITY(p, R)` được mã hoá bằng cách cấm mọi gán đầy đủ sai parity → `2^(n-1)`
mệnh đề. Vì vậy chương trình chỉ dùng `PARITY` trên vùng nhỏ (≤ 6 ô).

### 2.3 Verdict đã chứng minh

Mỗi status đã chứng minh thành **1 unit clause**: `C_i` nếu CRIMINAL, `¬C_i` nếu
INNOCENT (`CNFEncoder.encode_public_state`).

### 2.4 Kiểm chứng encoder

Bộ test `tests/test_encoder.py` đối chiếu CNF với **direct semantic evaluator**
(`logic/semantics.py`, không gọi encoder) trên **toàn bộ 512 phép gán** của bàn
3×3, cho mọi loại clue và mọi loại region. Không có sai lệch.

---

## 3. Algorithms

### 3.1 DPLL (`logic/dpll.py`)

```
DPLL(F, A):
    lặp:
        F ← simplify(F, A)                  # bỏ literal sai, bỏ clause đã thoả
        nếu F chứa clause rỗng:  return UNSAT        # conflict detection
        nếu F rỗng:              return SAT(A)
        nếu F có unit clause:    gán tất cả, A cập nhật, lặp lại   # unit propagation
        nếu có pure literal:     gán tất cả, lặp lại               # tuỳ chọn
        thoát vòng lặp
    v ← biến chưa gán có chỉ số NHỎ NHẤT     # deterministic variable selection
    với value ∈ (False, True):                # recursive branching
        nếu DPLL(F, A ∪ {v = value}) là SAT: return SAT
        backtracks += 1                       # backtracking
    return UNSAT
```

Đối chiếu 6 yêu cầu tối thiểu của mục 4.3:

| Yêu cầu | Vị trí |
|---|---|
| 1. Unit propagation | vòng lặp `units` trong `_dpll` |
| 2. Conflict detection | `_simplify` trả `None` khi có clause rỗng |
| 3. Deterministic variable selection | `min(v for v in used if v not in assignment)` |
| 4. Recursive branching + backtracking | đệ quy `_dpll` theo thứ tự `(False, True)` |
| 5. Trả SAT + assignment đầy đủ / UNSAT | `solve()` điền các biến còn lại bằng `False` |
| 6. Ghi nhận số liệu | `DPLLStats`: decisions, propagations, backtracks, pure_literals, runtime_ms |

**Pure-literal elimination** (đề bài ghi rõ là *optional*) đã được cài, bật/tắt
qua `DPLLSolver(use_pure_literal=...)` để lấy số liệu so sánh (mục 4.3).

Solver nhận **assumptions** dưới dạng unit clause tạm thời thêm vào `KB_t`.

### 3.2 Entailment classification (`logic/agent.py`)

Một model chỉ là **một** phép gán khả dĩ; verdict chỉ hợp lệ khi đúng trong
**mọi** model. Với mỗi nhân vật chưa giải, agent gọi DPLL đúng 2 lần:

```
KB_t ⊨  C_i   ⟺  KB_t ∧ ¬C_i  là UNSAT   → CRIMINAL
KB_t ⊨ ¬C_i   ⟺  KB_t ∧  C_i  là UNSAT   → INNOCENT
cả hai SAT                                → UNKNOWN
KB_t tự nó UNSAT                          → INCONSISTENT
```

Chi phí: `2 × (N² − số ô đã giải) + 1` lần gọi SAT cho mỗi lần phân tích.

### 3.3 Uniqueness check (`LogicAgent.uniqueness_check`)

```
1. giải KB → nếu UNSAT: INCONSISTENT
2. lấy model M, dựng blocking clause  B = ⋁_i (¬C_i nếu M(C_i)=True, ngược lại C_i)
3. giải KB ∧ B → UNSAT ⇒ UNIQUE, SAT ⇒ MULTIPLE
```

Đề bài yêu cầu "a separate uniqueness check for the **complete clue set**":
`run_experiments.py` dựng một `PublicState` chứa **toàn bộ** clue (nhưng vẫn
không có nhãn ẩn) rồi gọi hàm này. GUI cũng hiển thị kết quả cho `KB_t` hiện tại
ở dòng *Current public KB*.

### 3.4 Deduction loop (`game/session.py`)

```
KB_0 ← clue + status của các thẻ face-up
lặp:
    phân tích KB_t  →  phân loại mọi nhân vật
    chọn ô forced đầu tiên theo row-major   (không có → dừng, UNKNOWN)
    gửi verdict → engine kiểm tra entailment → lật thẻ
    KB_{t+1} ← KB_t ∧ unit(status) ∧ CNF(clue vừa lộ)
đến khi giải xong hoặc gặp trạng thái kết thúc khác
```

**Deduction trace** (`TraceEntry`) ghi: số bước, danh sách clue đang hoạt động,
số SAT query, verdict, và clue vừa lộ → xuất ra `output/deduction_traces.json`.

### 3.5 Ví dụ trace thật — case_01

`KB_0` = clue của A1 và B2 + status A1 = CRIMINAL, B2 = CRIMINAL.

| Bước | Ô | Verdict | Clue vừa lộ | Uniqueness của `KB_t` |
|---|---|---|---|---|
| 1 | B1 | INNOCENT | N02 (AT_LEAST) | MULTIPLE |
| 2 | C1 | CRIMINAL | N03 (SAME) | MULTIPLE |
| 3 | A2 | INNOCENT | N05 (FACT) | MULTIPLE |
| 4 | A3 | INNOCENT | N06 (EXACTLY) | MULTIPLE |
| 5 | B3 | CRIMINAL | N07 (EXACTLY) | **UNIQUE** |
| 6 | C2 | INNOCENT | N08 (DIFFERENT) | UNIQUE |
| 7 | C3 | CRIMINAL | N09 (FACT) | UNIQUE |

Đây là minh hoạ tốt cho ý *"model ≠ logical consequence"*: ở bước 1–4 KB công
khai vẫn còn nhiều model, nhưng từng verdict riêng lẻ vẫn được kéo theo.

---

## 4. Experiments

### 4.1 Bảng chính (`output/experiments.csv`)

| Case | Size | Biến sơ cấp | Biến phụ | Mệnh đề (bộ clue đầy đủ) | SAT calls | Decisions | Propagations | Backtracks | Pure literals | Deduction steps | Solved | Uniqueness | Runtime (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| case_01 | 3×3 | 9 | 0 | 22 | 63 | 0 | 413 | 0 | 0 | 7 | ✔ | UNIQUE | 1.21 |
| case_02 | 4×4 | 16 | 0 | 36 | 224 | 0 | 2108 | 0 | 0 | 14 | ✔ | UNIQUE | 5.73 |
| case_03 | 3×3 | 9 | 0 | 16 | 63 | 10 | 402 | 0 | 18 | 7 | ✔ | UNIQUE | 1.37 |
| case_04 | 4×4 | 16 | 0 | 46 | 224 | 260 | 2320 | 0 | 0 | 14 | ✔ | UNIQUE | 9.13 |
| case_05 | 5×5 | 25 | 0 | 124 | 575 | 81 | 9206 | 0 | 0 | 23 | ✔ | UNIQUE | 23.08 |
| case_06 | 5×5 | 25 | 0 | 252 | 575 | 227 | 9280 | 0 | 0 | 23 | ✔ | UNIQUE | 40.53 |

> Runtime dao động vài ms giữa các lần chạy — nên nêu rõ là chạy trên máy nào,
> Python bản nào, và lấy trung bình 3–5 lần nếu muốn chặt chẽ.

### 4.2 Ablation: pure-literal elimination (`output/pure_literal_ablation.csv`)

| Case | Decisions (off → on) | Propagations (off → on) | Pure literals | Runtime ms (off → on) |
|---|---|---|---|---|
| case_01 | 0 → 0 | 413 → 413 | 0 | 1.22 → 1.06 |
| case_02 | 0 → 0 | 2108 → 2108 | 0 | 5.17 → 5.52 |
| case_03 | **19 → 10** | 402 → 402 | 18 | 1.07 → 1.61 |
| case_04 | 260 → 260 | 2320 → 2320 | 0 | 8.84 → 8.19 |
| case_05 | 81 → 81 | 9206 → 9206 | 0 | 24.21 → 23.08 |
| case_06 | 227 → 227 | 9280 → 9280 | 0 | 40.16 → 38.13 |

### 4.3 Nhận xét nên viết

1. **Số mệnh đề tăng nhanh hơn số biến.** Từ 3×3 lên 5×5 số biến tăng 2.8× (9 →
   25) nhưng số mệnh đề tăng tới 11× (22 → 252), do counting clue sinh mệnh đề
   theo tổ hợp `C(n, k+1)` chứ không tuyến tính.

2. **Số lần gọi SAT tăng bậc hai và dự đoán được.** Mỗi lần phân tích tốn
   `2 × (số ô chưa giải) + 1` lần gọi; cộng dồn cả ván cho 63 / 224 / 575 lần
   gọi ứng với 3×3 / 4×4 / 5×5 — đúng bậc `Θ(N⁴)`.

3. **Instance nhỏ giải xong hoàn toàn bằng unit propagation.** `case_01` và
   `case_02` có `decisions = 0`: sau khi thêm status của thẻ face-up, mọi truy
   vấn SAT đều kết thúc trước khi cần rẽ nhánh. Chỉ `case_03`, `case_04`,
   `case_05`, `case_06` thực sự kích hoạt branching (10 / 260 / 81 / 227). Đây
   là lý do chính đáng để giữ hai case 5×5 trong bộ benchmark.

4. **`backtracks = 0` trên toàn bộ bộ test.** Không phải lỗi đếm: mọi truy vấn
   UNSAT đều bị phát hiện bởi unit propagation *trước khi* rẽ nhánh, còn truy
   vấn SAT thì nhánh thử đầu tiên (`False`) luôn dẫn tới model. Cần nói rõ quy
   ước đếm: `backtracks` +1 cho **mỗi nhánh thất bại**, nên hai nhánh cùng hỏng
   sẽ tính là 2.

5. **Pure-literal elimination hầu như không giúp gì ở bài toán này.** Chỉ
   `case_03` có pure literal (18 cái, giảm decisions 19 → 10). Lý do: KB
   Griductive dày đặc clue hai chiều (`SAME`, `DIFFERENT`, counting) nên gần như
   mọi biến đều xuất hiện ở cả hai cực. Runtime không cải thiện rõ vì chi phí
   quét cực literal xấp xỉ bằng phần tiết kiệm được. Đây là một kết luận âm
   hợp lệ và nên được báo cáo trung thực.

6. **Không có case nào thất bại hay timeout.** Cả 6 case đều `solved = True`,
   `uniqueness = UNIQUE`, và giải được tuần tự mà không cần đoán.

### 4.4 Failure cases và limitations (bắt buộc phải có)

1. **Cardinality encoding bùng nổ tổ hợp.** Direct combinatorial encoding sinh
   `C(n, k+1)` mệnh đề. Với vùng `BOUNDARY` của bàn 5×5 (16 ô) và `k` ở giữa
   dải, `EXACTLY(8, BOUNDARY)` cần `C(16,9) + C(16,8) = 24 310` mệnh đề, còn
   `PARITY` trên 16 ô cần `2¹⁵ = 32 768` mệnh đề. Vì vậy hai case 5×5 **không**
   dùng clue đếm trên `BOUNDARY`. Hướng khắc phục: chuyển sang sequential
   counter / totalizer encoding, chấp nhận sinh biến phụ trợ nhưng số mệnh đề
   chỉ còn `O(n·k)`.

2. **Không dùng SAT solver incremental.** Mỗi truy vấn dựng lại danh sách mệnh
   đề từ đầu; `_simplify` quét toàn bộ mệnh đề mỗi vòng. Với 5×5 tổng thời gian
   vẫn dưới 45 ms nên chấp nhận được, nhưng sẽ không mở rộng lên bàn 7×7+.

3. **Không có watched literals, không có clause learning.** DPLL thuần theo đúng
   yêu cầu đề bài; đây là giới hạn có chủ đích, không phải thiếu sót.

4. **Solver dừng ở trạng thái UNKNOWN.** Nếu bộ clue được lật ra không đủ để kéo
   theo thêm verdict nào, agent dừng và báo *"no forced verdict available"* thay
   vì đoán — đúng luật no-guess. Puzzle phải được thiết kế sao cho chuỗi suy
   diễn không đứt (bộ sinh puzzle của nhóm kiểm tra điều này tự động).

5. **Uniqueness check chỉ so 2 model.** Hàm chỉ phân biệt UNIQUE / MULTIPLE chứ
   không đếm hết số model. Đủ cho yêu cầu đề bài, nhưng không cho biết mức độ mơ
   hồ của một puzzle hỏng.

---

## 5. Những điểm PHẢI giải thích (dễ bị hỏi khi vấn đáp)

### 5.1 Vì sao `auxiliary_variables = 0`?

Đề bài cho phép: *"Because the required regions are small, a direct
combinatorial encoding is acceptable in this case."* Nhóm chọn encoding tổ hợp
trực tiếp nên **không sinh biến phụ trợ nào**; biến sơ cấp `C_i` cũng là toàn bộ
biến của công thức. Cột này bằng 0 là kết quả đúng, không phải chưa cài. Cần nói
kèm phần đánh đổi ở mục 4.4.1.

### 5.2 Vì sao thẻ face-up làm giảm số deduction step?

Đề bài mục 2.1: *"A few cards are face-up initially; their **statuses and clues**
form the public knowledge base state."* Mỗi case mở sẵn 2 thẻ, nên số bước suy
diễn là `N² − 2`: 7 (3×3), 14 (4×4), 23 (5×5). Nếu báo cáo ghi 9/16/25 là sai.

### 5.3 Phân biệt 4 kết quả trả về

| Kết quả | Điều kiện | Có lật thẻ? |
|---|---|---|
| `ACCEPTED` | status được `KB_t` kéo theo và đúng với verdict gửi lên | Có |
| `CONTRADICTED` | status **ngược lại** mới là cái được kéo theo | Không |
| `NOT_PROVABLE` | cả hai status đều còn model | Không |
| `INCONSISTENT` | bản thân `KB_t` là UNSAT | Không |

### 5.4 Vì sao Hint không phải là gian lận?

`LogicAgent.next_forced` chỉ nhận `PublicState`. Nó không có tham chiếu tới
`Puzzle` hay `GameEngine`, nên về mặt kiểu dữ liệu **không thể** đọc đáp án ẩn.
Hint chạy đúng cùng một vòng entailment như Auto Solve.

### 5.5 Vì sao cần 2 lần gọi SAT cho mỗi nhân vật?

Vì entailment không thể suy ra từ một model duy nhất. Ví dụ trong đề bài:
`KB = (C_A ∨ C_B) ∧ (¬C_A ∨ C_B)` có model `C_A = False, C_B = True`, nhưng chỉ
`C_B` là hệ quả logic. Phải thử phủ định từng phía mới kết luận được.

---

## 6. Checklist đối chiếu rubric

| Mục | Điểm | Trạng thái | Bằng chứng |
|---|---|---|---|
| 4.1 Reimplement the Game | 10 | ✔ | GUI Pygame; Load / Restart / Hint / Auto Solve có ở **cả** Play và Solver mode; highlight ô được clue tham chiếu; 4 kết quả verdict |
| 4.2 CNF encoding | 10 | ✔ | `logic/cnf_encoder.py`, `logic/semantics.py`; báo cáo biến + mệnh đề trên GUI và CSV |
| 4.3 DPLL | 10 | ✔ | `logic/dpll.py`, đủ 6 yêu cầu + pure-literal tuỳ chọn |
| 4.4 Deductive Logic Agent | 20 | ✔ | `logic/agent.py`, `game/session.py`; trace + uniqueness check |
| 4.5 Experiments | 10 | ✔ | 6 case (2×3×3, 2×4×4, 2×5×5), `output/*.csv` |
| 4.6 Report | 30 | ☐ | file này |
| 4.7 Demo video | 10 | ☐ | xem mục 7 |

**Độ phủ clue/region của bộ test** — nên đưa bảng này vào báo cáo:

| Case | Clue types | Region kinds |
|---|---|---|
| case_01 | FACT, SAME, DIFFERENT, EXACTLY, AT_LEAST, AT_MOST | ROW, COLUMN, NEIGHBORS, EXPLICIT |
| case_02 | cả 6 lõi + PARITY + IMPLIES | ROW, COLUMN, NEIGHBORS, EXPLICIT |
| case_03 | FACT, DIFFERENT, EXACTLY, AT_LEAST, AT_MOST | ROW, COLUMN, NEIGHBORS, EXPLICIT |
| case_04 | FACT, SAME, DIFFERENT, EXACTLY, AT_LEAST, AT_MOST | ROW, COLUMN, NEIGHBORS, EXPLICIT |
| case_05 | cả 6 lõi + PARITY + IMPLIES | ROW, COLUMN, NEIGHBORS, EXPLICIT, CORNERS |
| case_06 | cả 6 lõi + PARITY + IMPLIES | ROW, COLUMN, NEIGHBORS, EXPLICIT, CORNERS |

Bốn region **bắt buộc** của mục 2.1 (row, column, neighbors, explicit) đều được
mọi case sử dụng.

---

## 7. Demo video (mục 4.7) — kịch bản gợi ý 5–10 phút

1. **Giao diện (5đ)** — menu, How to play, màn chọn case, chỉ ra 6 case.
2. **Chơi tay** — chọn `case_01`, cố tình gửi verdict sai để cho thấy
   `CONTRADICTED`, rồi gửi một verdict chưa đủ dữ kiện để cho thấy
   `NOT_PROVABLE`, rồi giải đúng để thẻ lật.
3. **Highlight clue** — bấm vào một thẻ đã lật mang clue `NEIGHBORS` để cho thấy
   các ô được tham chiếu sáng lên.
4. **Hint** — nhấn `HINT`, giải thích rằng nó chỉ đọc public state.
5. **Auto Solve (5đ)** — mở `case_05` hoặc `case_06` (5×5), nhấn `AUTO SOLVE`,
   vừa chạy vừa chỉ vào bảng CNF/DPLL metrics đang cập nhật và dòng
   *Current public KB* đổi từ MULTIPLE sang UNIQUE.
6. **Experiments** — chạy `python run_experiments.py`, mở CSV.

Nhớ: upload Google Drive, chỉnh quyền *anyone with the link*, kiểm tra bằng cửa
sổ ẩn danh, **không** nộp link YouTube.

---

## 8. Appendix — khai báo sử dụng Generative AI (bắt buộc)

Đề bài yêu cầu ghi rõ đã dùng LLM như thế nào và prompt gì. Gợi ý cấu trúc:

- **Công cụ đã dùng:** tên model / công cụ, giai đoạn nào của dự án.
- **Việc AI đã làm:** ví dụ rà soát code đối chiếu đề bài, sinh và kiểm chứng
  hai case 5×5, tối ưu hiệu năng render, viết bộ test bổ sung.
- **Việc nhóm tự làm:** thiết kế kiến trúc, cài DPLL/encoder/agent, thiết kế
  GUI, viết báo cáo, quay video.
- **Prompt tiêu biểu:** chép lại nguyên văn 3–5 prompt.
- **Cách nhóm kiểm chứng đầu ra của AI:** nêu rõ đã chạy lại
  `python -m unittest discover -s tests`, `python run_experiments.py`, và đối
  chiếu độc lập (fuzz DPLL với vét cạn, đối chiếu CNF với semantic evaluator,
  đếm model không dùng CNF/DPLL).

> Ghi trung thực. Đề bài nói rõ AI **không bị cấm**, nhưng giảng viên có quyền
> vấn đáp ngẫu nhiên — hãy chắc chắn mọi thành viên giải thích được mục 3 và 5.

---

## 9. Task distribution (mục 4.6, gạch đầu dòng đầu tiên)

Bảng bắt buộc, nhóm tự điền:

| Thành viên | MSSV | Công việc phụ trách | % hoàn thành |
|---|---|---|---|
| | | | |

Nhắc lại cách tính điểm cá nhân trong đề: điểm nhóm 9.0 và mức hoàn thành 90%
→ điểm cá nhân `9.0 × 90% = 8.1`. Đánh giá **công bằng và chính xác**.

---

## 10. Lệnh cần chạy trước khi nộp

```bash
python -m unittest discover -s tests -t .
```

```bash
python run_experiments.py
```

```bash
python main.py
```
