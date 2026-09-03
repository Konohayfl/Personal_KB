CREATE TABLE IF NOT EXISTS "t_knb_chat_quote" (
  "quote_id" text(32) NOT NULL,
  "mesg_id" text(32) NOT NULL,
  "repos_id" text(32) NOT NULL,
  "dtset_id" text(32),
  "chk_id" text(32),
  "src_obj_typ" text(20) NOT NULL,
  "src_obj_id" text(32),
  "dtset_nm" text(200),
  "file_nm" text(200),
  "file_typ" text(20),
  "score" decimal(8,6),
  "content" text NOT NULL,
  "quote_order" integer NOT NULL,
  "crt_tm" text NOT NULL,
  PRIMARY KEY ("quote_id")
);

CREATE INDEX IF NOT EXISTS "idx_knb_chat_quote_message_order"
ON "t_knb_chat_quote" ("mesg_id", "quote_order");

CREATE INDEX IF NOT EXISTS "idx_knb_chat_quote_dataset"
ON "t_knb_chat_quote" ("dtset_id");
