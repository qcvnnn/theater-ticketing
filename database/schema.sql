-- Portfolio schema. Install only into a NEW empty database.
CREATE TABLE "Clients" (
 "ID_Client" integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 "Login" text NOT NULL UNIQUE CHECK ("Login" = lower(btrim("Login")) AND length("Login") BETWEEN 3 AND 64),
 "Password" text NOT NULL CHECK ("Password" LIKE 'pbkdf2_sha256$%'),
 "First_name" text NOT NULL DEFAULT '', "Second_name" text NOT NULL DEFAULT '',
 "Patronymic" text, "Phone_number" text UNIQUE, "Email" text UNIQUE,
 "is_admin" boolean NOT NULL DEFAULT false
);
CREATE TABLE "Theaters" (
 "ID_Theater" integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 "Title" text NOT NULL UNIQUE, "Contact_phone" text NOT NULL,
 "Address" text NOT NULL, "Number_of_halls" integer NOT NULL CHECK ("Number_of_halls">0)
);
CREATE TABLE "Productions" (
 "ID_Production" integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 "Title" text NOT NULL, "Annotation" text, "Author" text,
 "Duration" integer CHECK ("Duration">0), "Actors" text,
 "ID_Theater" integer NOT NULL REFERENCES "Theaters" ON DELETE RESTRICT,
 "Genre" text NOT NULL, "Image" text NOT NULL DEFAULT '',
 UNIQUE ("Title","ID_Theater")
);
CREATE TABLE "Troupe" (
 "ID_Actor" integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 "First_name" text NOT NULL, "Second_name" text NOT NULL, "Patronymic" text,
 "Education" text, "Experience" integer CHECK ("Experience">=0)
);
CREATE TABLE "Actor_Theater" (
 "ID_Actor" integer REFERENCES "Troupe" ON DELETE CASCADE,
 "ID_Theater" integer REFERENCES "Theaters" ON DELETE CASCADE,
 start_date date, PRIMARY KEY ("ID_Actor","ID_Theater")
);
CREATE TABLE "Show_Details" (
 "ID_ShowDetails" integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 "Show_Date" date NOT NULL, "Start_time" time NOT NULL,
 "Hall_number" integer NOT NULL CHECK ("Hall_number">0),
 "ID_Production" integer NOT NULL REFERENCES "Productions" ON DELETE RESTRICT,
 UNIQUE ("ID_Production","Show_Date","Start_time")
);
CREATE TABLE "ShowSeats" (
 "ID_ShowSeat" integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 "ShowDetails_ID" integer NOT NULL REFERENCES "Show_Details" ON DELETE RESTRICT,
 "SeatType" text NOT NULL CHECK ("SeatType" IN ('партер','бельэтаж','балкон')),
 "TotalSeats" integer NOT NULL CHECK ("TotalSeats">=0),
 "SoldSeats" integer NOT NULL DEFAULT 0 CHECK ("SoldSeats">=0 AND "SoldSeats"<="TotalSeats"),
 UNIQUE ("ShowDetails_ID","SeatType")
);
CREATE TABLE "Tickets" (
 "ID_Ticket" integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 "ID_Client" integer NOT NULL REFERENCES "Clients" ON DELETE RESTRICT,
 "ID_ShowDetails" integer NOT NULL REFERENCES "Show_Details" ON DELETE RESTRICT,
 "SeatType" text NOT NULL,
 "Status" text NOT NULL DEFAULT 'active' CHECK ("Status" IN ('active','cancelled')),
 "CreatedAt" timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
 "CancelledAt" timestamptz,
 FOREIGN KEY ("ID_ShowDetails","SeatType") REFERENCES "ShowSeats" ("ShowDetails_ID","SeatType") ON DELETE RESTRICT,
 CHECK (("Status"='active' AND "CancelledAt" IS NULL) OR ("Status"='cancelled' AND "CancelledAt" IS NOT NULL))
);
CREATE INDEX tickets_client_idx ON "Tickets" ("ID_Client");
CREATE INDEX tickets_show_idx ON "Tickets" ("ID_ShowDetails","SeatType","Status");
CREATE TABLE "Reviews" (
 "ID_Review" integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 "Review_content" text NOT NULL CHECK (length(btrim("Review_content")) BETWEEN 1 AND 4000),
 "Assessment" integer NOT NULL CHECK ("Assessment" BETWEEN 1 AND 10),
 "Date_of_writing" date NOT NULL DEFAULT CURRENT_DATE,
 "ID_Productions" integer NOT NULL REFERENCES "Productions" ON DELETE RESTRICT,
 "ID_Client" integer NOT NULL REFERENCES "Clients" ON DELETE RESTRICT,
 UNIQUE ("ID_Productions","ID_Client")
);

-- One atomic conditional UPDATE serializes competing requests for the last seat.
-- The trigger owns the counter: Python must never increment/decrement it itself.
CREATE FUNCTION ticket_capacity() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF TG_OP='INSERT' THEN
  IF NEW."Status" <> 'active' THEN RAISE EXCEPTION 'Новый билет должен быть активным'; END IF;
  IF NOT EXISTS (SELECT 1 FROM "Show_Details" WHERE "ID_ShowDetails"=NEW."ID_ShowDetails"
    AND "Show_Date"+"Start_time">LOCALTIMESTAMP) THEN
   RAISE EXCEPTION 'Показ уже начался или не существует';
  END IF;
  UPDATE "ShowSeats" SET "SoldSeats"="SoldSeats"+1
   WHERE "ShowDetails_ID"=NEW."ID_ShowDetails" AND "SeatType"=NEW."SeatType"
     AND "SoldSeats"<"TotalSeats";
  IF NOT FOUND THEN RAISE EXCEPTION 'Свободных мест нет'; END IF;
  RETURN NEW;
 ELSIF TG_OP='UPDATE' THEN
  IF NEW."ID_Ticket" IS DISTINCT FROM OLD."ID_Ticket" OR
     NEW."ID_Client" IS DISTINCT FROM OLD."ID_Client" OR
     NEW."ID_ShowDetails" IS DISTINCT FROM OLD."ID_ShowDetails" OR
     NEW."SeatType" IS DISTINCT FROM OLD."SeatType" OR
     NEW."CreatedAt" IS DISTINCT FROM OLD."CreatedAt" OR
     OLD."Status" <> 'active' OR NEW."Status" <> 'cancelled' THEN
    RAISE EXCEPTION 'Допустим только возврат активного билета';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM "Show_Details" WHERE "ID_ShowDetails"=OLD."ID_ShowDetails"
    AND "Show_Date"+"Start_time">LOCALTIMESTAMP) THEN RAISE EXCEPTION 'Показ уже начался'; END IF;
  NEW."CancelledAt"=CURRENT_TIMESTAMP;
  UPDATE "ShowSeats" SET "SoldSeats"="SoldSeats"-1
   WHERE "ShowDetails_ID"=OLD."ID_ShowDetails" AND "SeatType"=OLD."SeatType";
  RETURN NEW;
 ELSE
  RAISE EXCEPTION 'Билеты сохраняются в истории; используйте возврат';
 END IF;
END $$;
CREATE TRIGGER ticket_capacity_guard BEFORE INSERT OR UPDATE OR DELETE ON "Tickets"
 FOR EACH ROW EXECUTE FUNCTION ticket_capacity();
