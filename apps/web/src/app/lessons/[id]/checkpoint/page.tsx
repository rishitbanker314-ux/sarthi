"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import apiClient from "@sarathi/api-client";
import { Card, CardContent, CardHeader, CardTitle, CardFooter, Button, Skeleton, Badge } from "@sarathi/ui";
import { CheckCircle2, XCircle, Trophy, ArrowRight } from "lucide-react";
import type { components } from "@sarathi/api-types";
import { AdaptationDialog } from "@/components/adaptation/AdaptationDialog";

type CheckpointResponse = components["schemas"]["CheckpointResponse"];
type CheckpointAttemptResponse = components["schemas"]["CheckpointAttemptResponse"];

export default function CheckpointPage() {
  const { id } = useParams() as { id: string };
  const router = useRouter();

  const [responses, setResponses] = useState<Record<string, string>>({});
  const [attemptResult, setAttemptResult] = useState<CheckpointAttemptResponse | null>(null);

  // Generate checkpoint
  const { data: checkpoint, isLoading: isGenerating } = useQuery({
    queryKey: ["checkpoint", id],
    queryFn: async () => {
      const { data, error } = await apiClient.POST("/api/v1/lessons/{lesson_id}/checkpoint", {
        params: { path: { lesson_id: id } }
      });
      if (error) throw error;
      return data as CheckpointResponse;
    },
    // Prevent refetching to avoid generating multiple checkpoints
    refetchOnWindowFocus: false,
    staleTime: Infinity,
  });

  // Submit checkpoint
  const submitMutation = useMutation({
    mutationFn: async () => {
      if (!checkpoint) throw new Error("No checkpoint to submit");
      const { data, error } = await apiClient.POST("/api/v1/checkpoints/{checkpoint_id}/submit", {
        params: { path: { checkpoint_id: checkpoint.id } },
        body: { responses }
      });
      if (error) throw error;
      return data as CheckpointAttemptResponse;
    },
    onSuccess: (data) => {
      setAttemptResult(data);
    }
  });

  const handleOptionSelect = (itemId: string, option: string) => {
    setResponses(prev => ({
      ...prev,
      [itemId]: option
    }));
  };

  const isAllAnswered = checkpoint?.items?.length === Object.keys(responses).length;

  if (isGenerating) {
    return (
      <div className="container max-w-2xl mx-auto py-12 px-4 space-y-6">
        <div className="text-center space-y-4 mb-8">
          <Skeleton className="h-10 w-64 mx-auto" />
          <Skeleton className="h-5 w-48 mx-auto" />
        </div>
        {[1, 2].map(i => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-3/4" />
            </CardHeader>
            <CardContent className="space-y-3">
              {[1, 2, 3, 4].map(j => (
                <Skeleton key={j} className="h-12 w-full" />
              ))}
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (attemptResult) {
    return (
      <div className="container max-w-2xl mx-auto py-12 px-4 animate-in fade-in zoom-in-95 duration-500">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 text-primary mb-6">
            <Trophy className="w-10 h-10" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Checkpoint Complete!</h1>
          <p className="text-muted-foreground text-lg">
            You scored {attemptResult.score * 100}%
          </p>
        </div>

        {attemptResult.mastery_deltas?.length > 0 && (
          <Card className="mb-8 border-primary/20 bg-primary/5">
            <CardHeader>
              <CardTitle className="text-lg">Mastery Updates</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {attemptResult.mastery_deltas.map((delta: any, i: number) => (
                <div key={i} className="flex justify-between items-center">
                  <span className="font-medium text-primary">{delta.concept_id.replace("con_", "").replace(/_/g, " ")}</span>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-muted-foreground line-through">
                      {(delta.old_score * 100).toFixed(0)}%
                    </Badge>
                    <ArrowRight className="w-4 h-4 text-muted-foreground" />
                    <Badge className="bg-primary hover:bg-primary">
                      {(delta.new_score * 100).toFixed(0)}%
                    </Badge>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        <div className="space-y-6">
          <h3 className="text-xl font-semibold">Review</h3>
          {checkpoint?.items.map((item, i) => {
            const feedback = attemptResult.feedback.find((f: any) => f.item_id === item.id);
            return (
              <Card key={item.id} className={feedback?.correct ? "border-green-500/50" : "border-red-500/50"}>
                <CardHeader>
                  <CardTitle className="text-base font-medium flex gap-3">
                    <span className="text-muted-foreground">{i + 1}.</span>
                    {item.question}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="p-4 rounded-md bg-muted/50 text-sm flex items-start gap-3">
                    {feedback?.correct ? (
                      <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0 mt-0.5" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <p className="font-medium mb-1">Your answer: <span className="font-normal text-muted-foreground">{responses[item.id]}</span></p>
                      {feedback?.explanation && (
                        <p className="text-muted-foreground">{feedback.explanation}</p>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
        
        <div className="mt-8 flex justify-center">
          <Button size="lg" onClick={() => router.push("/dashboard")}>
            Return to Dashboard
          </Button>
        </div>

        {(attemptResult as any).adaptation_event_id && (
          <AdaptationDialog 
            adaptationId={(attemptResult as any).adaptation_event_id} 
            onOpenChange={() => {}} 
          />
        )}
      </div>
    );
  }

  return (
    <div className="container max-w-2xl mx-auto py-12 px-4">
      <div className="text-center space-y-2 mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Knowledge Check</h1>
        <p className="text-muted-foreground">Answer these questions to lock in your progress.</p>
      </div>

      <div className="space-y-8">
        {checkpoint?.items?.map((item, index) => (
          <Card key={item.id} className="animate-in slide-in-from-bottom-4" style={{ animationDelay: `${index * 100}ms` }}>
            <CardHeader>
              <CardTitle className="text-lg leading-relaxed flex gap-3">
                <span className="text-primary">{index + 1}.</span>
                {item.question}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {item.options?.map((option) => (
                <label 
                  key={option}
                  className={`flex items-center gap-3 p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    responses[item.id] === option 
                      ? "border-primary bg-primary/5" 
                      : "border-transparent bg-muted hover:bg-muted/80"
                  }`}
                >
                  <input 
                    type="radio" 
                    name={`q-${item.id}`} 
                    value={option}
                    checked={responses[item.id] === option}
                    onChange={() => handleOptionSelect(item.id, option)}
                    className="w-4 h-4 text-primary"
                  />
                  <span className="font-medium">{option}</span>
                </label>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mt-10 flex justify-end">
        <Button 
          size="lg" 
          disabled={!isAllAnswered || submitMutation.isPending}
          onClick={() => submitMutation.mutate()}
        >
          {submitMutation.isPending ? "Submitting..." : "Submit Checkpoint"}
        </Button>
      </div>
    </div>
  );
}
