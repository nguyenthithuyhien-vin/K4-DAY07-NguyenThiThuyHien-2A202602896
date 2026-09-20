# Chia việc — Thành viên 1 (TV1)

**Họ tên:** Tạ Đăng Dương
**Nhóm:** G69 (K4-L3B)
**Vai trò tắt:** Dẫn Phase 1 chunking + chiến lược Heading/Section ở Phase 2

> File cặp: `CHIA_VIEC_TV2.md` (Nguyễn Thị Thuý Hiền).

---

## Phase 1 — Code cá nhân (cùng repo `src/`)

| Việc | TV1 làm | Trạng thái |
|------|---------|------------|
| Dẫn implement `compute_similarity`, `SentenceChunker`, `RecursiveChunker`, `ChunkingStrategyComparator` | **Chính** | [x] Xong |
| Review `EmbeddingStore` + `KnowledgeBaseAgent` | Review + pytest | [x] Xong |
| Hiểu toàn bộ `src/` để viết REPORT_CANHAN §2 | Bắt buộc | [x] Đã viết |

**Checkpoint:** `pytest tests/ -v` → **42 passed**.

---

## Phase 2 — Nhóm

| Việc | Chi tiết | Checklist |
|------|----------|-----------|
| Thu thập corpus | Buyer-heavy + urls.csv | [x] |
| Chiến lược riêng | **HeadingSectionChunker** | [x] |
| Benchmark queries | 3/5 câu (gồm #3 cần filter) | [x] |
| Chạy đánh giá | `bench.py --strategy heading --ab-filter` | [x] |
| `REPORT_NHOM.md` | §1 + §3 | [x] |
| `REPORT_CANHAN_TV1.md` | §4–§5 | [x] |

---

## Sản phẩm cá nhân nộp

- [x] Code chung `src/` pass pytest
- [x] `HeadingSectionChunker` + đóng góp `bench.py`
- [x] `report/REPORT_CANHAN_TV1.md`
- [x] Đóng góp `REPORT_NHOM.md` §1 và §3
