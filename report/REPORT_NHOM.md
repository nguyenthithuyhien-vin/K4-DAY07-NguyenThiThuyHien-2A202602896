# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** G69 (K4-L3B)
**Thành viên:** [Họ tên TV1], [Họ tên TV2]
**Ngày:** 2026-09-20

> **Nộp 1 bản / nhóm.** Phần cá nhân nộp riêng trong `REPORT_CANHAN_TV1.md` / `REPORT_CANHAN_TV2.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách trả hàng/hoàn tiền, bảo hành và quy định buyer–seller trên **Shopee Việt Nam** (biến thể K4-L3B).

**Tại sao nhóm chọn chủ đề này?**
> Lớp L3B bắt buộc corpus thương mại điện tử. Shopee có Help Center / Shopee Uni công khai với số liệu cụ thể (15 ngày, 24 giờ, 2 ngày khiếu nại) — phù hợp viết gold answer có thể kiểm chứng và thử `metadata_filter` theo `audience`.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Chính sách trả hàng và hoàn tiền | https://help.shopee.vn/portal/4/article/77251 | 2026-09-20 / 2026-03-11 | ~26k | audience=buyer, category=returns-policy |
| 2 | Quy định chung TH/HT | https://help.shopee.vn/portal/4/article/79452 | 2026-09-20 / not-stated | ~2.7k | audience=buyer, category=returns-policy |
| 3 | Shopee Đảm Bảo là gì | https://help.shopee.vn/portal/4/article/79314 | 2026-09-20 / not-stated | ~2.0k | audience=buyer, category=returns-policy |
| 4 | Chính sách bảo hành (trích quy chế) | https://help.shopee.vn/portal/4/article/77245 | 2026-09-20 / not-stated | ~2.5k | audience=both, category=warranty |
| 5 | FAQ TH/HT cho Người bán | https://banhang.shopee.vn/edu/article/10626 | 2026-09-20 / 2025-11-11 | ~5.5k | audience=seller, category=seller-ops |
| 6 | Tổng quan trang quản lý TH/HT/Hủy | https://banhang.shopee.vn/edu/article/21021 | 2026-09-20 / not-stated | ~2.2k | audience=seller, category=seller-ops |
| 7 | Quy định đăng bán sản phẩm | https://help.shopee.vn/portal/4/article/77246 | 2026-09-20 / not-stated | ~21k | audience=seller, category=seller-ops |

**Bản đầy đủ lưu kèm (không đưa vào bench vì quá dài, gây nhiễu):** `shopee-quy-che-bao-hanh.md`, `shopee-terms-of-service.md` — vẫn có trong `data/ecommerce/` + `sources.csv`.

**Cách thu thập:** `scripts/fetch_public_pages.py` với `data/urls.csv`. Các trang SPA (79452, 21021, 10626) trả HTML rỗng → làm sạch thủ công từ nội dung công khai cùng URL (ghi trong frontmatter).

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu chỉ chứa nguồn công khai; không có dữ liệu cá nhân/đăng nhập.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` trong metadata; `sources.csv` khớp 1-1.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| audience | str | buyer / seller / both | Lọc trước khi search — tránh lẫn đáp án buyer vs seller |
| category | str | returns-policy, warranty, seller-ops | Thu hẹp miền chính sách |
| language | str | vi | Dự phòng corpus đa ngữ |
| source_url | str | URL Help/Uni | Truy vết nguồn cho gold answer |
| retrieved_at | date | 2026-09-20 | Kiểm tra độ mới |
| document_version | str | 2026-03-11 / not-stated | Phiên bản hiệu lực nếu nguồn nêu |
| doc_id | str | shopee-seller-return-faq | Khóa ổn định cho delete / đối chiếu |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare(..., chunk_size=400)` trên body (không YAML):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| shopee-dam-bao | fixed_size | 4 | 366 | Trung bình — cắt giữa câu |
| shopee-dam-bao | by_sentences | 5 | 266 | Tốt hơn với đoạn ngắn |
| shopee-dam-bao | recursive | 4 | 335 | Ổn |
| shopee-dang-ban-san-pham | fixed_size | 60 | 398 | Nhiều chunk |
| shopee-dang-ban-san-pham | by_sentences | 78 | 273 | Mảnh hơn |
| shopee-dang-ban-san-pham | recursive | 68 | 315 | Cân bằng |
| shopee-return-refund-general | fixed_size | 6 | 388 | OK |
| shopee-return-refund-general | by_sentences | 6 | 353 | OK |
| shopee-return-refund-general | recursive | 7 | 302 | OK |

### Chiến lược của từng thành viên

**Thành viên 1 — [Họ tên TV1]**
- **Loại chiến lược:** Custom — `HeadingSectionChunker`
- **Mô tả & lý do chọn cho chủ đề này:** Chính sách Shopee được biên soạn theo mục (`##`, `3.2.`, …). Chia theo heading giữ nguyên đơn vị ngữ nghĩa; section dài thì cắt recursive và **prefix lại tiêu đề** vào mảnh con.
- **Code snippet:** xem `src/heading_chunker.py`

```python
class HeadingSectionChunker:
    def chunk(self, text: str) -> list[str]:
        # split on # headings / numbered sections, then size-limit with RecursiveChunker
        ...
```

**Thành viên 2 — [Họ tên TV2]**
- **Loại chiến lược:** RecursiveChunker tinh chỉnh (`chunk_size=400`, separators mặc định)
- **Mô tả & lý do chọn:** Baseline recursive ổn trên văn bản dài; giảm `chunk_size` để tăng mật độ thông tin trong top-k so với fixed-size mặc định 500.
- **Code snippet:** `RecursiveChunker(chunk_size=400)` trong `bench.py --strategy recursive`

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược | Điểm truy xuất (/10 ước lượng) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| TV1 | Heading | ~7/10 (Q1,Q3,Q4,Q5 tốt; Q2 yếu) | Section mạch lạc; filter seller rõ | Tài liệu ít heading (Đảm Bảo) bị kém hạng |
| TV2 | Recursive-400 | ~6/10 (Q1,Q3,Q5 tốt; Q2/Q4 yếu) | Top-1 Q1 sát số liệu 15 ngày | Dễ cắt cụt câu then chốt bảo hành |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Heading phù hợp hơn với văn bản điều khoản có mục rõ. Recursive vẫn hữu ích khi tài liệu ít heading. Cả hai đều cần corpus “gọn” — dump quy chế/điều khoản đầy đủ (~100k ký tự) làm nhiễu cosine nên nhóm loại khỏi tập bench, giữ bản trích bảo hành.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

Embedding: `paraphrase-multilingual-MiniLM-L12-v2`. Chi tiết: `ket_qua_benchmark.txt`.

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Người mua có bao nhiêu ngày để gửi yêu cầu trả hàng hoàn tiền sau khi giao thành công? | 15 ngày kể từ giao thành công; thực phẩm tươi/đông lạnh: 24 giờ. | `shopee-return-refund-policy` §3.2; `shopee-return-refund-general` §1.2 |
| 2 | Shopee Đảm Bảo cho phép trả hàng hoàn tiền trong bao nhiêu ngày và xử lý khi chưa nhận được hàng? | Đảm Bảo: TH/HT trong 15 ngày; chưa nhận hàng → yêu cầu lý do “Chưa nhận được hàng”, phản hồi 3–5 ngày làm việc. | `shopee-dam-bao` |
| 3 | Trong bao lâu cần phản hồi hoặc khiếu nại quyết định hoàn tiền của Shopee? **(cần `metadata_filter={"audience":"seller"}`)** | Người bán khiếu nại/phản hồi trong **2 ngày**. | `shopee-seller-return-faq` (và điều khoản seller trong policy) |
| 4 | Shopee có phải là bên thực hiện nghĩa vụ bảo hành sản phẩm trên sàn không? | Không — trừ sản phẩm do chính Shopee đăng bán; Người Bán/NSX chịu trách nhiệm. | `shopee-warranty-policy` |
| 5 | Người bán vào đâu trên Kênh Người Bán để quản lý đơn Trả hàng/Hoàn tiền/Hủy? | Quản lý đơn hàng → mục Trả hàng/Hoàn tiền/Hủy. | `shopee-seller-return-overview` §1 |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất | Chunk liên quan top-3? | Ghi chú |
|---|---------|---------------------|------------------------|---------|
| 1 | Thời hạn 15 ngày | Cả hai (Recursive top-1 sát hơn) | Có | Heading cũng có marker ở #3 |
| 2 | Shopee Đảm Bảo | Recursive (doc đúng ở #2) | Một phần | Heading lệch sang general returns — **failure case** |
| 3 | 2 ngày phản hồi (seller) | Heading + filter | Có (toàn seller) | Không filter: top-1 thành buyer/general |
| 4 | Bảo hành | Heading (warranty #2) | Có (Heading) | Recursive miss — **failure case** |
| 5 | Menu Kênh Người Bán | Cả hai | Có | Heading & Recursive đều top-1 đúng |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có — câu #3. Có `audience=seller`: top-3 toàn FAQ người bán (2 ngày khiếu nại). Không filter: top-1 là trang buyer (phản hồi 3–5 ngày làm việc) hoặc đoạn “02 ngày lịch” trong policy buyer-facing — dễ trả lời sai đối tượng. A/B ghi trong `ket_qua_benchmark.txt`.

### Failure analysis (nhóm)

1. **Q2 + Heading:** query nhắc “trả hàng hoàn tiền / ngày” nên chunk general returns thắng chunk Đảm Bảo (ít heading, nội dung ngắn).
2. **Q4 + Recursive:** câu key “không phải bên thực hiện nghĩa vụ bảo hành” bị tách / xếp dưới chunk returns có từ “Shopee đảm bảo quyền lợi”.
3. **Bài học:** corpus quá dài + từ vựng chồng chéo buyer/seller → bắt buộc filter + ưu tiên file trích gọn.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1) A/B metadata filter trên câu #3 (seller vs không filter). 2) Heading vs Recursive trên cùng 5 query. 3) Vì sao loại dump quy chế/ToS khỏi bench.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng corpus và cùng query, Heading thắng ở tài liệu có mục rõ (bảo hành, FAQ); Recursive thắng khi cần bắt cụm số liệu giữa đoạn. Filter `audience` không phải “tối ưu điểm” mà là điều kiện để câu #3 đúng nghĩa.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Tách sớm mọi trang “both” thành buyer/seller; chuẩn hóa heading trước khi ingest; không nạp nguyên văn bản pháp lý >50k ký tự vào một store duy nhất.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 9 / 10 |
| Thiết kế chiến lược (Strategy Design) | 13 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 7 / 10 |
| Thuyết trình (Demo) | 4 / 5 (chuẩn bị nội dung; chưa trình bày) |
| **Tổng phần nhóm** | **33 / 40** |
