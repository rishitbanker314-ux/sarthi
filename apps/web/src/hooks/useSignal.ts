"use client";

import { useCallback } from "react";
import apiClient from "@sarathi/api-client";
import type { components } from "@sarathi/api-types";

type SignalType = components["schemas"]["SignalType"];
type SignalCreate = components["schemas"]["SignalCreate"];

export function useSignal(lessonId: string) {
  const sendSignal = useCallback(async (
    type: SignalType,
    value: Record<string, any> = {},
    blockId?: string
  ) => {
    try {
      const payload: SignalCreate = {
        type,
        value,
      };
      if (blockId) {
        payload.block_id = blockId;
      }
      
      // Fire and forget
      apiClient.POST("/api/v1/lessons/{id}/signals", {
        params: { path: { id: lessonId } },
        body: payload,
      }).catch(err => console.error("Failed to send signal", err));
    } catch (e) {
      console.error("Error preparing signal", e);
    }
  }, [lessonId]);

  return { sendSignal };
}
