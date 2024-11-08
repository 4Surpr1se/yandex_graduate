-- init.sql

CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY,
    content_id UUID NOT NULL,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_notification_send TIMESTAMP
);
