"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { useAuth } from "@/components/providers/Providers";
import apiClient from "@sarathi/api-client";
import { Button, Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@sarathi/ui";
import type { components } from "@sarathi/api-types";

type GoalCreate = components["schemas"]["GoalCreate"];

export default function NewGoalPage() {
  const router = useRouter();
  const { session, isLoading: isAuthLoading } = useAuth();
  const [rawInput, setRawInput] = useState("");

  useEffect(() => {
    if (!isAuthLoading && !session) {
      router.push("/login");
    }
  }, [session, isAuthLoading, router]);

  const mutation = useMutation({
    mutationFn: async (payload: GoalCreate) => {
      const { data, error } = await apiClient.POST("/api/v1/goals", {
        body: payload,
      });
      if (error) throw error;
      return data;
    },
    onSuccess: (data) => {
      if (data?.id) {
        router.push(`/goals/${data.id}`);
      }
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (rawInput.trim().length < 10) return;
    mutation.mutate({ raw_input: rawInput.trim() });
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4 bg-gray-50 dark:bg-gray-950">
      <Card className="w-full max-w-2xl">
        <form onSubmit={handleSubmit}>
          <CardHeader>
            <CardTitle className="text-2xl">What do you want to learn?</CardTitle>
            <CardDescription>
              Describe your goal in your own words. The more detail you provide, the better Sarathi can tailor the plan.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <textarea
                className="w-full min-h-[150px] p-4 border rounded-md dark:bg-gray-800 dark:border-gray-700 focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., I want to understand how transformers work in machine learning so I can build my own language model. I have a background in software engineering but no ML experience."
                value={rawInput}
                onChange={(e) => setRawInput(e.target.value)}
              />
              {rawInput.length > 0 && rawInput.length < 10 && (
                <p className="text-sm text-red-500">Please enter at least 10 characters.</p>
              )}
            </div>
            {mutation.isError && (
              <div className="p-3 bg-red-100 text-red-700 rounded text-sm">
                {(mutation.error as Error)?.message || "Failed to create goal"}
              </div>
            )}
          </CardContent>
          <CardFooter className="flex justify-end gap-3">
            <Button variant="outline" type="button" onClick={() => router.back()}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={rawInput.length < 10 || mutation.isPending}
            >
              {mutation.isPending ? "Analyzing..." : "Analyze Goal"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
