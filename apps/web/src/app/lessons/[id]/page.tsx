"use client";

import { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import apiClient from "@sarathi/api-client";
import { parseSSEChunk, StreamEvent } from "@sarathi/api-client";
import { BlockRenderer } from "@/components/blocks/BlockRenderer";
import { Button, Card, CardContent, Skeleton } from "@sarathi/ui";
import type { components, ContentBlock } from "@sarathi/api-types";
import { TutorDrawer } from "@/components/tutor/TutorDrawer";
import { useSignal } from "@/hooks/useSignal";

export default function LessonPage() {
  const { id } = useParams() as { id: string };
  const router = useRouter();
  
  const [blocks, setBlocks] = useState<ContentBlock[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionData, setSessionData] = useState<any>(null); // From Supabase session
  const { sendSignal } = useSignal(id);

  // Fetch session to inject token into SSE fetch
  useEffect(() => {
    // We get the token manually to pass to fetch
    const getToken = async () => {
      try {
        const { createClient } = await import('@supabase/supabase-js');
        const supabase = createClient(
          process.env.NEXT_PUBLIC_SUPABASE_URL!,
          process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
        );
        const { data } = await supabase.auth.getSession();
        setSessionData(data.session);
      } catch (e) {
        console.error("Failed to get session", e);
      }
    };
    getToken();
  }, []);

  const { data: lessonMeta, isLoading: metaLoading } = useQuery({
    queryKey: ["lesson", id],
    queryFn: async () => {
      const { data, error } = await apiClient.GET("/api/v1/lessons/{id}", {
        params: { path: { id } }
      });
      if (error) throw error;
      return data;
    }
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (!sessionData?.access_token) return;
    
    // Start streaming content
    const startStreaming = async () => {
      setIsStreaming(true);
      setError(null);
      setBlocks([]);
      
      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:4010"}/api/v1/lessons/${id}/content`, {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${sessionData.access_token}`
          },
          signal: abortController.signal
        });

        if (!response.ok) {
          throw new Error(`Failed to start stream: ${response.status} ${response.statusText}`);
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error("No readable stream available");

        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const parsed = parseSSEChunk(chunk, buffer);
          buffer = parsed.buffer;

          for (const event of parsed.events) {
            if (event.type === "block") {
              setBlocks(prev => [...prev, event.block as ContentBlock]);
            } else if (event.type === "done") {
              setIsStreaming(false);
            } else if (event.type === "error") {
              setError(event.message);
              setIsStreaming(false);
              abortController.abort();
            }
          }
        }
      } catch (err: any) {
        if (err.name !== "AbortError") {
          setError(err.message || "An error occurred while streaming");
          setIsStreaming(false);
        }
      }
    };

    startStreaming();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [id, sessionData]);

  const handleReexplain = async () => {
    sendSignal("confusion_flag", { action: "reexplain_requested" });
    if (!sessionData?.access_token) return;
    if (isStreaming) return; // Wait for current stream to finish
    
    setIsStreaming(true);
    setError(null);
    
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:4010"}/api/v1/lessons/${id}/reexplain`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${sessionData.access_token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({}),
        signal: abortController.signal
      });

      if (!response.ok) {
        throw new Error(`Failed to start re-explain stream: ${response.status} ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No readable stream available");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const parsed = parseSSEChunk(chunk, buffer);
        buffer = parsed.buffer;

        for (const event of parsed.events) {
          if (event.type === "block") {
            setBlocks(prev => [...prev, event.block as ContentBlock]);
          } else if (event.type === "done") {
            setIsStreaming(false);
          } else if (event.type === "error") {
            setError(event.message);
            setIsStreaming(false);
            abortController.abort();
          }
        }
      }
    } catch (err: any) {
      if (err.name !== "AbortError") {
        setError(err.message || "An error occurred while streaming");
        setIsStreaming(false);
      }
    }
  };

  return (
    <div className="container max-w-3xl mx-auto py-8 px-4 flex gap-6">
      <div className="flex-1 space-y-8 animate-in fade-in duration-500">
        <div>
          {metaLoading ? (
            <Skeleton className="h-10 w-3/4 mb-4" />
          ) : (
            <h1 className="text-3xl font-bold tracking-tight mb-4">
              {(lessonMeta as components["schemas"]["LessonResponse"])?.title || "Lesson"}
            </h1>
          )}
        </div>

        <div className="space-y-6" aria-live="polite">
          {blocks.map((block, i) => (
            <div key={`${block.id}-${i}`} className="animate-in slide-in-from-bottom-4 duration-300">
              <BlockRenderer block={block} />
            </div>
          ))}
          
          {isStreaming && (
            <div className="flex justify-center py-4">
              <div className="flex items-center gap-2 text-muted-foreground">
                <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                <div className="w-2 h-2 rounded-full bg-primary animate-pulse delay-75" />
                <div className="w-2 h-2 rounded-full bg-primary animate-pulse delay-150" />
              </div>
            </div>
          )}
          
          {error && (
            <Card className="border-destructive/50 bg-destructive/10">
              <CardContent className="py-4 text-destructive">
                {error}
              </CardContent>
            </Card>
          )}
        </div>

        {!isStreaming && blocks.length > 0 && !error && (
          <div className="flex justify-between items-center pt-8 border-t">
            <div className="flex gap-4">
              <Button variant="outline" onClick={handleReexplain}>
                I'm lost. Explain differently.
              </Button>
              <TutorDrawer lessonId={id} sessionData={sessionData} />
            </div>
            <Button onClick={() => router.push(`/lessons/${id}/checkpoint`)}>
              Take Checkpoint
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
