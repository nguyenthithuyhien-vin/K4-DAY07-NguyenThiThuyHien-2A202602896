# Chia việc — Thành viên 2 (TV2)

**Họ tên:** [Điền họ tên TV2]
**Nhóm:** G69 (K4-L3B)
**Vai trò tắt:** Dẫn Phase 1 store/agent + chiến lược Recursive tinh chỉnh ở Phase 2

> Đổi `[Điền họ tên TV2]` thành tên thật trước khi nộp. File cặp: `CHIA_VIEC_TV1.md`.

---

## Phase 1 — Code cá nhân (cùng repo `src/`)

| Việc | TV2 làm | Trạng thái |
|------|---------|------------|
| Dẫn implement `EmbeddingStore` + `KnowledgeBaseAgent` | **Chính** | [x] Xong |
| Review chunking + similarity + comparator | Review + pytest | [x] Xong |
| Hiểu toàn bộ `src/` để viết REPORT_CANHAN §2 | Bắt buộc | [x] Đã viết |

**Checkpoint:** `pytest tests/ -v` → **42 passed**.

---

## Phase 2 — Nhóm

| Việc | Chi tiết | Checklist |
|------|----------|-----------|
| Thu thập corpus | Seller-heavy + sources.csv / metadata | [x] |
| Chiến lược riêng | **RecursiveChunker(chunk_size=400)** | [x] |
| Benchmark queries | 2/5 câu (#4, #5) + verify gold | [x] |
| Chạy đánh giá | `bench.py --strategy recursive --ab-filter` | [x] |
| `REPORT_NHOM.md` | §2 + §4 | [x] |
| `REPORT_CANHAN_TV2.md` | §4–§5 | [x] |

---

## Sản phẩm cá nhân nộp

- [x] Code chung `src/` pass pytest
- [x] `report/REPORT_CANHAN_TV2.md`
- [x] Đóng góp `REPORT_NHOM.md` §2 và §4
