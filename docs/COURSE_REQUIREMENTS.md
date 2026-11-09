# Đối chiếu yêu cầu đề CSC14003 Project 2

Ngày rà soát: 08/11/2026. Nguồn: `[2526 HK3] IntroAI - Project 2 (1).pdf` trong thư mục dự án, đã đọc đủ 9 trang và kiểm tra bản render các trang yêu cầu. Đây là kiểm tra kỹ thuật theo đề, không phải điểm chấm chính thức.

Người dùng yêu cầu sửa mã khi cần và chỉ cung cấp **dàn ý báo cáo**, không tạo Report.pdf. Dàn ý và kịch bản video nằm trong `REPORT_OUTLINE_VI.md`. Báo cáo PDF, video thật, thông tin thành viên và nộp bài do nhóm hoàn thiện.

## Kết quả đối chiếu

| Mục đề / trang | Yêu cầu | Trước rà soát | Hiện tại / bằng chứng |
|---|---|---|---|
| 2.1 / 2 | N=3,4,5; tọa độ; tên theo alphabet | Có lưới, tên mẫu chưa theo alphabet | Đã sắp lại identity mẫu theo row-major và kiểm tra alphabet khi nạp; test_case_import |
| 2.1–2.2 / 2 | Clue luôn thật; public chỉ gồm starting reveals và các bước được chứng minh | Đã có | Vault/PublicSnapshot; rejected verdict không đổi state; test_investigation_flow |
| 2.2 / 2 | Đề hợp lệ có đúng một nghiệm đầy đủ | Chỉ kiểm tra clue đúng, chưa bắt buộc uniqueness | Bộ nạp yêu cầu full-clue UNIQUE, không dùng solution làm unit; test multiple assignments bị từ chối |
| 3.1 / 3 | Biến chính deterministic, biến phụ tách biệt | Đã có | Circuit đánh số biến chính trước, auxiliary sau; uniqueness chỉ block biến chính |
| 3.2 / 3 | Sáu clue bắt buộc và ít nhất hai mở rộng | Đã có | FACT/SAME/DIFFERENT/EXACTLY/AT_LEAST/AT_MOST; PARITY, IMPLIES, CORNERS, BOUNDARY |
| 3.3 / 4 | Tự sinh CNF, không viết tay mỗi puzzle | Đã có | compiler.py nhận cấu trúc clue; không có CNF riêng cho từng đề mẫu |
| 3.4 / 4 | Entailment bằng truy vấn giả định; UNKNOWN và INCONSISTENT | Đã có | analyze() kiểm tra baseline, hai giả định cho người chưa giải; exhaustive oracle |
| 4.1 / 5, 10 điểm | GUI hiển thị tên/nghề, trạng thái, clue ngửa/thẻ úp | Tên/nghề chỉ hiện khi chọn, tile chưa có clue | Mỗi thẻ hiện tên/nghề, Face down/up, trạng thái và chỉ clue công khai; GUI test và live inspection |
| 4.1 / 5 | Chơi tay, chấp nhận đúng và đổi mặt thẻ | Đã có chức năng | Thẻ chuyển từ sealed sang clue, hiện verdict; không cần hoạt ảnh 3D |
| 4.1 / 5 | Phân biệt NOT_PROVABLE/CONTRADICTED | Logic có nhưng UI chưa hiện token | UI hiện đúng token cùng giải thích; không mở clue khi bị từ chối |
| 4.1 / 5 | Chọn clue và highlight tham chiếu | Đã có | Evidence/card selection; sáu loại region và binary references |
| 4.1 / 5 | Load, Restart, Hint, Auto Solve | Có chức năng với tên khác | Nhãn Load JSON, Restart, Hint, Auto Solve/Pause; vùng điều khiển/thông báo được ghim ngoài vùng cuộn |
| 4.1 / 5 | Game Engine riêng với Logic Agent | Đã có | cases/vault giữ bí mật; reasoning chỉ dùng public contracts; worker không nhận Definition |
| 4.2 / 6, 10 điểm | Validation, encoder tái sử dụng, known unit clauses, counters | Đã có | import_json, regions, compiler; Analysis/CSV hiện primary/auxiliary/clauses |
| 4.2 / 6 | Semantic evaluator độc lập cho mỗi core clue | Đã có | truth.py không gọi compiler; 352 tổ hợp truth table/CNF |
| 4.3 / 6, 10 điểm | Unit propagation, conflict, chọn biến deterministic | Đã có | search.py; generated CNF oracle với pure OFF/ON |
| 4.3 / 6 | **Recursive branching and backtracking** | DPLL dùng stack tường minh, chưa đúng chữ “recursive” | Đã đổi thành lời gọi đệ quy visit(); test nhánh đầu thất bại và quay lui |
| 4.3 / 6 | SAT có model đầy đủ hoặc UNSAT; counters/time | Đã có | Model điền đủ biến; counters tách backtracks khỏi root conflict |
| 4.4 / 7, 20 điểm | Phân loại mọi người chưa giải, chỉ chọn forced, reveal rồi lặp | Đã có | inference/coordinator/automation; all samples solve OFF/ON; stalled không đoán |
| 4.4 / 7 | Trace gồm step, active clues, SAT queries, verdict, clue mới | Chỉ có số SAT calls và ID clue | Đã thêm từng assumption/result SAT/UNSAT và revealed_statement đầy đủ; JSON và Chronology |
| 4.4 / 7 | Kiểm tra uniqueness riêng cho complete clue set | Đã có trong batch nhưng chưa validate input | Vẫn có check riêng; nay thêm gate xác thực puzzle hợp lệ trước chơi |
| 4.5 / 7, 10 điểm | Nhiều đề 3×3/4×4; stress 5×5; đủ metrics | Đã có | 2+2+2 đề gốc mới; experiments.csv, ablation CSV, deduction trace |
| 4.5 / 7 | Cùng tập đề khi so sánh; giữ failures/timeouts | Lỗi file có thể làm hủy cả batch; chưa có timeout | Mỗi input/mode chạy worker có timeout; SOLVED/STALLED/INVALID/ERROR/TIMEOUT được giữ trong CSV; ghép theo source_file |
| 4.6 / 8, 30 điểm | Report.pdf đủ kế hoạch, mô hình, derivations, thuật toán, experiments, references/AI | Chưa có PDF | Theo phạm vi người dùng: cung cấp dàn ý chi tiết, không tạo PDF hoặc bịa đóng góp thành viên |
| 4.7 / 8, 10 điểm | Video 5–10 phút, GUI + chơi tay/solver, lời bình/phụ đề VI/EN, Drive công khai | Chưa có video | Có kịch bản 7 phút và checklist quyền ẩn danh; nhóm cần tự quay/upload; không có link YouTube thay thế |
| 5 / 9 | Archive tên MSSV, Source/main.py/README/requirements, Report.pdf chứa video URL | Chưa có direct entry và requirements | Đã thêm main.py, requirements.txt và helper đóng gói chọn lọc; chưa tạo archive nộp bài vì chưa có Report.pdf/MSSV |
| 6 / 9 | Bài nhóm; AI được phép và phải minh bạch; không sửa sau deadline | Chưa có hướng dẫn báo cáo cụ thể | Dàn ý yêu cầu đóng góp thật, khai báo Codex/prompts/kiểm chứng; không tự suy đoán ngày deadline |

## Thí nghiệm tái lập

Từ thư mục griductive-rebuild:

```powershell
$env:PYTHONPATH = "src"
python -m proofledger.reports --output output --timeout 30
python -m proofledger.reports --puzzles examples/diagnostics --output output/diagnostics --timeout 30
python -m proofledger.reports --output output/timeout_probe --timeout 0.001
```

Kết quả đã quan sát: sáu đề mẫu SOLVED, full clues UNIQUE, số bước 7/7/14/14/23/23. Bộ diagnostic giữ một STALLED và hai INVALID. Timeout probe giữ sáu TIMEOUT trong cả hai chế độ. Probe chỉ kiểm tra đường timeout với ngưỡng cố tình quá nhỏ; không dùng nó để kết luận hiệu năng puzzle.

CSV giữ các cột metrics cũ và thêm status/error/source_file. Counters chưa có ở một lượt timeout được để trống, không điền số 0 giả. Một puzzle ID trùng ở các file khác vẫn giữ từng hàng và từng trace, không bị ghi đè. Counter SAT chính chỉ gồm phân loại, không cộng uniqueness; runtime giới hạn và cách đo được giải thích trong README/dàn ý.

## Những mục còn thuộc phần nhóm hoàn thiện

1. Báo cáo PDF từ dàn ý, với phân công/tỷ lệ hoàn thành thật và link demo.
2. Video có lời bình/phụ đề, upload Drive, kiểm tra quyền bằng cửa sổ ẩn danh.
3. Archive tên MSSV thật, nộp đúng hạn. Helper không tự xác minh quyền Drive hay thời hạn lớp.

Không tuyên bố đã hoàn tất ba mục này chỉ vì mã nguồn đã chạy qua kiểm thử. Số test và kiểm tra đóng gói cuối cùng được ghi trong PARITY.md.

## Kiểm tra cuối cùng đã thực hiện

| Lệnh / kiểm tra | Kết quả |
|---|---|
| `python -m ruff check .` | Pass |
| `python -m compileall -q src main.py tools` | Pass |
| `python -m unittest discover -s tests -v` | **40 test pass**, không fail/error/skip; lần cuối 13.731 giây |
| `python -m build --wheel --no-isolation` | Build wheel thành công |
| Cài lại wheel bằng `--no-index --no-deps` trong venv riêng | Pass |
| Smoke GUI/worker/hint từ wheel đã cài, không dùng source PYTHONPATH | Pass |
| Bộ sáu đề mẫu, pure OFF và ON | Tất cả SOLVED; bộ clue đầy đủ UNIQUE |
| Bộ chẩn đoán và timeout probe | Các hàng STALLED/INVALID/TIMEOUT được giữ đúng |
| Chạy thử helper đóng gói trong `.qa/archive-smoke` | Đúng cấu trúc Source/main.py, requirements và Report.pdf; không có cache/virtualenv/build. Chỉ dùng PDF đề làm đầu vào kiểm thử, không phải báo cáo nộp bài |
| Kiểm tra trực quan GUI sau sửa | Mỗi thẻ hiện tên/nghề, Face down/up; CONTRADICTED giữ clue kín và hiện rõ ở footer; phán quyết được chứng minh mở thẻ/clue và highlight đúng tham chiếu |

Git từ đầu lượt kiểm tra đã có thao tác di chuyển PDF đề của người dùng từ thư mục cha vào dự án mới. Không khôi phục/ghi đè thao tác có sẵn đó; mọi sửa mã và tài liệu ở lượt này nằm trong griductive-rebuild.
