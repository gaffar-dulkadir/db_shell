-- UUID generation'ı Python tarafında halledelim, sadece gerekli kısımları çalıştıralım

-- Configuration settings
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

-- Create schemas
CREATE SCHEMA IF NOT EXISTS auth;
ALTER SCHEMA auth OWNER TO postgres;

CREATE SCHEMA IF NOT EXISTS chats;
ALTER SCHEMA chats OWNER TO postgres;

CREATE SCHEMA IF NOT EXISTS marketplace;
ALTER SCHEMA marketplace OWNER TO postgres;

-- Create extension (fallback için)
CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;
COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';

-- AUTH SCHEMA TABLES
CREATE TABLE auth.users (
    user_id uuid NOT NULL,
    user_name character varying(255) NOT NULL,
    user_surname character varying(255) NOT NULL,
    user_email character varying(254) NOT NULL,
    user_created_at timestamp with time zone DEFAULT now() NOT NULL,
    user_updated_at timestamp with time zone DEFAULT now() NOT NULL,
    password_hash text NOT NULL,
    CONSTRAINT email_lowercase CHECK (((user_email)::text = lower((user_email)::text))),
    CONSTRAINT email_syntax CHECK (((user_email)::text ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'::text))
);

CREATE TABLE auth.user_profiles (
    user_id uuid NOT NULL,
    bio text,
    avatar_url text,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE auth.user_settings (
    user_id uuid NOT NULL,
    theme character varying(20) DEFAULT 'dark'::character varying,
    notifications_enabled boolean DEFAULT true,
    language character varying(10) DEFAULT 'tr'::character varying,
    privacy_mode boolean DEFAULT false,
    bot_behavior character varying(255) DEFAULT 'kind'::character varying,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

-- MARKETPLACE SCHEMA TABLES
CREATE TABLE marketplace.bot_categories (
    category_id uuid NOT NULL,
    category_name character varying(100) NOT NULL,
    category_description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE marketplace.bots (
    bot_id uuid NOT NULL,
    default_system_prompt text,
    default_knowledge text,
    bot_name character varying(255) NOT NULL,
    bot_description text,
    bot_avatar_url text,
    bot_category_id uuid,
    bot_owner_id uuid NOT NULL,
    bot_status character varying(50) DEFAULT 'active'::character varying NOT NULL,
    is_public boolean DEFAULT true NOT NULL,
    bot_version character varying(50) DEFAULT '1.0'::character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    bot_default_memory text
);

-- CHATS SCHEMA TABLES
CREATE TABLE chats.conversation (
    conversation_id uuid NOT NULL,
    conversation_user_id uuid NOT NULL,
    conversation_bot_id uuid NOT NULL,
    default_system_prompt text,
    default_knowledge text,
    memory text,
    conversation_title character varying(255),
    conversation_status character varying(50) DEFAULT 'active'::character varying NOT NULL,
    conversation_created_at timestamp with time zone DEFAULT now() NOT NULL,
    conversation_updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE chats.message (
    message_id uuid NOT NULL,
    message_conversation_id uuid NOT NULL,
    message_parent_message_id uuid,
    message_role character varying(20) NOT NULL,
    message_bot_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE chats.document (
    document_id uuid NOT NULL,
    document_uploaded_by uuid NOT NULL,
    document_filename character varying(500) NOT NULL,
    document_file_size bigint NOT NULL,
    document_mime_type character varying(100) NOT NULL,
    document_content text NOT NULL,
    document_message_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE chats.memory_history (
    id uuid NOT NULL,
    conversation_id uuid NOT NULL,
    date_time timestamp without time zone NOT NULL,
    memory_history text NOT NULL
);

-- SET TABLE OWNERS
ALTER TABLE auth.users OWNER TO postgres;
ALTER TABLE auth.user_profiles OWNER TO postgres;
ALTER TABLE auth.user_settings OWNER TO postgres;
ALTER TABLE marketplace.bot_categories OWNER TO postgres;
ALTER TABLE marketplace.bots OWNER TO postgres;
ALTER TABLE chats.conversation OWNER TO postgres;
ALTER TABLE chats.message OWNER TO postgres;
ALTER TABLE chats.document OWNER TO postgres;
ALTER TABLE chats.memory_history OWNER TO postgres;

-- PRIMARY KEY CONSTRAINTS
ALTER TABLE ONLY auth.users ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);
ALTER TABLE ONLY auth.users ADD CONSTRAINT users_user_email_key UNIQUE (user_email);
ALTER TABLE ONLY auth.user_profiles ADD CONSTRAINT user_profiles_pkey PRIMARY KEY (user_id);
ALTER TABLE ONLY auth.user_settings ADD CONSTRAINT user_settings_pkey PRIMARY KEY (user_id);

ALTER TABLE ONLY marketplace.bot_categories ADD CONSTRAINT bot_categories_pkey PRIMARY KEY (category_id);
ALTER TABLE ONLY marketplace.bot_categories ADD CONSTRAINT bot_categories_category_name_key UNIQUE (category_name);
ALTER TABLE ONLY marketplace.bots ADD CONSTRAINT bots_pkey PRIMARY KEY (bot_id);
ALTER TABLE ONLY marketplace.bots ADD CONSTRAINT bots_bot_name_key UNIQUE (bot_name);

ALTER TABLE ONLY chats.conversation ADD CONSTRAINT conversation_pkey PRIMARY KEY (conversation_id);
ALTER TABLE ONLY chats.message ADD CONSTRAINT message_pkey PRIMARY KEY (message_id);
ALTER TABLE ONLY chats.document ADD CONSTRAINT document_pkey PRIMARY KEY (document_id);
ALTER TABLE ONLY chats.memory_history ADD CONSTRAINT memort_history_pkey PRIMARY KEY (id);

-- FOREIGN KEY CONSTRAINTS
ALTER TABLE ONLY auth.user_profiles ADD CONSTRAINT user_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(user_id) ON DELETE CASCADE;
ALTER TABLE ONLY auth.user_settings ADD CONSTRAINT user_settings_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(user_id) ON DELETE CASCADE;

ALTER TABLE ONLY marketplace.bots ADD CONSTRAINT fk_bot_category FOREIGN KEY (bot_category_id) REFERENCES marketplace.bot_categories(category_id) ON DELETE SET NULL;
ALTER TABLE ONLY marketplace.bots ADD CONSTRAINT fk_bot_owner FOREIGN KEY (bot_owner_id) REFERENCES auth.users(user_id) ON DELETE CASCADE;

ALTER TABLE ONLY chats.conversation ADD CONSTRAINT fk_conversation_user FOREIGN KEY (conversation_user_id) REFERENCES auth.users(user_id) ON DELETE CASCADE;
ALTER TABLE ONLY chats.conversation ADD CONSTRAINT fk_conversation_bot FOREIGN KEY (conversation_bot_id) REFERENCES marketplace.bots(bot_id) ON DELETE CASCADE;

ALTER TABLE ONLY chats.message ADD CONSTRAINT fk_message_conversation FOREIGN KEY (message_conversation_id) REFERENCES chats.conversation(conversation_id) ON DELETE CASCADE;
ALTER TABLE ONLY chats.message ADD CONSTRAINT fk_message_bot FOREIGN KEY (message_bot_id) REFERENCES marketplace.bots(bot_id) ON DELETE CASCADE;
ALTER TABLE ONLY chats.message ADD CONSTRAINT fk_parent_message FOREIGN KEY (message_parent_message_id) REFERENCES chats.message(message_id) ON DELETE SET NULL;

ALTER TABLE ONLY chats.document ADD CONSTRAINT fk_document_message FOREIGN KEY (document_message_id) REFERENCES chats.message(message_id) ON DELETE CASCADE;
ALTER TABLE ONLY chats.document ADD CONSTRAINT fk_document_uploaded_by FOREIGN KEY (document_uploaded_by) REFERENCES auth.users(user_id) ON DELETE CASCADE;

ALTER TABLE ONLY chats.memory_history ADD CONSTRAINT fk_memory_conversation FOREIGN KEY (conversation_id) REFERENCES chats.conversation(conversation_id) ON DELETE CASCADE;

-- PERFORMANCE INDEXES
CREATE INDEX idx_users_email ON auth.users(user_email);
CREATE INDEX idx_conversation_user_id ON chats.conversation(conversation_user_id);
CREATE INDEX idx_conversation_bot_id ON chats.conversation(conversation_bot_id);
CREATE INDEX idx_message_conversation_id ON chats.message(message_conversation_id);
CREATE INDEX idx_message_created_at ON chats.message(created_at DESC);
CREATE INDEX idx_message_parent_id ON chats.message(message_parent_message_id);
CREATE INDEX idx_document_message_id ON chats.document(document_message_id);
CREATE INDEX idx_memory_conversation_id ON chats.memory_history(conversation_id);
CREATE INDEX idx_memory_datetime ON chats.memory_history(date_time DESC);
CREATE INDEX idx_bots_owner_id ON marketplace.bots(bot_owner_id);
CREATE INDEX idx_bots_category_id ON marketplace.bots(bot_category_id);
CREATE INDEX idx_bots_public ON marketplace.bots(is_public) WHERE is_public = true;

-- Success message
SELECT 'Database schema created successfully! UUID generation will be handled by Python.' as result;