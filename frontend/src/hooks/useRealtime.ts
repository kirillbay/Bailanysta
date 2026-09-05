import { useEffect, useRef, useState, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";

function getWsUrl(): string {
  const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
  const wsUrl = apiUrl.replace(/^http/, "ws") + "/api/v1/ws";
  return wsUrl;
}

export function useChannelRealtime(channelId: string | null) {
  const qc = useQueryClient();
  const [status, setStatus] = useState<"connecting" | "connected" | "reconnecting" | "offline">("offline");
  const wsRef = useRef<WebSocket | null>(null);
  const backoffRef = useRef(1000);

  const connect = useCallback(() => {
    if (!channelId) return;
    setStatus("connecting");
    const ws = new WebSocket(getWsUrl());
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus("connected");
      backoffRef.current = 1000;
      ws.send(JSON.stringify({ type: "subscribe", payload: { channel_id: channelId } }));
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "message.created") {
          // deduplicate by id handled via invalidate, but also append optimistically
          qc.invalidateQueries({ queryKey: ["club-messages"] });
        } else if (msg.type === "message.updated") {
          qc.invalidateQueries({ queryKey: ["club-messages"] });
        } else if (msg.type === "message.deleted") {
          qc.invalidateQueries({ queryKey: ["club-messages"] });
        }
      } catch {}
    };

    ws.onclose = () => {
      setStatus("reconnecting");
      const delay = Math.min(backoffRef.current, 16000);
      setTimeout(() => {
        backoffRef.current = Math.min(backoffRef.current * 2, 16000);
        connect();
      }, delay);
    };

    ws.onerror = () => {
      try {
        ws.close();
      } catch {}
    };
  }, [channelId, qc]);

  useEffect(() => {
    connect();
    return () => {
      try {
        wsRef.current?.close();
      } catch {}
    };
  }, [connect]);

  return { status };
}

export function useNotificationsRealtime() {
  const qc = useQueryClient();
  const [status, setStatus] = useState<"connected" | "offline">("offline");
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const wsUrl = getWsUrl();
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => setStatus("connected");
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "notification.created") {
          qc.invalidateQueries({ queryKey: ["notifications"] });
          qc.invalidateQueries({ queryKey: ["notifications-unread"] });
        }
      } catch {}
    };
    ws.onclose = () => setStatus("offline");
    return () => {
      try {
        ws.close();
      } catch {}
    };
  }, [qc]);

  return { status };
}
