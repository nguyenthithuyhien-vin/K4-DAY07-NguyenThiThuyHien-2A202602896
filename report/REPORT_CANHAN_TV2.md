# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Thị Thuý Hiền
**Nhóm:** G69 (K4-L3B)
**Ngày:** 2026-09-20
**Vai trò Phase 1:** Dẫn EmbeddingStore + KnowledgeBaseAgent; review chunking

> **Nộp 1 bản / sinh viên.** Phần nhóm nộp chung trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Cosine cao nghĩa là hai embedding “cùng hướng”: hệ thống coi hai đoạn văn gần nghĩa dù từ ngữ không hoàn toàn trùng.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sản phẩm lỗi do nhà sản xuất được bảo hành 12 tháng.
- Câu B: Thời hạn bảo hành chính hãng là một năm nếu lỗi kỹ thuật từ NSX.
- Tại sao tương đồng: cùng mô tả thời hạn và điều kiện bảo hành.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Sản phẩm lỗi do nhà sản xuất được bảo hành 12 tháng.
- Câu B: Phí vận chuyển quốc tế được tính theo khối lượng và vùng giao.
- Tại sao khác: bảo hành sản phẩm vs phí ship quốc tế — hai chủ đề policy khác nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Với embedding, độ dài vector thường không phản ánh “mức độ liên quan”; cosine chuẩn hóa theo độ dài nên so sánh hướng nghĩa ổn định hơn khoảng cách Euclid.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Công thức lab:* `ceil((độ_dài - overlap) / (chunk_size - overlap))`
> `ceil((10000 - 50) / (500 - 50)) = ceil(22.111…) → 23`
> *Đáp án:* **23**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Tăng lên 25 chunk (`ceil(9900/400)=25`) vì bước trượt nhỏ hơn. Overlap giúp mang ngữ cảnh biên sang chunk kế tiếp, giảm mất thông tin khi câu/điều khoản nằm giữa hai đoạn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Vai trò của tôi: dẫn `store.py` / `agent.py`; review phần chunking Tạ Đăng Dương đã viết để hiểu đủ khi giải thích trong báo cáo.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Khi review: tách câu bằng lookbehind để giữ dấu câu, rồi nhóm theo `max_sentences_per_chunk`. Text rỗng phải trả list rỗng. Tôi lưu ý edge case viết tắt tiếng Việt (`v.v.`) vẫn có thể bị split nhầm — ghi nhận khi phân tích lỗi Phase 2.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Hiểu thuật toán hai chiều: đệ quy xuống separator nhỏ hơn khi mảnh còn dài, rồi merge các mảnh ngắn. Base case quan trọng với `separators=[]` (hard-split) — thiếu nhánh này sẽ fail test. Ở Phase 2 tôi sẽ tinh chỉnh `chunk_size`/separators trên corpus policy.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` thành record: embed content, copy metadata, đảm bảo có `doc_id`. Search: embed query → dot product với mọi embedding → sort giảm dần → cắt `top_k`. Cố ý không trả field `embedding` ra ngoài để output gọn.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Filter **trước** search: nếu lọc sau top-k sẽ dễ mất hết kết quả đúng. `delete_document` lọc bỏ mọi chunk cùng `doc_id` (hữu ích khi một file bị chunk thành nhiều record). Không dùng nhánh Chroma trong lab để tránh `_use_chroma=True` khi client chưa sẵn sàng.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Pipeline RAG tối giản: `store.search` → ghép context có số thứ tự và source → prompt yêu cầu chỉ dùng context + cite `[n]` → `llm_fn(prompt)`. Nếu không có chunk nào thì trả chuỗi báo thiếu context thay vì crash.

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

Embedding: `LocalEmbedder` (cùng backend với Tạ Đăng Dương, cặp câu khác).

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Shopee Đảm Bảo cho phép trả hàng trong 15 ngày. | Người mua được bảo vệ bằng chính sách đảm bảo của sàn. | cao | 0.222 | Không (thấp) |
| 2 | Bảo hành do người bán hoặc nhà sản xuất thực hiện. | Shopee không phải bên thực hiện nghĩa vụ bảo hành. | cao vừa | 0.218 | Không (thấp hơn kỳ vọng) |
| 3 | Người bán chịu phí vận chuyển trả hàng tối đa 40000 VND. | Cửa hàng phải trả phí ship khi khách đổi ý trả hàng. | cao | 0.408 | Một phần |
| 4 | Đơn hàng chưa giao đúng hạn có thể hoàn tiền. | Công thức nấu phở bò truyền thống miền Bắc. | thấp | 0.077 | Có |
| 5 | Video mở hàng 6 mặt kiện là bằng chứng mạnh. | Quay video khi mở thùng hàng hoàn giúp khiếu nại thành công. | cao | 0.560 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 1–2 cùng chủ đề chính sách nhưng paraphrase khác mạnh → điểm thấp. Embedding bắt overlap từ vựng hơn là quan hệ logic “A chịu trách nhiệm / B không chịu”. Cặp 4 (policy vs công thức nấu ăn) đúng là thấp — sanity check tốt.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chiến lược: **RecursiveChunker(chunk_size=400)**. Cùng 5 query với nhóm.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Thời hạn TH/HT? | “15 ngày… Giao hàng thành công” (general) | 0.79 | Có | 15 ngày (+ policy 24h ở #2) |
| 2 | Shopee Đảm Bảo? | Lệch sang phản hồi 02 ngày của seller trong policy | 0.84 | Một phần (dam-bao ở #2) | Context lẫn; có đoạn chưa nhận hàng |
| 3 | Phản hồi hoàn tiền? (+ filter seller) | FAQ seller hoàn tiền ngay / 2 ngày | 0.75 | Có | 2 ngày khiếu nại |
| 4 | Nghĩa vụ bảo hành? | Chunk returns “Shopee đảm bảo quyền lợi” | 0.68 | Không | Sai hướng — failure |
| 5 | Menu Kênh Người Bán? | Overview TH/HT/Hủy | 0.78 | Có | Đúng mục quản lý |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 3 / 5 (Q2 một phần; Q4 miss)

**A/B filter câu #3:** Không filter → top-1 là đoạn buyer-facing “02 ngày lịch” trong `return-refund-policy` (không phải FAQ seller). Có filter → toàn `audience=seller`.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Heading giữ được câu then chốt bảo hành nhờ prefix tiêu đề section; Recursive của tôi cắt mảnh quá generic. Sẽ thử tăng overlap ý nghĩa bằng prefix `doc_id`/title vào mọi chunk recursive.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 7 / 10 |
| **Tổng phần cá nhân** | **57 / 60** |
