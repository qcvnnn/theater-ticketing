--
-- PostgreSQL database dump
--

\restrict tb4zaFysosUanLQkzen5bmOV4teeAli99gAIkv0GG7IHX3TombLKgRatYr7fGhm

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: Actor_Theater; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."Actor_Theater" (
    "ID_Actor" integer NOT NULL,
    "ID_Theater" integer NOT NULL,
    start_date date
);


--
-- Name: Clients; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."Clients" (
    "ID_Client" integer CONSTRAINT clients_id_client_not_null NOT NULL,
    "First_name" text CONSTRAINT clients_first_name_not_null NOT NULL,
    "Second_name" text CONSTRAINT clients_second_name_not_null NOT NULL,
    "Patronymic" text,
    "Phone_number" text CONSTRAINT clients_phone_number_not_null NOT NULL,
    "Email" text CONSTRAINT clients_email_not_null NOT NULL,
    is_admin boolean DEFAULT false,
    "Login" text DEFAULT 'test'::text NOT NULL,
    "Password" text NOT NULL
);


--
-- Name: ProductionSeats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."ProductionSeats" (
    "ID_ProductionSeat" integer NOT NULL,
    "Production_ID" integer,
    "SeatType" character varying(50),
    "TotalSeats" integer
);


--
-- Name: ProductionSeats_ID_ProductionSeat_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."ProductionSeats_ID_ProductionSeat_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ProductionSeats_ID_ProductionSeat_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."ProductionSeats_ID_ProductionSeat_seq" OWNED BY public."ProductionSeats"."ID_ProductionSeat";


--
-- Name: Productions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."Productions" (
    "ID_Production" integer CONSTRAINT productions_id_production_not_null NOT NULL,
    "Title" text CONSTRAINT productions_title_not_null NOT NULL,
    "Annotation" text,
    "Author" text,
    "Duration" integer,
    "Actors" text,
    "ID_Theater" integer,
    "Genre" text CONSTRAINT "Productions_genre_not_null" NOT NULL,
    "Image" text,
    CONSTRAINT productions_duration_check CHECK (("Duration" > 0))
);


--
-- Name: Reviews; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."Reviews" (
    "ID_Review" integer CONSTRAINT "Reviews_id_review_not_null" NOT NULL,
    "Review_content" text,
    "Assessment" integer,
    "Date_of_writing" date DEFAULT CURRENT_DATE,
    "ID_Productions" integer,
    "ID_Client" integer,
    CONSTRAINT check_assessment CHECK ((("Assessment" >= 1) AND ("Assessment" <= 10)))
);


--
-- Name: Reviews_id_review_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."Reviews_id_review_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: Reviews_id_review_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."Reviews_id_review_seq" OWNED BY public."Reviews"."ID_Review";


--
-- Name: SeatTypes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."SeatTypes" (
    "ID_SeatType" integer NOT NULL,
    "Production_ID" integer,
    "SeatType" character varying(50) NOT NULL,
    "TotalSeats" integer NOT NULL,
    "ShowDetails_ID" integer,
    CONSTRAINT "SeatTypes_TotalSeats_check" CHECK (("TotalSeats" > 0))
);


--
-- Name: SeatTypes_ID_SeatType_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."SeatTypes_ID_SeatType_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: SeatTypes_ID_SeatType_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."SeatTypes_ID_SeatType_seq" OWNED BY public."SeatTypes"."ID_SeatType";


--
-- Name: ShowSeats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."ShowSeats" (
    "ID_ShowSeat" integer NOT NULL,
    "ShowDetails_ID" integer,
    "SeatType" character varying(50),
    "TotalSeats" integer,
    "SoldSeats" integer DEFAULT 0
);


--
-- Name: ShowSeats_ID_ShowSeat_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."ShowSeats_ID_ShowSeat_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ShowSeats_ID_ShowSeat_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."ShowSeats_ID_ShowSeat_seq" OWNED BY public."ShowSeats"."ID_ShowSeat";


--
-- Name: Show_Details; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."Show_Details" (
    "ID_ShowDetails" integer NOT NULL,
    "Show_Date" date NOT NULL,
    "Start_time" time(0) without time zone NOT NULL,
    "Hall_number" integer,
    "ID_Production" integer,
    CONSTRAINT "Show_Details_Hall_number_check" CHECK (("Hall_number" > 0))
);


--
-- Name: Show_Details_ID_ShowDetails_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."Show_Details_ID_ShowDetails_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: Show_Details_ID_ShowDetails_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."Show_Details_ID_ShowDetails_seq" OWNED BY public."Show_Details"."ID_ShowDetails";


--
-- Name: Theaters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."Theaters" (
    "ID_Theater" integer NOT NULL,
    "Title" text NOT NULL,
    "Contact_phone" text NOT NULL,
    "Address" text NOT NULL,
    "Number_of_halls" integer NOT NULL
);


--
-- Name: Theaters_ID_Theater_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."Theaters_ID_Theater_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: Theaters_ID_Theater_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."Theaters_ID_Theater_seq" OWNED BY public."Theaters"."ID_Theater";


--
-- Name: Tickets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."Tickets" (
    "ID_Ticket" integer NOT NULL,
    "Location" text,
    "Row_number" integer,
    "Seat_number" integer,
    "ID_Client" integer,
    "ID_ShowDetails" integer,
    "SeatType" character varying(50)
);


--
-- Name: Tickets_ID_Ticket_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."Tickets_ID_Ticket_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: Tickets_ID_Ticket_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."Tickets_ID_Ticket_seq" OWNED BY public."Tickets"."ID_Ticket";


--
-- Name: Troupe; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."Troupe" (
    "ID_Actor" integer NOT NULL,
    "First_name" text NOT NULL,
    "Second_name" text NOT NULL,
    "Patronymic" text NOT NULL,
    "Education" text NOT NULL,
    "Experience" integer NOT NULL
);


--
-- Name: Troupe_ID_Actor_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."Troupe_ID_Actor_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: Troupe_ID_Actor_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."Troupe_ID_Actor_seq" OWNED BY public."Troupe"."ID_Actor";


--
-- Name: clients_id_client_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.clients_id_client_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: clients_id_client_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.clients_id_client_seq OWNED BY public."Clients"."ID_Client";


--
-- Name: productions_id_production_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.productions_id_production_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: productions_id_production_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.productions_id_production_seq OWNED BY public."Productions"."ID_Production";


--
-- Name: Clients ID_Client; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Clients" ALTER COLUMN "ID_Client" SET DEFAULT nextval('public.clients_id_client_seq'::regclass);


--
-- Name: ProductionSeats ID_ProductionSeat; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."ProductionSeats" ALTER COLUMN "ID_ProductionSeat" SET DEFAULT nextval('public."ProductionSeats_ID_ProductionSeat_seq"'::regclass);


--
-- Name: Productions ID_Production; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Productions" ALTER COLUMN "ID_Production" SET DEFAULT nextval('public.productions_id_production_seq'::regclass);


--
-- Name: Reviews ID_Review; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Reviews" ALTER COLUMN "ID_Review" SET DEFAULT nextval('public."Reviews_id_review_seq"'::regclass);


--
-- Name: SeatTypes ID_SeatType; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."SeatTypes" ALTER COLUMN "ID_SeatType" SET DEFAULT nextval('public."SeatTypes_ID_SeatType_seq"'::regclass);


--
-- Name: ShowSeats ID_ShowSeat; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."ShowSeats" ALTER COLUMN "ID_ShowSeat" SET DEFAULT nextval('public."ShowSeats_ID_ShowSeat_seq"'::regclass);


--
-- Name: Show_Details ID_ShowDetails; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Show_Details" ALTER COLUMN "ID_ShowDetails" SET DEFAULT nextval('public."Show_Details_ID_ShowDetails_seq"'::regclass);


--
-- Name: Theaters ID_Theater; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Theaters" ALTER COLUMN "ID_Theater" SET DEFAULT nextval('public."Theaters_ID_Theater_seq"'::regclass);


--
-- Name: Tickets ID_Ticket; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Tickets" ALTER COLUMN "ID_Ticket" SET DEFAULT nextval('public."Tickets_ID_Ticket_seq"'::regclass);


--
-- Name: Troupe ID_Actor; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Troupe" ALTER COLUMN "ID_Actor" SET DEFAULT nextval('public."Troupe_ID_Actor_seq"'::regclass);


--
-- Name: Actor_Theater Actor_Theater_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Actor_Theater"
    ADD CONSTRAINT "Actor_Theater_pkey" PRIMARY KEY ("ID_Actor", "ID_Theater");


--
-- Name: ProductionSeats ProductionSeats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."ProductionSeats"
    ADD CONSTRAINT "ProductionSeats_pkey" PRIMARY KEY ("ID_ProductionSeat");


--
-- Name: Reviews Reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Reviews"
    ADD CONSTRAINT "Reviews_pkey" PRIMARY KEY ("ID_Review");


--
-- Name: SeatTypes SeatTypes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."SeatTypes"
    ADD CONSTRAINT "SeatTypes_pkey" PRIMARY KEY ("ID_SeatType");


--
-- Name: ShowSeats ShowSeats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."ShowSeats"
    ADD CONSTRAINT "ShowSeats_pkey" PRIMARY KEY ("ID_ShowSeat");


--
-- Name: Show_Details Show_Details_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Show_Details"
    ADD CONSTRAINT "Show_Details_pkey" PRIMARY KEY ("ID_ShowDetails");


--
-- Name: Theaters Theaters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Theaters"
    ADD CONSTRAINT "Theaters_pkey" PRIMARY KEY ("ID_Theater");


--
-- Name: Tickets Tickets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Tickets"
    ADD CONSTRAINT "Tickets_pkey" PRIMARY KEY ("ID_Ticket");


--
-- Name: Troupe Troupe_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Troupe"
    ADD CONSTRAINT "Troupe_pkey" PRIMARY KEY ("ID_Actor");


--
-- Name: Clients clients_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Clients"
    ADD CONSTRAINT clients_email_key UNIQUE ("Email");


--
-- Name: Clients clients_phone_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Clients"
    ADD CONSTRAINT clients_phone_number_key UNIQUE ("Phone_number");


--
-- Name: Clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Clients"
    ADD CONSTRAINT clients_pkey PRIMARY KEY ("ID_Client");


--
-- Name: Productions productions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Productions"
    ADD CONSTRAINT productions_pkey PRIMARY KEY ("ID_Production");


--
-- Name: Productions unique_title_per_theater; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Productions"
    ADD CONSTRAINT unique_title_per_theater UNIQUE ("Title", "ID_Theater");


--
-- Name: Actor_Theater Actor_Theater_ID_Actor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Actor_Theater"
    ADD CONSTRAINT "Actor_Theater_ID_Actor_fkey" FOREIGN KEY ("ID_Actor") REFERENCES public."Troupe"("ID_Actor") ON DELETE CASCADE;


--
-- Name: Actor_Theater Actor_Theater_ID_Theater_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Actor_Theater"
    ADD CONSTRAINT "Actor_Theater_ID_Theater_fkey" FOREIGN KEY ("ID_Theater") REFERENCES public."Theaters"("ID_Theater") ON DELETE CASCADE;


--
-- Name: ProductionSeats ProductionSeats_Production_ID_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."ProductionSeats"
    ADD CONSTRAINT "ProductionSeats_Production_ID_fkey" FOREIGN KEY ("Production_ID") REFERENCES public."Productions"("ID_Production") ON DELETE CASCADE;


--
-- Name: Reviews Reviews_id_client_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Reviews"
    ADD CONSTRAINT "Reviews_id_client_fkey" FOREIGN KEY ("ID_Client") REFERENCES public."Clients"("ID_Client") ON DELETE CASCADE;


--
-- Name: Reviews Reviews_id_productions_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Reviews"
    ADD CONSTRAINT "Reviews_id_productions_fkey" FOREIGN KEY ("ID_Productions") REFERENCES public."Productions"("ID_Production") ON DELETE CASCADE;


--
-- Name: SeatTypes SeatTypes_Production_ID_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."SeatTypes"
    ADD CONSTRAINT "SeatTypes_Production_ID_fkey" FOREIGN KEY ("Production_ID") REFERENCES public."Productions"("ID_Production") ON DELETE CASCADE;


--
-- Name: SeatTypes SeatTypes_ShowDetails_ID_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."SeatTypes"
    ADD CONSTRAINT "SeatTypes_ShowDetails_ID_fkey" FOREIGN KEY ("ShowDetails_ID") REFERENCES public."Show_Details"("ID_ShowDetails");


--
-- Name: ShowSeats ShowSeats_ShowDetails_ID_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."ShowSeats"
    ADD CONSTRAINT "ShowSeats_ShowDetails_ID_fkey" FOREIGN KEY ("ShowDetails_ID") REFERENCES public."Show_Details"("ID_ShowDetails");


--
-- Name: Show_Details Show_Details_ID_Production_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Show_Details"
    ADD CONSTRAINT "Show_Details_ID_Production_fkey" FOREIGN KEY ("ID_Production") REFERENCES public."Productions"("ID_Production") ON DELETE CASCADE;


--
-- Name: Tickets Tickets_ID_Client_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Tickets"
    ADD CONSTRAINT "Tickets_ID_Client_fkey" FOREIGN KEY ("ID_Client") REFERENCES public."Clients"("ID_Client") ON DELETE CASCADE;


--
-- Name: Tickets Tickets_ID_ShowDetails_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Tickets"
    ADD CONSTRAINT "Tickets_ID_ShowDetails_fkey" FOREIGN KEY ("ID_ShowDetails") REFERENCES public."Show_Details"("ID_ShowDetails") ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict tb4zaFysosUanLQkzen5bmOV4teeAli99gAIkv0GG7IHX3TombLKgRatYr7fGhm

