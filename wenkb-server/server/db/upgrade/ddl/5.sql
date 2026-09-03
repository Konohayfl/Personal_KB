ALTER TABLE "t_knb_dataset_index_error" RENAME TO "t_knb_dataset_index_error_old";

CREATE TABLE IF NOT EXISTS "t_knb_dataset_index_error" (
  "error_id" text(32) NOT NULL,
  "dtset_id" text(32),
  "idx_typ" text(10),
  "err_inf" text,
  "crt_tm" text,
  PRIMARY KEY ("error_id")
);

INSERT INTO "t_knb_dataset_index_error" (
  "error_id", "dtset_id", "idx_typ", "err_inf", "crt_tm"
)
SELECT
  lower(hex(randomblob(16))),
  "dtset_id",
  "idx_typ",
  "err_inf",
  coalesce("crt_tm", strftime('%Y-%m-%d %H:%M:%S', 'now'))
FROM "t_knb_dataset_index_error_old";

DROP TABLE "t_knb_dataset_index_error_old";

CREATE INDEX IF NOT EXISTS "idx_knb_dataset_index_error_query"
ON "t_knb_dataset_index_error" ("dtset_id", "idx_typ", "crt_tm");
