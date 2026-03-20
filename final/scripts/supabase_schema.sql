-- Run this in Supabase SQL Editor once.

create extension if not exists pgcrypto;

create table if not exists public.users (
  id uuid primary key,
  email text unique not null,
  api_token uuid unique not null,
  created_at timestamptz default now()
);

create table if not exists public.monitor_settings (
  user_id uuid primary key references public.users(id) on delete cascade,
  interval_seconds integer not null default 60,
  threshold double precision not null default 0.85,
  updated_at timestamptz default now()
);

create table if not exists public.model_versions (
  id bigserial primary key,
  user_id uuid references public.users(id) on delete set null,
  model_version text,
  s3_path text,
  created_at timestamptz default now()
);

alter table public.users enable row level security;
alter table public.monitor_settings enable row level security;
alter table public.model_versions enable row level security;

-- Predictions table: stores all prediction history for audit trail
create table if not exists public.predictions (
  id bigserial primary key,
  user_id uuid references public.users(id) on delete cascade,
  api_key text not null,
  timestamp timestamptz default now(),
  input_data jsonb not null,
  score double precision not null,
  is_anomaly boolean not null,
  recommended_action text not null,
  processing_time_ms integer,
  model_version text
);

create index if not exists idx_predictions_user_id on public.predictions(user_id);
create index if not exists idx_predictions_timestamp on public.predictions(timestamp);
alter table public.predictions enable row level security;

-- Alerts table: stores all triggered alerts with delivery status
create table if not exists public.alerts (
  id bigserial primary key,
  user_id uuid references public.users(id) on delete cascade,
  prediction_id bigint references public.predictions(id) on delete set null,
  timestamp timestamptz default now(),
  alert_type text not null,
  severity text not null,
  score double precision not null,
  payload jsonb not null,
  status text default 'pending',
  error_message text
);

create index if not exists idx_alerts_user_id on public.alerts(user_id);
create index if not exists idx_alerts_status on public.alerts(status);
create index if not exists idx_alerts_timestamp on public.alerts(timestamp);
alter table public.alerts enable row level security;

-- API Logs table: stores all API access for monitoring
create table if not exists public.api_logs (
  id bigserial primary key,
  user_id uuid,
  api_key text,
  endpoint text not null,
  method text not null,
  timestamp timestamptz default now(),
  status_code integer,
  response_time_ms integer,
  error_message text
);

create index if not exists idx_api_logs_user_id on public.api_logs(user_id);
create index if not exists idx_api_logs_timestamp on public.api_logs(timestamp);
alter table public.api_logs enable row level security;

-- Performance Metrics table: stores model performance over time
create table if not exists public.performance_metrics (
  id bigserial primary key,
  user_id uuid references public.users(id) on delete set null,
  timestamp timestamptz default now(),
  metric_type text not null,
  metric_value double precision not null,
  metadata jsonb
);

create index if not exists idx_performance_metrics_timestamp on public.performance_metrics(timestamp);
alter table public.performance_metrics enable row level security;

-- Add notification preferences to monitor_settings
alter table public.monitor_settings
add column if not exists notification_channels text[] default array['webhook']::text[];

-- Service role bypasses RLS; keep policies minimal for now.
