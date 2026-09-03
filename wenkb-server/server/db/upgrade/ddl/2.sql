CREATE TABLE IF NOT EXISTS "t_knb_dataset_index_error" (
  "error_id" text(32) NOT NULL,
  "dtset_id" text(32),
  "idx_typ" text(10),
  "err_inf" text,
  "crt_tm" text,
  PRIMARY KEY ("error_id")
);

CREATE INDEX IF NOT EXISTS "idx_knb_dataset_index_error_query"
ON "t_knb_dataset_index_error" ("dtset_id", "idx_typ", "crt_tm");
