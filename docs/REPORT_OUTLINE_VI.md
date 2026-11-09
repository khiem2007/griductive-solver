# Dàn ý báo cáo Project 2 — Proof Ledger

Đối chiếu đề CSC14003, mục 4.6 (trang 8), cùng các yêu cầu kỹ thuật ở trang 2–7 và nộp bài ở trang 9. Đây là dàn ý để nhóm tự hoàn thiện báo cáo, không phải Report.pdf đã hoàn tất. Ngày rà soát: 08/11/2026.

## 0. Trang bìa, mục lục và thông tin demo

- Tên môn, Project 2, tên sản phẩm Proof Ledger, lớp và giảng viên theo thông tin thực tế.
- Họ tên, MSSV từng thành viên; ngày nộp thực tế.
- Link video Google Drive có quyền “Anyone with the link can view”. Đặt link dễ thấy trên trang đầu hoặc trong mục Demo; PDF cuối cùng phải chứa link.
- Mục lục tự động, đánh số hình/bảng/công thức và số trang.

Gợi ý dung lượng: khoảng 12–16 trang nội dung và phụ lục tùy mức chi tiết; đề không quy định số trang báo cáo. Không trình bày gợi ý này thành một ràng buộc của đề.

## 1. Kế hoạch và phân công công việc

### 1.1. Mục tiêu và kế hoạch

- Mục tiêu: tái hiện trò chơi có GUI và giải bằng suy diễn logic, tuyệt đối không đoán.
- Các mốc thực tế: phân tích yêu cầu, mô hình dữ liệu, encoder/evaluator, DPLL, agent, GUI, kiểm thử/thí nghiệm, báo cáo/video.
- Dùng timeline hoặc bảng mốc với kế hoạch và kết quả thực tế. Không tự điền lịch hoặc thành tích chưa được nhóm xác nhận.

### 1.2. Trách nhiệm từng thành viên — bắt buộc theo đề

| Họ tên / MSSV | Công việc được giao | Sản phẩm thực tế / bằng chứng | Tỷ lệ hoàn thành cá nhân | Ghi chú |
|---|---|---|---|---|
| Nhóm tự điền | Ví dụ: encoder và kiểm thử truth table | File, commit, biên bản review thực tế | Nhóm xác nhận | Không điền phần trăm giả định |

Phân biệt tỷ trọng phân công với tỷ lệ hoàn thành nhiệm vụ cá nhân. Đề minh họa điểm cá nhân bằng điểm nhóm nhân tỷ lệ hoàn thành: điểm nhóm 9.0 và hoàn thành 90% thì điểm cá nhân 8.1. Không mặc định các tỷ lệ hoàn thành cá nhân phải cộng thành 100%.

## 2. Phát biểu bài toán và luật chơi

### 2.1. Bàn cờ và dữ liệu

- Lưới N×N; chương trình hỗ trợ N = 3, 4, 5.
- Tọa độ cột A… và hàng 1…; thứ tự row-major. Tên hiển thị tăng theo alphabet trên thứ tự này.
- Mỗi ô có tên, nghề, trạng thái nhị phân ẩn và một clue có cấu trúc. Tên/nghề không tự tạo ràng buộc logic.
- Clue nào được mở cũng đúng, kể cả clue của Criminal; không phải bài toán người nói thật/nói dối.
- Trình bày ngắn schema JSON bằng một ví dụ từ `src/proofledger/samples`, không chép toàn bộ file vào phần chính.

### 2.2. Biến mệnh đề và tri thức công khai

Định nghĩa C_i = True khi người i là Criminal, False khi Innocent. Một biến chính cho mỗi người; biến phụ encoder được đánh số sau các biến chính.

Đưa công thức:

`KB_t = CNF(các clue đã mở ở bước t) ∧ các unit clause cho trạng thái đã biết`.

Giải thích các thẻ ban đầu công khai đồng thời trạng thái và clue. Hidden solution và các clue chưa mở không thuộc KB_t. Việc bộ nạp kiểm tra tính đúng/duy nhất của đề là một bước xác thực riêng; không được dùng kết quả riêng tư này để chọn hint hay phán quyết trong phiên chơi.

### 2.3. Giao thức reveal

Vẽ sơ đồ: chọn người chưa giải → kiểm tra entailment → từ chối hoặc chấp nhận → công khai đồng thời trạng thái và clue → tăng revision → phân tích lại.

| Kết quả | Điều kiện | Thay đổi trạng thái |
|---|---|---|
| ACCEPTED | Phán quyết được suy ra và khớp đề hợp lệ | Mở trạng thái + clue, ghi một bước trace |
| NOT_PROVABLE | Cả hai trạng thái vẫn có model | Không thay đổi |
| CONTRADICTED | Trạng thái đối lập được suy ra | Không thay đổi |
| INCONSISTENT | KB hiện tại UNSAT hoặc có mâu thuẫn nội bộ | Không mở clue |

UNKNOWN là kết quả phân loại của một người chưa được xác định; không phải một trạng thái thật trong solution. INVALID/PENDING là trạng thái thao tác/phân tích của ứng dụng, không thay thế bốn kết quả logic trên.

### 2.4. Nghiệm duy nhất và khả năng giải tiến triển

- Một đề hợp lệ phải có đúng một phép gán cho bộ clue đầy đủ.
- Có nghiệm duy nhất khi biết toàn bộ clue không đảm bảo người chơi suy ra được bước đầu từ các clue đang mở.
- Dùng `examples/diagnostics/01_stalled.json` để minh họa: bộ clue đầy đủ UNIQUE nhưng không có clue/trạng thái ban đầu nên phiên công khai STALLED.

## 3. Thiết kế hệ thống và giao diện

### 3.1. Sơ đồ kiến trúc

Trình bày sơ đồ `cases/vault → PublicSnapshot → reasoning → investigation → desktop` và nhánh `reports` chạy không cần GUI.

| Thành phần | Trách nhiệm | File chính |
|---|---|---|
| Game Engine / kho riêng | Giữ đề đầy đủ, xác nhận reveal | cases/vault.py |
| Điều phối phiên | Kiểm tra revision, xử lý phán quyết và journal | investigation/coordinator.py |
| Logic Agent | Chỉ nhận public snapshot, phân loại và tìm forced move | reasoning/inference.py |
| Encoder và evaluator | Biên dịch tự động; đánh giá trực tiếp độc lập | reasoning/compiler.py, truth.py |
| SAT solver | DPLL đệ quy tự cài đặt | reasoning/search.py |
| GUI | Bảng thẻ, evidence, history, metrics, controls | desktop/ |
| Thí nghiệm | Giới hạn thời gian từng lượt, xuất kết quả | reports/ |

Giải thích frozen dataclass/tuple, session ID và revision ngăn dùng kết quả cũ sau Restart/chuyển đề. Worker riêng nhận duy nhất public snapshot; GUI không bị chặn bởi DPLL. Không cần liệt kê mọi hàm trong báo cáo.

### 3.2. Các hình GUI nên chụp

1. Trạng thái ban đầu: tọa độ, tên/nghề, thẻ úp và clue của thẻ ngửa.
2. Chọn clue công khai và các ô được highlight.
3. NOT_PROVABLE hoặc CONTRADICTED, chứng minh thẻ chưa mở.
4. ACCEPTED: trạng thái thay đổi, mặt ngửa và clue mới xuất hiện.
5. Auto Solve hoàn thành; tab Chronology/Analysis.

Mỗi hình cần chú thích giải thích hành vi, không chỉ ghi “giao diện chương trình”. Nêu Load, Restart, Hint và Auto Solve có thể dùng ở hai chế độ Hands-on/Observe. Việc đổi mặt thẻ là thay đổi hiển thị từ “Face down / Statement sealed” sang trạng thái và clue công khai; không cần khẳng định có hoạt ảnh 3D.

## 4. Ngữ nghĩa clue và mã hóa CNF

### 4.1. Sáu template bắt buộc

| Template | Ngữ nghĩa |
|---|---|
| FACT(i, Criminal) / FACT(i, Innocent) | C_i / ¬C_i |
| SAME(i,j) | C_i ↔ C_j |
| DIFFERENT(i,j) | C_i XOR C_j |
| EXACTLY(k,R) | Tổng C_i trên R bằng k |
| AT_LEAST(k,R) | Tổng C_i trên R ≥ k |
| AT_MOST(k,R) | Tổng C_i trên R ≤ k |

Mô tả bốn vùng bắt buộc: ROW, COLUMN, NEIGHBORS gồm tám hướng và loại chính ô trung tâm, EXPLICIT không trùng tọa độ. Nêu kiểm tra 0 ≤ k ≤ |R|, tọa độ hợp lệ, vùng không rỗng.

### 4.2. Ít nhất hai mở rộng

- PARITY: tổng Criminal trong vùng chẵn/lẻ; biên dịch thành chuỗi XOR với số gate tăng tuyến tính.
- IMPLIES: C_a → C_b, CNF là (¬C_a ∨ C_b).
- Các vùng CORNERS và BOUNDARY là hai khả năng bổ sung nữa. Không tính AT_LEAST/AT_MOST là mở rộng vì chúng đã là yêu cầu cơ bản.
- Cho một ví dụ thật trong các đề mẫu và chỉ ra evaluator/CNF xử lý giống nhau.

### 4.3. Ví dụ suy diễn binary — bắt buộc có ít nhất một

Với SAME(A1,B1), đặt x = C_A1, y = C_B1:

`x ↔ y = (x → y) ∧ (y → x) = (¬x ∨ y) ∧ (x ∨ ¬y)`.

Giải thích code dùng biến phụ z cho `z ↔ (x XOR y)` rồi thêm `¬z`. Với x=1, y=2, z=3, đúng các clause được sinh là:

```text
(1 ∨ 2 ∨ ¬3)
(1 ∨ ¬2 ∨ 3)
(¬1 ∨ 2 ∨ 3)
(¬1 ∨ ¬2 ∨ ¬3)
(¬3)
```

Khi cố định x,y, tồn tại phép gán z thỏa CNF khi và chỉ khi x=y. Không viết rằng mã hiện tại chỉ sinh hai clause trực tiếp cho SAME.

### 4.4. Ví dụ suy diễn counting — bắt buộc có ít nhất một

Chọn AT_MOST(1,{A1,B1,C1}), đặt x,y,z là ba biến chính. Dạng trực tiếp tương đương:

`(¬x ∨ ¬y) ∧ (¬x ∨ ¬z) ∧ (¬y ∨ ¬z)`.

Sau đó giải thích cách code thực sự dùng prefix counter. Đặt p: prefix đầu đã có ít nhất một Criminal; q: prefix gồm hai người đã có ít nhất một Criminal. Encoder tạo:

```text
(¬x ∨ p)       x bắt buộc bật cờ p
(¬y ∨ ¬p)      nếu p đã bật thì y không được là Criminal
(¬y ∨ q)       y cũng có thể bật q
(¬p ∨ q)       cờ đếm truyền sang prefix sau
(¬z ∨ ¬q)      q đã bật thì z không được là Criminal
```

Với x=1,y=2,z=3,p=4,q=5: `(-1,4), (-2,-4), (-2,5), (-4,5), (-3,-5)`; đây là kết quả đã kiểm tra với encoder hiện tại. Phép gán có hai hoặc ba Criminal tạo mâu thuẫn; với không quá một Criminal luôn có thể chọn p,q phù hợp. Biến phụ chỉ cần tồn tại một cách gán, không bắt buộc được xác định duy nhất.

Nêu cách ghép: `AT_LEAST(k,x) = AT_MOST(n-k,¬x)` và `EXACTLY(k)=AT_LEAST(k)∧AT_MOST(k)`. Giải thích k=0 và k=n; không liệt kê CNF viết tay riêng cho từng puzzle. Có thể nói các counter có kích thước O(nk), thường O(n²), còn DPLL vẫn có thể tốn thời gian mũ.

### 4.5. Kiểm chứng encoder

Mô tả kiểm thử truth table: cố định mọi phép gán biến chính trên một miền nhỏ, so sánh evaluator trực tiếp với việc tồn tại phép gán biến phụ làm CNF SAT. Evaluator không gọi compiler. Có 352 tổ hợp clue/phép gán trong bài kiểm thử bốn ô, bao phủ count boundary và hai parity.

## 5. Thuật toán

### 5.1. DPLL đệ quy

Trình bày pseudocode có lời gọi đệ quy thực sự:

```text
DPLL(clauses, assignment):
    simplify clauses under assignment
    if an empty clause exists: return UNSAT
    if no clause remains: return completed SAT assignment
    propagate units; repeat simplification
    optionally eliminate pure literals; repeat
    choose a deterministic unassigned variable v
    try DPLL(clauses, assignment ∪ {v=True})
    if failed: backtrack and try v=False
    if both failed: return UNSAT
```

Giải thích chiến lược hiện tại: ưu tiên biến chính còn xuất hiện; tần suất cao trước, hòa thì số biến nhỏ trước; thử True rồi False. Biến phụ được xét khi cần. Quy ước counters: decisions là số điểm chọn nhánh, propagations là unit assignments, backtracks là số nhánh con thất bại, runtime đo bằng perf_counter. Mâu thuẫn ở gốc chưa có nhánh không tự tính thành backtrack.

Đưa ví dụ cần quay lui, không chỉ ví dụ giải hoàn toàn bằng unit propagation: `(x∨y)∧(¬x∨y)∧(¬x∨¬y)`. Nhánh x=True mâu thuẫn; quay lui x=False cho model y=True.

### 5.2. Entailment và UNKNOWN

Trước tiên kiểm tra KB có SAT. Sau đó, với mỗi người chưa giải:

- `KB ∧ ¬C_i` UNSAT ⇒ Criminal.
- `KB ∧ C_i` UNSAT ⇒ Innocent.
- Cả hai SAT ⇒ UNKNOWN.
- KB UNSAT ⇒ INCONSISTENT, không sử dụng nguyên lý bùng nổ để mở tất cả thẻ.

Giải thích một model SAT không đủ kết luận người đang xét. Thêm một ví dụ có một người forced và một người UNKNOWN.

### 5.3. Uniqueness check riêng

1. Biên dịch toàn bộ clue, không thêm hidden solution làm unit clauses.
2. Tìm model M; nếu không có thì INCONSISTENT.
3. Tạo blocking clause chỉ từ các biến chính: `∨(¬C_i nếu M(C_i)=True, C_i nếu M(C_i)=False)`.
4. Giải lại: UNSAT ⇒ UNIQUE, SAT ⇒ MULTIPLE.

Không block các biến phụ: nhiều cách gán counter không đồng nghĩa có hai nghiệm bàn cờ. Phân biệt uniqueness bộ clue đầy đủ với uniqueness KB công khai đang hiển thị trong GUI.

### 5.4. Deduction loop và trace thực tế

Chọn forced move đầu tiên theo row-major, submit qua Game Engine, mở clue, cập nhật KB, lặp đến solved/stalled/inconsistent/error. Hint dùng cùng forced move nhưng không reveal.

Đưa một bước thật từ `output/deduction_traces.json`, ví dụ bước đầu ledger_01:

| Trường | Giá trị đã quan sát |
|---|---|
| step | 1 |
| active_clues | PL1-01, PL1-09 |
| cell / verdict | A2 / CRIMINAL |
| truy vấn phủ định | KB ∧ ¬C_A2; assumptions [-4]; UNSAT |
| truy vấn khẳng định | KB ∧ C_A2; assumptions [4]; SAT |
| revealed_clue | PL1-07, SAME(A2,C2) |

Trace ghi log mọi truy vấn phân loại trong bước; không nhầm tổng sat_calls với nội dung truy vấn. Active clues là trạng thái trước khi mở clue mới.

## 6. Kiểm thử và thí nghiệm

### 6.1. Môi trường và khả năng tái lập

- Ghi Python implementation/version, hệ điều hành, cấu hình máy thực tế và timeout; không sao chép cấu hình máy khác.
- Ghi lệnh chạy và thư mục làm việc `griductive-rebuild`.
- Sáu đề mẫu cố định: hai 3×3, hai 4×4, hai stress 5×5. Cùng chính xác các file cho pure-literal OFF/ON.
- Runtime trong CSV là thời gian vòng suy diễn, chưa gồm xác thực nạp file, full-clue uniqueness cuối lượt và khởi động process. Timeout lại giới hạn toàn lượt worker, bao gồm các phần này. Ghi rõ phạm vi thay vì coi hai số đo giống nhau.
- sat_calls/decisions/propagations/backtracks chính thống kê truy vấn phân loại; kiểm tra uniqueness được loại khỏi counters này.

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python -m proofledger.reports --output output --timeout 30
python -m proofledger.reports --puzzles examples/diagnostics --output output/diagnostics --timeout 30
python -m proofledger.reports --output output/timeout_probe --timeout 0.001
```

Hai lệnh cuối cố tình tạo kết quả chưa giải/lỗi/timeout và trả exit code 1 sau khi vẫn xuất đủ các hàng. Exit code 2 dành cho cấu hình đầu vào cấp lệnh không hợp lệ, chẳng hạn thư mục rỗng hoặc timeout không dương/hữu hạn. Timeout 0.001 là kiểm thử cơ chế timeout, không phải chứng cứ đề mẫu không giải được với giới hạn bình thường.

### 6.2. Bảng kết quả chính — lấy số trực tiếp từ CSV mới nhất

Các cột cần có: case, kích thước, primary, auxiliary, CNF clauses, SAT calls, decisions, propagations, backtracks, deduction steps, runtime, status. Không bỏ các hàng thất bại.

Nguồn: `output/experiments.csv`. Dùng `output/pure_literal_ablation.csv` cho bảng so sánh OFF/ON, có cùng source_file. Dùng `output/deduction_traces.json` cho các bước chứng minh. Nếu thời gian cho phép, chạy nhiều lần và trình bày median/min/max; nếu chỉ một lần, ghi rõ chỉ có một phép đo và không suy diễn độ tin cậy thống kê.

### 6.3. Nhận xét có thể kiểm chứng

- Số biến chính bằng N²; auxiliary/clause phụ thuộc dạng clue và vùng, không chỉ kích thước lưới.
- ledger_05 chứa boundary cardinality lớn nên chậm hơn một số case cùng kích thước; chỉ gọi đó là quan sát của tập dữ liệu này.
- Pure-literal ON có thể giảm propagation/branching nhưng không đảm bảo runtime luôn tốt hơn vì phải tìm pure literals và có nhiễu đo thời gian. Ví dụ lần chạy đã ghi nhận ledger_06 ON chậm hơn OFF; không xóa số đo này.
- Backtracks bằng 0 trên một số puzzle không có nghĩa thuật toán thiếu backtracking; bài kiểm thử nhánh mâu thuẫn riêng xác nhận chức năng đó.
- Các đề mẫu có hai thẻ công khai nên số lần reveal thêm lần lượt 7/14/23. Không đếm starting reveals thành deduction steps.

### 6.4. Bảng failure cases

| Trường hợp | Kết quả mong đợi | Bằng chứng |
|---|---|---|
| Full clues duy nhất nhưng không có starting evidence | STALLED, 0 bước, không đoán | output/diagnostics |
| Vòng SAME chỉ xác định hai phép gán đồng nhất | INVALID khi nạp vì không UNIQUE | output/diagnostics |
| Một clue sai dưới solution | INVALID | output/diagnostics |
| Giới hạn worker 0.001 giây | TIMEOUT, giữ hàng; counters chưa có để trống | output/timeout_probe |
| Public snapshot chứa hai fact đối lập | INCONSISTENT, không hint/reveal | test_inference_contracts.py |
| Phán quyết đúng solution nhưng chưa suy ra | NOT_PROVABLE, không đổi state | test_investigation_flow.py |

### 6.5. Bảng kiểm thử theo yêu cầu

Gom thành các nhóm: loader/regions, evaluator↔CNF, SAT model oracle, entailment/uniqueness, reveal không rò rỉ, automation/reset/revision, GUI, exports/timeout. Ghi tổng test thực tế từ lần chạy cuối, số fail/error/skip; không giữ số từ bản cũ nếu đã sửa thêm tests.

## 7. Đánh giá, giới hạn và hướng phát triển

- Nêu phần đã đáp ứng và liên kết `docs/COURSE_REQUIREMENTS.md`; không tự khẳng định được đủ điểm khi chưa có đánh giá của giảng viên.
- Giới hạn: DPLL thời gian mũ, GUI/import chỉ hỗ trợ N=3–5, không save session, không NLP, full-clue uniqueness không bảo đảm progressive solvability, chưa chứng nhận mọi nền tảng/DPI.
- Có thể phát triển: giải thích proof ngắn hơn, SAT incremental/heuristic tốt hơn, kiểm tra progressive solvability khi biên soạn puzzle, thêm clue/region và bộ dữ liệu khó hơn.
- Phân biệt hạng mục đã cài với ý tưởng tương lai; không mô tả ý tưởng thành tính năng hiện có.

## 8. Tài liệu tham khảo và phụ lục

### 8.1. Tham khảo

- Đề CSC14003 Project 2 được cung cấp, dẫn đúng mục/trang.
- Dự án tham chiếu Griductive Solver: https://github.com/TranTai35/griductive-solver; mô tả vai trò là tham chiếu hành vi, xem NOTICE.md. Không giả định giấy phép đã được xác định.
- Thêm các bài báo/sách/tài liệu Python/Tkinter/SAT mà nhóm thực sự đã đọc; ghi đủ tác giả, tên, năm, URL/ngày truy cập khi có. Không liệt kê nguồn chưa sử dụng chỉ để làm dài danh mục.

### 8.2. Phụ lục AI — phải mô tả trung thực

- Công cụ: Codex đã hỗ trợ phân tích, tạo/sửa mã, kiểm thử, rà yêu cầu và soạn dàn ý. Nhóm cần tự xác nhận phần đã review và hiểu, không tự nhận toàn bộ mã được viết tay không có AI.
- Ghi các prompt thực tế: yêu cầu “spec-first reimplementation”; yêu cầu đối chiếu PDF và sửa/bổ sung; yêu cầu chỉ cung cấp dàn ý thay vì tạo báo cáo PDF.
- Bảng đề xuất: prompt/mục đích → sản phẩm AI tạo → cách nhóm kiểm chứng → điều chỉnh của nhóm. Điền từ quá trình làm việc thực tế.
- Đưa các kiểm chứng độc lập: truth table, CNF oracle, trace SAT/UNSAT, manual GUI checks và lần chạy thí nghiệm.
- Không đưa khóa truy cập/thông tin tài khoản hoặc toàn bộ hội thoại riêng tư không liên quan vào phụ lục.

### 8.3. Phụ lục kỹ thuật

- Hướng dẫn cài/chạy, schema JSON, tên và ý nghĩa cột CSV, trích trace, định nghĩa counters, kết quả kiểm thử.
- Các ví dụ CNF dài, log lỗi chi tiết và bảng raw có thể để ở đây thay vì chen vào phần chính.

## 9. Kịch bản video 5–10 phút

Gợi ý khoảng 7 phút, có lời bình hoặc phụ đề tiếng Việt/Anh:

| Thời gian gợi ý | Nội dung cần quay |
|---|---|
| 0:00–0:40 | Giới thiệu mục tiêu no-guess, tên nhóm/sản phẩm |
| 0:40–1:30 | Nạp đề 3×3; tên/nghề, tọa độ, thẻ úp/ngửa, starting clues |
| 1:30–2:30 | Chơi tay: NOT_PROVABLE/CONTRADICTED rồi ACCEPTED; thẻ mới mở |
| 2:30–3:20 | Chọn clue, highlight đúng vùng; Hint không làm reveal |
| 3:20–4:30 | Restart; Auto Solve, Pause/Resume; hiện bàn cờ giải xong |
| 4:30–5:20 | Đề 4×4 và stress 5×5; Observe mode và Analysis |
| 5:20–6:20 | Chronology, hai truy vấn giả định SAT/UNSAT, uniqueness |
| 6:20–7:00 | Thí nghiệm/CSV, ví dụ STALLED và giới hạn của chương trình |

Đây là kịch bản để nhóm quay, chưa phải video đã tạo. Upload Google Drive, bật quyền xem qua link, tự kiểm tra bằng cửa sổ ẩn danh và đưa URL vào Report.pdf. Đề không chấp nhận link YouTube.

## 10. Checklist nộp bài

```text
StudentID1_StudentID2_.../
  Source/
    main.py
    README.md
    requirements.txt
    src/proofledger/...
    tests/...
    output/...
  Report.pdf       # chứa link demo Drive đã kiểm tra quyền
```

- Thay StudentID bằng MSSV thật và giữ đúng tên archive `.zip`/`.rar`.
- Không nén `.qa`, virtualenv, caches, build tạm hoặc các file cá nhân.
- Source có thể chạy bằng `python main.py` từ thư mục Source; Tkinter/Tcl-Tk phải có trong Python.
- Có helper `python tools/prepare_submission.py --ids MSSV1 MSSV2 --report duong-dan/Report.pdf`; chỉ dùng khi nhóm đã hoàn thành PDF thật. Helper không tạo báo cáo, không tải lên Drive và không tự xác nhận quyền video.
- Nếu file nén lớn hơn 20 MB, đề yêu cầu chia sẻ qua Google Drive. Không sửa sau hạn nộp. Đề chỉ nói thời lượng dự án xấp xỉ ba tuần, không cung cấp ngày deadline cụ thể trong PDF này.
