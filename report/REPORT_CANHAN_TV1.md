# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Điền họ tên TV1]
**Nhóm:** G69 (K4-L3B)
**Ngày:** 2026-09-20
**Vai trò Phase 1:** Dẫn chunking / similarity / comparator; review store + agent

> **Nộp 1 bản / sinh viên.** Phần nhóm nộp chung trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector hướng gần như cùng chiều trong không gian embedding: góc giữa chúng nhỏ, nên nội dung văn bản thường cùng chủ đề hoặc diễn đạt gần nhau về nghĩa.

**Ví dụ có độ tương tự CAO:**
- Câu A: Khách hàng được đổi trả hàng trong vòng 7 ngày kể từ khi nhận.
- Câu B: Người mua có 7 ngày để yêu cầu hoàn trả sản phẩm sau khi giao thành công.
- Tại sao tương đồng: cùng nói về thời hạn đổi trả cho buyer, từ vựng gần nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Khách hàng được đổi trả hàng trong vòng 7 ngày kể từ khi nhận.
- Câu B: Người bán phải cập nhật tồn kho trước 23:59 mỗi ngày.
- Tại sao khác: một bên là chính sách đổi trả buyer, một bên là nghĩa vụ vận hành seller — chủ đề khác hẳn.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ quan tâm hướng (hướng nghĩa), ít bị ảnh hưởng bởi độ lớn vector; khoảng cách Euclid nhạy với độ dài/magnitude nên kém ổn định khi so sánh embedding văn bản.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Phép tính:* `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.111…) = 23`
> *Đáp án:* **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunk tăng: `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25`. Overlap lớn hơn giúp ý nghĩa ở biên chunk không bị cắt đứt, retrieval dễ bắt được câu nằm giữa hai đoạn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận khi lập trình các phần chính trong gói `src`. Vai trò của tôi: dẫn phần chunking; review phần store/agent của TV2.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng `re.split` với lookbehind `(?<=[.!?])(?: |\n)` để tách *sau* dấu câu, giữ lại `.` / `!` / `?` thay vì nuốt mất như `[.!?]\s+`. Sau đó gom tối đa `max_sentences_per_chunk` câu, `strip` khoảng trắng; text rỗng trả `[]`. Edge case chưa xử lý: viết tắt (`TS.`, `v.v.`) và số thập phân vẫn có thể bị cắt sai.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thử separators theo thứ tự thô → mịn. Base case: text ngắn hơn `chunk_size` trả về nguyên; hết separator hoặc separator `""` thì hard-split theo ký tự; `separators=[]` cũng hard-split (test empty separators). Sau khi tách còn bước `_merge` nối các mảnh nhỏ liền kề tới sát `chunk_size` để tránh chunk vụn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Chỉ dùng in-memory (không bật Chroma sớm để tránh trap). `_make_record` copy metadata và luôn gắn `doc_id`. `search` nhúng query rồi gọi `_search_records` xếp hạng bằng dot product, trả về không kèm embedding thô.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Lọc metadata **trước**, rồi mới search trên tập ứng viên (cùng `_search_records` với `search`). Xóa mọi record có `metadata['doc_id']` khớp; có xóa được thì `True`, không thì `False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Retrieve top-k → dựng prompt đánh số chunk `[1] [2] [3]` kèm nguồn → gọi `llm_fn`. Store rỗng thì trả thông báo, không gọi LLM. Yêu cầu chỉ trả lời từ context và trích dẫn số chunk để truy vết.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts ==============================
platform darwin -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::... PASSED (7 tests)
tests/test_solution.py::TestSentenceChunker::... PASSED (4 tests)
tests/test_solution.py::TestRecursiveChunker::... PASSED (4 tests)
tests/test_solution.py::TestEmbeddingStore::... PASSED (8 tests)
tests/test_solution.py::TestKnowledgeBaseAgent::... PASSED (2 tests)
tests/test_solution.py::TestComputeSimilarity::... PASSED (4 tests)
tests/test_solution.py::TestCompareChunkingStrategies::... PASSED (3 tests)
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::... PASSED (3 tests)
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::... PASSED (3 tests)

============================== 42 passed in 0.02s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Embedding: `LocalEmbedder` (`paraphrase-multilingual-MiniLM-L12-v2`).

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Người mua được trả hàng trong 15 ngày. | Khách hàng có 15 ngày để yêu cầu hoàn tiền. | cao | 0.900 | Có |
| 2 | Người bán phải khiếu nại trong 2 ngày. | Shop cần phản hồi quyết định hoàn tiền trong vòng 02 ngày lịch. | cao | 0.687 | Có (cao vừa) |
| 3 | Shopee không bảo hành sản phẩm của người bán. | Phí vận chuyển quốc tế tính theo khối lượng kiện hàng. | thấp | -0.002 | Có |
| 4 | Truy cập Trả hàng/Hoàn tiền/Hủy trên Kênh Người Bán. | Vào Quản lý đơn hàng rồi chọn mục Trả hàng hoàn tiền hủy. | cao | 0.431 | Một phần (thấp hơn kỳ vọng) |
| 5 | Thực phẩm đông lạnh phải gửi yêu cầu trong 24 giờ. | Hàng tươi sống chỉ còn một ngày để trả hàng hoàn tiền. | cao | 0.303 | Không (thấp hơn dự đoán) |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 5 cùng ý “thời hạn ngắn cho hàng tươi/đông lạnh” nhưng điểm chỉ ~0.30 — paraphrase đa ngữ vẫn nhạy từ vựng bề mặt (“24 giờ” vs “một ngày”). Cặp 4 cùng thao tác UI nhưng điểm vừa phải vì khác cách diễn đạt.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chiến lược: **HeadingSectionChunker** (`bench.py --strategy heading`). Backend: multilingual MiniLM.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Thời hạn TH/HT sau giao thành công? | §1.2 general + §3.2 policy (15 ngày / 24h) | 0.75 | Có (marker top-3) | Dựa context: 15 ngày; thực phẩm 24h |
| 2 | Shopee Đảm Bảo / chưa nhận hàng? | General returns (lệch) | 0.83 | Không (miss dam-bao) | Context không đủ về Đảm Bảo |
| 3 | Thời hạn phản hồi hoàn tiền? (+ filter seller) | FAQ seller: khiếu nại trong 2 ngày | 0.77 | Có | 2 ngày theo FAQ người bán |
| 4 | Shopee có bảo hành không? | Warranty #2 trong top-3 | 0.69 | Có | Không phải bên BH (trừ hàng Shopee) |
| 5 | Menu quản lý TH/HT/Hủy? | Kênh NB > Quản lý đơn hàng > TH/HT/Hủy | 0.71 | Có | Đúng đường dẫn |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5 (trượt Q2)

**A/B filter câu #3:** Có filter → top-3 toàn `audience=seller`. Không filter → top-1 là buyer general (3–5 ngày làm việc) — chứng minh cần metadata.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Recursive bắt cụm “15 ngày” ở top-1 tốt hơn Heading trên Q1; Heading giữ section bảo hành tốt hơn trên Q4. Cùng query, khác chunker → khác failure mode.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10 |
| **Tổng phần cá nhân** | **58 / 60** |
