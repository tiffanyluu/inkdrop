\restrict dbmate

-- Dumped from database version 18.6 (Debian 18.6-1.pgdg12+2)
-- Dumped by pg_dump version 18.6

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

--
-- Name: sources_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.sources_type_enum AS ENUM (
    'MANGADEX',
    'ATHREA'
);


--
-- Name: title_status_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.title_status_enum AS ENUM (
    'ONGOING',
    'COMPLETED',
    'HIATUS',
    'CANCELED'
);


--
-- Name: set_modified_datetime(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.set_modified_datetime() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
begin
    new.modified_datetime = now();
    return new;
end;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications (
    row_id bigint NOT NULL,
    notification_public_id uuid DEFAULT gen_random_uuid() NOT NULL,
    chapter numeric NOT NULL,
    user_row_id bigint NOT NULL,
    title_row_id bigint NOT NULL,
    create_datetime timestamp with time zone DEFAULT now() NOT NULL,
    seen_datetime timestamp with time zone
);


--
-- Name: notifications_row_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.notifications ALTER COLUMN row_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.notifications_row_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying NOT NULL
);


--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.subscriptions (
    row_id bigint CONSTRAINT subscriptions_id_not_null NOT NULL,
    subscription_public_id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_row_id bigint NOT NULL,
    title_row_id bigint NOT NULL,
    latest_read_chapter numeric,
    read_url text,
    latest_notified_chapter numeric,
    create_datetime timestamp with time zone DEFAULT now() NOT NULL,
    modified_datetime timestamp with time zone
);


--
-- Name: subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.subscriptions ALTER COLUMN row_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.subscriptions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: title_sources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.title_sources (
    row_id bigint CONSTRAINT title_sources_id_not_null NOT NULL,
    source_id character varying(255) NOT NULL,
    title_row_id bigint NOT NULL,
    source_type public.sources_type_enum NOT NULL,
    latest_free_chapter numeric,
    latest_paid_chapter numeric,
    create_datetime timestamp with time zone DEFAULT now() NOT NULL,
    modified_datetime timestamp with time zone,
    last_checked_datetime timestamp with time zone,
    latest_free_chapter_datetime timestamp with time zone
);


--
-- Name: title_sources_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.title_sources ALTER COLUMN row_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.title_sources_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: titles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.titles (
    row_id bigint CONSTRAINT titles_id_not_null NOT NULL,
    title_public_id uuid DEFAULT gen_random_uuid() NOT NULL,
    title_name character varying(255) NOT NULL,
    cover_url text,
    title_status public.title_status_enum NOT NULL,
    create_datetime timestamp with time zone DEFAULT now() NOT NULL,
    modified_datetime timestamp with time zone,
    description text
);


--
-- Name: titles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.titles ALTER COLUMN row_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.titles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: user_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_sessions (
    row_id bigint CONSTRAINT user_sessions_id_not_null NOT NULL,
    token_hash character varying(64) NOT NULL,
    user_row_id bigint NOT NULL,
    create_datetime timestamp with time zone DEFAULT now() NOT NULL,
    expiration_datetime timestamp with time zone NOT NULL
);


--
-- Name: user_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.user_sessions ALTER COLUMN row_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.user_sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    row_id bigint CONSTRAINT users_id_not_null NOT NULL,
    user_public_id uuid DEFAULT gen_random_uuid() NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    create_datetime timestamp with time zone DEFAULT now() NOT NULL,
    modified_datetime timestamp with time zone
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.users ALTER COLUMN row_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: notifications notifications_notification_public_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_notification_public_id_key UNIQUE (notification_public_id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (row_id);


--
-- Name: notifications notifications_user_row_id_title_row_id_chapter_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_row_id_title_row_id_chapter_key UNIQUE (user_row_id, title_row_id, chapter);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (row_id);


--
-- Name: subscriptions subscriptions_subscription_public_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_subscription_public_id_key UNIQUE (subscription_public_id);


--
-- Name: subscriptions subscriptions_user_row_id_title_row_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_row_id_title_row_id_key UNIQUE (user_row_id, title_row_id);


--
-- Name: title_sources title_sources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.title_sources
    ADD CONSTRAINT title_sources_pkey PRIMARY KEY (row_id);


--
-- Name: title_sources title_sources_source_type_source_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.title_sources
    ADD CONSTRAINT title_sources_source_type_source_id_key UNIQUE (source_type, source_id);


--
-- Name: titles titles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.titles
    ADD CONSTRAINT titles_pkey PRIMARY KEY (row_id);


--
-- Name: titles titles_title_public_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.titles
    ADD CONSTRAINT titles_title_public_id_key UNIQUE (title_public_id);


--
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (row_id);


--
-- Name: user_sessions user_sessions_token_hash_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_token_hash_key UNIQUE (token_hash);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (row_id);


--
-- Name: users users_user_public_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_user_public_id_key UNIQUE (user_public_id);


--
-- Name: idx_subscriptions_title; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_subscriptions_title ON public.subscriptions USING btree (title_row_id);


--
-- Name: idx_title_sources_title; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_title_sources_title ON public.title_sources USING btree (title_row_id);


--
-- Name: idx_user_sessions_expiration_datetime; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_sessions_expiration_datetime ON public.user_sessions USING btree (expiration_datetime);


--
-- Name: idx_user_sessions_user_row_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_sessions_user_row_id ON public.user_sessions USING btree (user_row_id);


--
-- Name: idx_users_email_lower; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_users_email_lower ON public.users USING btree (lower((email)::text));


--
-- Name: subscriptions trigger_subscriptions_modified_datetime; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_subscriptions_modified_datetime BEFORE UPDATE ON public.subscriptions FOR EACH ROW EXECUTE FUNCTION public.set_modified_datetime();


--
-- Name: title_sources trigger_title_sources_modified_datetime; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_title_sources_modified_datetime BEFORE UPDATE ON public.title_sources FOR EACH ROW EXECUTE FUNCTION public.set_modified_datetime();


--
-- Name: titles trigger_titles_modified_datetime; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_titles_modified_datetime BEFORE UPDATE ON public.titles FOR EACH ROW EXECUTE FUNCTION public.set_modified_datetime();


--
-- Name: users trigger_users_modified_datetime; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_users_modified_datetime BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.set_modified_datetime();


--
-- Name: notifications notifications_title_row_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_title_row_id_fkey FOREIGN KEY (title_row_id) REFERENCES public.titles(row_id) ON DELETE CASCADE;


--
-- Name: notifications notifications_user_row_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_row_id_fkey FOREIGN KEY (user_row_id) REFERENCES public.users(row_id) ON DELETE CASCADE;


--
-- Name: subscriptions subscriptions_title_row_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_title_row_id_fkey FOREIGN KEY (title_row_id) REFERENCES public.titles(row_id) ON DELETE CASCADE;


--
-- Name: subscriptions subscriptions_user_row_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_row_id_fkey FOREIGN KEY (user_row_id) REFERENCES public.users(row_id) ON DELETE CASCADE;


--
-- Name: title_sources title_sources_title_row_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.title_sources
    ADD CONSTRAINT title_sources_title_row_id_fkey FOREIGN KEY (title_row_id) REFERENCES public.titles(row_id) ON DELETE CASCADE;


--
-- Name: user_sessions user_sessions_user_row_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_user_row_id_fkey FOREIGN KEY (user_row_id) REFERENCES public.users(row_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict dbmate


--
-- Dbmate schema migrations
--

INSERT INTO public.schema_migrations (version) VALUES
    ('20261111210633'),
    ('20261112024443'),
    ('20261112024829'),
    ('20261112165303'),
    ('20261113042306'),
    ('20261114223258'),
    ('20261114230549'),
    ('20261121025829'),
    ('20261121030229');
