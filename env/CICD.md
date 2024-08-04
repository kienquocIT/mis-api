# Mô tả các biến môi trường cho CICD của repo này

---

1. Sử dụng cấu hình Database mặc định để sử dụng tập tin database là `db.sqlite3`
2. Migrate và init dữ liệu cần thiết
3. Copy (override nếu tồn tại) từ `db.sqlite3` sang `.gitlab-ci-db.sqlite3`
4. Cấu hình variables của CICD trên repo sử dụng tập database backup `CICD_ENABLED__USE_DB_MOCKUP=1`
5. Cấu hình sẽ luôn đảm bảo `CICD_ENABLED__USE_DB_MOCKUP=1` và tồn tại tệp `.gitlab-ci-db.sqlite3`

---

- CICD_ENABLED__USE_DB_MOCKUP ( 0 hoặc 1) : Giúp chuyển cấu hình Database mặc định sang `.gitlab-ci-db.sqlite3`
- 