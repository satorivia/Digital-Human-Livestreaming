-- Digital Human Live System - PostgreSQL DDL Draft v1.0
-- This schema is intended as an implementation guide for Alembic migrations.
-- Use UUID primary keys. In production, enable pgcrypto or uuid-ossp.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE merchant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE app_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchant(id),
    email TEXT,
    phone TEXT,
    display_name TEXT NOT NULL,
    password_hash TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE role (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchant(id),
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE permission (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE user_role (
    user_id UUID NOT NULL REFERENCES app_user(id),
    role_id UUID NOT NULL REFERENCES role(id),
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE role_permission (
    role_id UUID NOT NULL REFERENCES role(id),
    permission_id UUID NOT NULL REFERENCES permission(id),
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE shop (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    name TEXT NOT NULL,
    platform TEXT NOT NULL,
    platform_shop_id TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE platform_account (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    shop_id UUID REFERENCES shop(id),
    platform TEXT NOT NULL,
    account_name TEXT NOT NULL,
    platform_account_id TEXT,
    auth_status TEXT NOT NULL DEFAULT 'not_connected',
    token_ref TEXT,
    config JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE product (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    title TEXT NOT NULL,
    brand TEXT,
    category TEXT,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE product_sku (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    product_id UUID NOT NULL REFERENCES product(id),
    sku_code TEXT NOT NULL,
    sku_name TEXT,
    spec JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE product_price (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    sku_id UUID NOT NULL REFERENCES product_sku(id),
    platform TEXT NOT NULL,
    list_price NUMERIC(12,2),
    live_price NUMERIC(12,2),
    currency TEXT NOT NULL DEFAULT 'CNY',
    coupon_info JSONB NOT NULL DEFAULT '{}',
    effective_from TIMESTAMP,
    effective_to TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE product_inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    sku_id UUID NOT NULL REFERENCES product_sku(id),
    platform TEXT NOT NULL,
    quantity INTEGER,
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE product_selling_point (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    product_id UUID NOT NULL REFERENCES product(id),
    title TEXT,
    content TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0,
    risk_level TEXT NOT NULL DEFAULT 'low',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE product_faq (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    product_id UUID NOT NULL REFERENCES product(id),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    platform TEXT,
    risk_level TEXT NOT NULL DEFAULT 'low',
    enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE product_policy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    product_id UUID NOT NULL REFERENCES product(id),
    policy_type TEXT NOT NULL, -- shipping, return, exchange, warranty, after_sales
    content TEXT NOT NULL,
    platform TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE product_forbidden_claim (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    product_id UUID NOT NULL REFERENCES product(id),
    claim TEXT NOT NULL,
    reason TEXT,
    platform TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE product_platform_copy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    product_id UUID NOT NULL REFERENCES product(id),
    platform TEXT NOT NULL,
    copy_type TEXT NOT NULL, -- opening, selling_point, closing, faq, cold_start
    content TEXT NOT NULL,
    risk_level TEXT NOT NULL DEFAULT 'low',
    enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE knowledge_chunk (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    product_id UUID REFERENCES product(id),
    source_type TEXT NOT NULL, -- faq, selling_point, policy, document
    source_id UUID,
    title TEXT,
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL DEFAULT 0,
    qdrant_collection TEXT,
    qdrant_point_id TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE avatar (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    name TEXT NOT NULL,
    style TEXT,
    model_type TEXT NOT NULL DEFAULT 'livetalking',
    provider_config JSONB NOT NULL DEFAULT '{}',
    default_voice_id UUID,
    idle_video_url TEXT,
    fallback_video_url TEXT,
    supported_platforms JSONB NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE voice_profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'zh-CN',
    gender TEXT,
    config JSONB NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE voice_license (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    voice_id UUID NOT NULL REFERENCES voice_profile(id),
    owner_name TEXT NOT NULL,
    source_file_url TEXT,
    consent_document_url TEXT,
    allowed_platforms JSONB NOT NULL DEFAULT '[]',
    commercial_allowed BOOLEAN NOT NULL DEFAULT false,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE live_room (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    shop_id UUID REFERENCES shop(id),
    platform TEXT NOT NULL,
    platform_room_id TEXT,
    name TEXT NOT NULL,
    config JSONB NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE live_session (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    live_room_id UUID NOT NULL REFERENCES live_room(id),
    avatar_id UUID REFERENCES avatar(id),
    voice_id UUID REFERENCES voice_profile(id),
    title TEXT,
    state TEXT NOT NULL DEFAULT 'CREATED',
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    config JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE live_session_product (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    live_session_id UUID NOT NULL REFERENCES live_session(id),
    product_id UUID NOT NULL REFERENCES product(id),
    sort_order INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE live_state_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    live_session_id UUID NOT NULL REFERENCES live_session(id),
    from_state TEXT,
    to_state TEXT NOT NULL,
    event TEXT NOT NULL,
    triggered_by TEXT NOT NULL,
    reason TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE platform_event_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchant(id),
    live_session_id UUID REFERENCES live_session(id),
    platform TEXT NOT NULL,
    room_id TEXT,
    event_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}',
    payload_hash TEXT,
    processed BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE(platform, event_id)
);

CREATE TABLE comment_task (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    event_id TEXT NOT NULL UNIQUE,
    platform TEXT NOT NULL,
    room_id UUID REFERENCES live_room(id),
    live_session_id UUID NOT NULL REFERENCES live_session(id),
    user_nickname TEXT,
    user_platform_hash TEXT,
    content TEXT NOT NULL,
    normalized_content TEXT,
    product_id UUID REFERENCES product(id),
    intent TEXT,
    priority INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE answer_candidate (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    comment_task_id UUID REFERENCES comment_task(id),
    live_session_id UUID NOT NULL REFERENCES live_session(id),
    product_id UUID REFERENCES product(id),
    answer_text TEXT NOT NULL,
    source_type TEXT NOT NULL, -- llm, cache, manual, script
    llm_provider TEXT,
    model_name TEXT,
    prompt_version TEXT,
    risk_level TEXT,
    status TEXT NOT NULL DEFAULT 'generated',
    generation_metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE compliance_result (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    answer_candidate_id UUID REFERENCES answer_candidate(id),
    text TEXT NOT NULL,
    platform TEXT NOT NULL,
    category TEXT,
    blocked BOOLEAN NOT NULL DEFAULT false,
    risk_level TEXT NOT NULL,
    need_human_review BOOLEAN NOT NULL DEFAULT false,
    reasons JSONB NOT NULL DEFAULT '[]',
    suggested_rewrite TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE human_review_task (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    live_session_id UUID NOT NULL REFERENCES live_session(id),
    answer_candidate_id UUID REFERENCES answer_candidate(id),
    status TEXT NOT NULL DEFAULT 'pending',
    original_text TEXT NOT NULL,
    reviewed_text TEXT,
    reviewer_id UUID REFERENCES app_user(id),
    review_reason TEXT,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE tts_asset (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    provider TEXT NOT NULL,
    voice_id UUID REFERENCES voice_profile(id),
    text_hash TEXT NOT NULL,
    text_preview TEXT,
    audio_url TEXT NOT NULL,
    duration_ms INTEGER,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE speech_task (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    live_session_id UUID NOT NULL REFERENCES live_session(id),
    answer_candidate_id UUID REFERENCES answer_candidate(id),
    text TEXT NOT NULL,
    voice_id UUID REFERENCES voice_profile(id),
    tts_asset_id UUID REFERENCES tts_asset(id),
    audio_url TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    priority INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE avatar_command_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    live_session_id UUID NOT NULL REFERENCES live_session(id),
    avatar_id UUID REFERENCES avatar(id),
    speech_task_id UUID REFERENCES speech_task(id),
    command_type TEXT NOT NULL,
    command_payload JSONB NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE media_stream (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    live_session_id UUID NOT NULL REFERENCES live_session(id),
    stream_type TEXT NOT NULL, -- rtmp, webrtc, virtualcam, obs
    stream_url TEXT,
    preview_url TEXT,
    status TEXT NOT NULL DEFAULT 'unknown',
    last_heartbeat_at TIMESTAMP,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE recording_asset (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchant(id),
    live_session_id UUID NOT NULL REFERENCES live_session(id),
    file_url TEXT NOT NULL,
    duration_ms INTEGER,
    status TEXT NOT NULL DEFAULT 'created',
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchant(id),
    actor_user_id UUID REFERENCES app_user(id),
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id UUID,
    before JSONB,
    after JSONB,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchant(id),
    config_key TEXT NOT NULL,
    config_value JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE(merchant_id, config_key)
);

-- Indexes
CREATE INDEX idx_product_merchant_status ON product(merchant_id, status);
CREATE INDEX idx_product_sku_product ON product_sku(product_id);
CREATE INDEX idx_product_price_sku_platform ON product_price(sku_id, platform);
CREATE INDEX idx_live_session_room_state ON live_session(live_room_id, state);
CREATE INDEX idx_live_state_log_session_time ON live_state_log(live_session_id, created_at);
CREATE INDEX idx_platform_event_session_time ON platform_event_log(live_session_id, created_at);
CREATE INDEX idx_comment_task_session_status ON comment_task(live_session_id, status, created_at);
CREATE INDEX idx_answer_candidate_comment ON answer_candidate(comment_task_id);
CREATE INDEX idx_review_task_session_status ON human_review_task(live_session_id, status, created_at);
CREATE INDEX idx_speech_task_session_status ON speech_task(live_session_id, status, priority, created_at);
CREATE INDEX idx_avatar_command_session_status ON avatar_command_log(live_session_id, status, created_at);
CREATE INDEX idx_audit_log_merchant_time ON audit_log(merchant_id, created_at);
