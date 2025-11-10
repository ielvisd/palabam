-- Realtime setup for multiplayer sync
-- Enables Supabase Realtime subscriptions for quests and sessions

-- Enable replication for realtime
ALTER PUBLICATION supabase_realtime ADD TABLE public.quests;
ALTER PUBLICATION supabase_realtime ADD TABLE public.sessions;

-- Note: Realtime is automatically enabled for tables added to the publication
-- The frontend will subscribe to changes using Supabase Realtime client

