--
-- SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
-- SPDX-License-Identifier: Apache-2.0
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 13.4 (Debian 13.4-4.pgdg110+1)
-- Dumped by pg_dump version 13.4 (Debian 13.4-4.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: noticelevel; Type: TYPE; Schema: public; Owner: dev
--

CREATE TYPE public.noticelevel AS ENUM (
    'PRIMARY',
    'SECONDARY',
    'SUCCESS',
    'DANGER',
    'WARNING',
    'INFO',
    'ALERT'
);


ALTER TYPE public.noticelevel OWNER TO dev;

--
-- Name: repositoryuserpermission; Type: TYPE; Schema: public; Owner: dev
--

CREATE TYPE public.repositoryuserpermission AS ENUM (
    'READ',
    'WRITE'
);


ALTER TYPE public.repositoryuserpermission OWNER TO dev;

--
-- Name: repositoryuserrole; Type: TYPE; Schema: public; Owner: dev
--

CREATE TYPE public.repositoryuserrole AS ENUM (
    'USER',
    'MANAGER',
    'ADMIN'
);


ALTER TYPE public.repositoryuserrole OWNER TO dev;

--
-- Name: role; Type: TYPE; Schema: public; Owner: dev
--

CREATE TYPE public.role AS ENUM (
    'USER',
    'ADMIN'
);


ALTER TYPE public.role OWNER TO dev;

--
-- Name: workspacetype; Type: TYPE; Schema: public; Owner: dev
--

CREATE TYPE public.workspacetype AS ENUM (
    'PERSISTENT',
    'READONLY'
);


ALTER TYPE public.workspacetype OWNER TO dev;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: dev
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO dev;

--
-- Name: git_models; Type: TABLE; Schema: public; Owner: dev
--

CREATE TABLE public.git_models (
    id integer NOT NULL,
    name character varying,
    path character varying,
    entrypoint character varying,
    revision character varying,
    "primary" boolean,
    repository_name character varying NOT NULL,
    project_id integer NOT NULL
);


ALTER TABLE public.git_models OWNER TO dev;

--
-- Name: git_models_id_seq; Type: SEQUENCE; Schema: public; Owner: dev
--

CREATE SEQUENCE public.git_models_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.git_models_id_seq OWNER TO dev;

--
-- Name: git_models_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev
--

ALTER SEQUENCE public.git_models_id_seq OWNED BY public.git_models.id;


--
-- Name: jenkins; Type: TABLE; Schema: public; Owner: dev
--

CREATE TABLE public.jenkins (
    id integer NOT NULL,
    name character varying,
    git_model_id integer NOT NULL
);


ALTER TABLE public.jenkins OWNER TO dev;

--
-- Name: jenkins_id_seq; Type: SEQUENCE; Schema: public; Owner: dev
--

CREATE SEQUENCE public.jenkins_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.jenkins_id_seq OWNER TO dev;

--
-- Name: jenkins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev
--

ALTER SEQUENCE public.jenkins_id_seq OWNED BY public.jenkins.id;


--
-- Name: notices; Type: TABLE; Schema: public; Owner: dev
--

CREATE TABLE public.notices (
    id integer NOT NULL,
    title character varying,
    message character varying,
    level public.noticelevel,
    scope character varying
);


ALTER TABLE public.notices OWNER TO dev;

--
-- Name: notices_id_seq; Type: SEQUENCE; Schema: public; Owner: dev
--

CREATE SEQUENCE public.notices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notices_id_seq OWNER TO dev;

--
-- Name: notices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev
--

ALTER SEQUENCE public.notices_id_seq OWNED BY public.notices.id;


--
-- Name: projects; Type: TABLE; Schema: public; Owner: dev
--

CREATE TABLE public.projects (
    id integer NOT NULL,
    name character varying,
    repository_name character varying
);


ALTER TABLE public.projects OWNER TO dev;

--
-- Name: projects_id_seq; Type: SEQUENCE; Schema: public; Owner: dev
--

CREATE SEQUENCE public.projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.projects_id_seq OWNER TO dev;

--
-- Name: projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev
--

ALTER SEQUENCE public.projects_id_seq OWNED BY public.projects.id;


--
-- Name: repositories; Type: TABLE; Schema: public; Owner: dev
--

CREATE TABLE public.repositories (
    id integer NOT NULL,
    name character varying
);


ALTER TABLE public.repositories OWNER TO dev;

--
-- Name: repositories_id_seq; Type: SEQUENCE; Schema: public; Owner: dev
--

CREATE SEQUENCE public.repositories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repositories_id_seq OWNER TO dev;

--
-- Name: repositories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev
--

ALTER SEQUENCE public.repositories_id_seq OWNED BY public.repositories.id;


--
-- Name: repository_user_association; Type: TABLE; Schema: public; Owner: dev
--

CREATE TABLE public.repository_user_association (
    username character varying NOT NULL,
    repository_name character varying NOT NULL,
    role public.repositoryuserrole,
    permission public.repositoryuserpermission NOT NULL
);


ALTER TABLE public.repository_user_association OWNER TO dev;

--
-- Name: sessions; Type: TABLE; Schema: public; Owner: dev
--

CREATE TABLE public.sessions (
    id character varying NOT NULL,
    owner_name character varying,
    ports integer[],
    created_at timestamp without time zone,
    guacamole_username character varying,
    guacamole_connection_id character varying,
    repository character varying,
    mac character varying,
    host character varying,
    rdp_password character varying,
    guacamole_password character varying,
    type public.workspacetype DEFAULT 'PERSISTENT'::public.workspacetype NOT NULL
);


ALTER TABLE public.sessions OWNER TO dev;

--
-- Name: users; Type: TABLE; Schema: public; Owner: dev
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying,
    role public.role
);


ALTER TABLE public.users OWNER TO dev;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: dev
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO dev;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: git_models id; Type: DEFAULT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.git_models ALTER COLUMN id SET DEFAULT nextval('public.git_models_id_seq'::regclass);


--
-- Name: jenkins id; Type: DEFAULT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.jenkins ALTER COLUMN id SET DEFAULT nextval('public.jenkins_id_seq'::regclass);


--
-- Name: notices id; Type: DEFAULT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.notices ALTER COLUMN id SET DEFAULT nextval('public.notices_id_seq'::regclass);


--
-- Name: projects id; Type: DEFAULT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.projects ALTER COLUMN id SET DEFAULT nextval('public.projects_id_seq'::regclass);


--
-- Name: repositories id; Type: DEFAULT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.repositories ALTER COLUMN id SET DEFAULT nextval('public.repositories_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: dev
--

COPY public.alembic_version (version_num) FROM stdin;
687484695147
\.


--
-- Data for Name: git_models; Type: TABLE DATA; Schema: public; Owner: dev
--

COPY public.git_models (id, name, path, entrypoint, revision, "primary", repository_name, project_id) FROM stdin;
1	py-capellambse	https://github.com/DSD-DBS/py-capellambse.git	tests/data/melodymodel/5_2/Melody Model Test.aird	master	f	py-capellambse	3
2	collab-platform-arch	https://github.com/DSD-DBS/collab-platform-arch.git	collab-platform-arch.aird	main	t	collab-platform-arch	1
\.


--
-- Data for Name: jenkins; Type: TABLE DATA; Schema: public; Owner: dev
--

COPY public.jenkins (id, name, git_model_id) FROM stdin;
1	py-capellambse - Git Backup	1
2	collab-platform-arch - Git Backup	2
\.


--
-- Data for Name: notices; Type: TABLE DATA; Schema: public; Owner: dev
--

COPY public.notices (id, title, message, level, scope) FROM stdin;
57	Maintenance work	Today maintenance work will take place from 6 p.m. The service may be temporarily unavailable.	DANGER	t4c
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: dev
--

COPY public.projects (id, name, repository_name) FROM stdin;
1	Capella Platform Architecture	collab-platform-arch
2	WizzardEducation	wizzard-education
3	py-capellambse	py-capellambse
\.


--
-- Data for Name: repositories; Type: TABLE DATA; Schema: public; Owner: dev
--

COPY public.repositories (id, name) FROM stdin;
1	collab-platform-arch
2	wizzard-education
3	py-capellambse
\.


--
-- Data for Name: repository_user_association; Type: TABLE DATA; Schema: public; Owner: dev
--

COPY public.repository_user_association (username, repository_name, role, permission) FROM stdin;
timothebaillybarthez	collab-platform-arch	USER	WRITE
timothebaillybarthez	wizzard-education	USER	READ
ernstwuerger	collab-platform-arch	USER	WRITE
ernstwuerger	wizzard-education	USER	READ
ernstwuerger	py-capellambse	USER	WRITE
jamilraichouni	collab-platform-arch	USER	WRITE
jamilraichouni	wizzard-education	USER	READ
jamilraichouni	py-capellambse	USER	WRITE
martinlehmann	py-capellambse	MANAGER	WRITE
martinlehmann	wizzard-education	USER	READ
dominiklammers	wizzard-education	MANAGER	WRITE
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: dev
--

COPY public.sessions (id, owner_name, ports, created_at, guacamole_username, guacamole_connection_id, repository, mac, host, rdp_password, guacamole_password, type) FROM stdin;
356db170c0ff3389afc97048b2f7cae2cd84553c4728b2ade0d42cf30e1bbc00	moritzweber	{50000}	2022-04-22 04:31:54.629846	pRuIXWCxsS	2457		02:42:ac:11:00:02	localhost	Ruu6RziwA5jtEXbW2bpgVTvGk300wZCKUWNxvBUScNXJkVv3ufMhI4ifgzsExq6i	uxpuMD5fKY2PT9mbmKbnbofQ3wPzS91WAQdvopr1ilzmmni6zJMFgUk1KxUeXKb5	PERSISTENT
02bdee5a9c2c48cf063f1aaf8af25b32aa1cd5c6938edc7c0bc4964dcbf4906c	viktorkravchenko	{50002}	2022-04-22 05:23:12.862638	16yJciAO1K	2459	collab-platform-arch	02:42:ac:11:00:03	localhost	HBGsqSDGsueqAHdd2Ey84FRI7pQmncuRPsIwJKN8uZEsEzLZmi0qLCCS6pAAGOHl	j8oAZYQBS6mTm62k3RSXROxxL6mMNvRwKX7gzSr26ibAIU28vuLiHUuIBDNvi7wr	READONLY
0d6bb0f334ab6d16058fce4031d0c18c0291724218bf59e5e03a922b44ec8b13	timothebaillybarthez	{50003}	2022-04-22 05:54:16.058932	zrgTeOV5NM	2460	wizzard-education	02:42:ac:11:00:04	localhost	xXYGUsft3kWu9K0CuvucYVzVzNR0r1Lr9KPBXbglx6ZQ47UqchqcGtU0ekcyBhFh	EGfBRgcMHRaKjgJCmcJt7A8o9ALBxXW67YbseHWMVoQN5maP5JrbVlVDxMQ2KxeP	READONLY
2189f857e1992b985e91447ab99975c330fc41601d751041ea2275f5debefc37	ernstwuerger	{50005}	2022-04-22 06:43:26.208018	8EuCLtuVhb	2462		02:42:ac:11:00:06	localhost	R8xCUdNdKh7gcNevsVA0yx71F1Lw6vGh1G628LbbpL6LvCDGKvG5tr7H5WQrd3ru	ZthPyKrtSIGPQxzYVyCRe5xdZaVPLwWyXSpNf5CI0lrPIoNtM3dalzaGyGCcFt3y	PERSISTENT
e2cc9cc4a3d0be4789fef4afacf6a3e557de7ebf9729f15397eb2f99c43dbce2	jamilraichouni	{50006}	2022-04-22 06:56:38.681194	cEOBH7ewgX	2463	wizzard-education	02:42:ac:11:00:07	localhost	lozwaY1seJ0acggt8MDUBVnPJRHnhBupIgU2EnHJ6q1oc6AwN7m3fX7QaRJINbrb	SCjkgf9eKe4OCaqFsi6dYzwJIgcWDx6SsPxCk5WzaAjt7jAFFfdPMc7dR6Qv2dx0	READONLY
207f9f1ea5b3c7982434f27ca1b99ade043c3a93d13ca026aa2521217a36a4a9	martinlehmann	{50007}	2022-04-22 07:02:57.035976	C2TE5zCRXv	2464		02:42:ac:11:00:08	localhost	k7r3O592gJspnOS0636DlPq5gS8y4Q99k9P6WTCn7r0H4ouITyNDBbPztz1N3gTr	NPxvrfZfRCAZe6AWpRGw9Yd5L3EmoR0qXTASim5CqT9oAf9nSCNC3796jInC2dBD	PERSISTENT
c2c5f811c949e9c2ddacca8d2ea9ca57aa474bbfcab38f0c48875b997821c63c	dominiklammers	{50008}	2022-04-22 07:53:05.759363	TmifzOQ8Ij	2465	wizzard-education	02:42:ac:11:00:09	localhost	ag35bl0lW1JBri7tNvRDFZFEjQjF2FJXUgB9jhv9FcACUTdZDSE4VOXzg2B8QKbl	41ztDy5ItUlH82ZTTSFUqJ2Okg3BP74lPXZXVhRiRAiErY4eoIF2eWKgYDUNfHWJ	READONLY
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: dev
--

COPY public.users (id, name, role) FROM stdin;
1	moritzweber	ADMIN
2	viktorkravchenko	ADMIN
3	timothebaillybarthez	USER
4	ernstwuerger	USER
5	jamilraichouni	USER
6	martinlehmann	USER
7	dominiklammers	USER
\.


--
-- Name: git_models_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev
--

SELECT pg_catalog.setval('public.git_models_id_seq', 11, true);


--
-- Name: jenkins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev
--

SELECT pg_catalog.setval('public.jenkins_id_seq', 12, true);


--
-- Name: notices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev
--

SELECT pg_catalog.setval('public.notices_id_seq', 57, true);


--
-- Name: projects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev
--

SELECT pg_catalog.setval('public.projects_id_seq', 9, true);


--
-- Name: repositories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev
--

SELECT pg_catalog.setval('public.repositories_id_seq', 15, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev
--

SELECT pg_catalog.setval('public.users_id_seq', 181, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: git_models git_models_pkey; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.git_models
    ADD CONSTRAINT git_models_pkey PRIMARY KEY (id);


--
-- Name: jenkins jenkins_pkey; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.jenkins
    ADD CONSTRAINT jenkins_pkey PRIMARY KEY (id, git_model_id);


--
-- Name: notices notices_pkey; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.notices
    ADD CONSTRAINT notices_pkey PRIMARY KEY (id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: repositories repositories_pkey; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.repositories
    ADD CONSTRAINT repositories_pkey PRIMARY KEY (id);


--
-- Name: repository_user_association repository_user_association_pkey; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.repository_user_association
    ADD CONSTRAINT repository_user_association_pkey PRIMARY KEY (username, repository_name);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_git_models_id; Type: INDEX; Schema: public; Owner: dev
--

CREATE INDEX ix_git_models_id ON public.git_models USING btree (id);


--
-- Name: ix_jenkins_id; Type: INDEX; Schema: public; Owner: dev
--

CREATE INDEX ix_jenkins_id ON public.jenkins USING btree (id);


--
-- Name: ix_notices_id; Type: INDEX; Schema: public; Owner: dev
--

CREATE INDEX ix_notices_id ON public.notices USING btree (id);


--
-- Name: ix_projects_id; Type: INDEX; Schema: public; Owner: dev
--

CREATE INDEX ix_projects_id ON public.projects USING btree (id);


--
-- Name: ix_projects_name; Type: INDEX; Schema: public; Owner: dev
--

CREATE INDEX ix_projects_name ON public.projects USING btree (name);


--
-- Name: ix_repositories_id; Type: INDEX; Schema: public; Owner: dev
--

CREATE INDEX ix_repositories_id ON public.repositories USING btree (id);


--
-- Name: ix_repositories_name; Type: INDEX; Schema: public; Owner: dev
--

CREATE UNIQUE INDEX ix_repositories_name ON public.repositories USING btree (name);


--
-- Name: ix_sessions_id; Type: INDEX; Schema: public; Owner: dev
--

CREATE INDEX ix_sessions_id ON public.sessions USING btree (id);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: dev
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_name; Type: INDEX; Schema: public; Owner: dev
--

CREATE UNIQUE INDEX ix_users_name ON public.users USING btree (name);


--
-- Name: git_models git_models_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.git_models
    ADD CONSTRAINT git_models_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: git_models git_models_repository_name_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.git_models
    ADD CONSTRAINT git_models_repository_name_fkey FOREIGN KEY (repository_name) REFERENCES public.repositories(name) ON DELETE CASCADE;


--
-- Name: jenkins jenkins_git_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.jenkins
    ADD CONSTRAINT jenkins_git_model_id_fkey FOREIGN KEY (git_model_id) REFERENCES public.git_models(id) ON DELETE CASCADE;


--
-- Name: projects projects_repository_name_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_repository_name_fkey FOREIGN KEY (repository_name) REFERENCES public.repositories(name) ON DELETE CASCADE;


--
-- Name: repository_user_association repository_user_association_repository_name_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.repository_user_association
    ADD CONSTRAINT repository_user_association_repository_name_fkey FOREIGN KEY (repository_name) REFERENCES public.repositories(name);


--
-- Name: repository_user_association repository_user_association_username_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.repository_user_association
    ADD CONSTRAINT repository_user_association_username_fkey FOREIGN KEY (username) REFERENCES public.users(name);


--
-- Name: sessions sessions_owner_name_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_owner_name_fkey FOREIGN KEY (owner_name) REFERENCES public.users(name);


--
-- PostgreSQL database dump complete
--
