"use client";

import { useState, useRef, useEffect } from "react";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@sarathi/ui";
import { Button } from "@sarathi/ui";
import { Input } from "@sarathi/ui";
import { parseSSEChunk } from "@sarathi/api-client";
import { BlockRenderer } from "@/components/blocks/BlockRenderer";
import type { ContentBlock } from "@sarathi/api-types";
import { Send, MessageCircle } from "lucide-react";
import { useSignal } from "@/hooks/useSignal";

interface Message {
  id: string;
  role: "user" | "tutor";
  content: string;
  blocks: ContentBlock[];
}

interface TutorDrawerProps {
  lessonId: string;
  sessionData: any;
  children?: React.ReactNode;
}

export function TutorDrawer({ lessonId, sessionData, children }: TutorDrawerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const { sendSignal } = useSignal(lessonId);

  // Send signal on open
  useEffect(() => {
    if (isOpen) {
      sendSignal("hint_requested", { context: "tutor_drawer_opened" });
    }
  }, [isOpen, sendSignal]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isStreaming]);

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isStreaming || !sessionData?.access_token) return;

    const userMessage = input;
    setInput("");
    
    const newId = Math.random().toString(36).substring(2, 9);
    setMessages(prev => [
      ...prev,
      { id: `user-${newId}`, role: "user", content: userMessage, blocks: [] }
    ]);
    
    // Add empty tutor message
    const tutorMsgId = `tutor-${newId}`;
    setMessages(prev => [
      ...prev,
      { id: tutorMsgId, role: "tutor", content: "", blocks: [] }
    ]);

    setIsStreaming(true);
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:4010"}/api/v1/tutor/messages`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${sessionData.access_token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          lesson_id: lessonId,
          content: userMessage
        }),
        signal: abortController.signal
      });

      if (!response.ok) {
        throw new Error(`Failed to send message: ${response.status}`);
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
          if (event.type === "token") {
            setMessages(prev => prev.map(msg => 
              msg.id === tutorMsgId 
                ? { ...msg, content: msg.content + (event.text || "") }
                : msg
            ));
          } else if (event.type === "block") {
            setMessages(prev => prev.map(msg => 
              msg.id === tutorMsgId 
                ? { ...msg, blocks: [...msg.blocks, event.block as ContentBlock] }
                : msg
            ));
          } else if (event.type === "done" || event.type === "error") {
            setIsStreaming(false);
            if (event.type === "error") {
              abortController.abort();
            }
          }
        }
      }
    } catch (err: any) {
      if (err.name !== "AbortError") {
        console.error("Tutor stream error:", err);
        setIsStreaming(false);
      }
    }
  };

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        {children || (
          <Button variant="outline" size="sm" className="gap-2">
            <MessageCircle className="w-4 h-4" />
            Ask Tutor
          </Button>
        )}
      </SheetTrigger>
      <SheetContent className="w-full sm:max-w-md flex flex-col p-0">
        <SheetHeader className="p-4 border-b">
          <SheetTitle>Tutor Chat</SheetTitle>
        </SheetHeader>
        
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-4 space-y-6"
          aria-live="polite"
        >
          {messages.length === 0 && (
            <div className="text-center text-muted-foreground mt-8">
              <MessageCircle className="w-12 h-12 mx-auto mb-4 opacity-20" />
              <p>Ask anything about this lesson.</p>
            </div>
          )}
          
          {messages.map(msg => (
            <div 
              key={msg.id} 
              className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
            >
              <div 
                className={`px-4 py-2 rounded-lg max-w-[90%] ${
                  msg.role === "user" 
                    ? "bg-primary text-primary-foreground rounded-br-none" 
                    : "bg-muted rounded-bl-none"
                }`}
              >
                {msg.content && <div className="whitespace-pre-wrap text-sm">{msg.content}</div>}
              </div>
              
              {msg.blocks && msg.blocks.length > 0 && (
                <div className="mt-3 space-y-3 w-full pl-2 border-l-2 border-primary/20">
                  {msg.blocks.map((block, idx) => (
                    <BlockRenderer key={idx} block={block} />
                  ))}
                </div>
              )}
            </div>
          ))}
          
          {isStreaming && (
            <div className="flex items-center gap-1 text-muted-foreground pt-2">
              <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
              <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse delay-75" />
              <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse delay-150" />
            </div>
          )}
        </div>
        
        <div className="p-4 border-t bg-background">
          <form 
            onSubmit={handleSubmit}
            className="flex items-center gap-2"
          >
            <Input 
              placeholder="Ask a question..." 
              value={input}
              onChange={e => setInput(e.target.value)}
              disabled={isStreaming}
              className="flex-1"
            />
            <Button 
              type="submit" 
              size="icon"
              disabled={!input.trim() || isStreaming}
            >
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </div>
      </SheetContent>
    </Sheet>
  );
}
