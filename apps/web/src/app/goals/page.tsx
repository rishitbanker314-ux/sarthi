"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/components/providers/Providers";
import apiClient from "@sarathi/api-client";
import { Button, Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle, Skeleton } from "@sarathi/ui";

export default function GoalsPage() {
  const router = useRouter();
  const { session, isLoading: isAuthLoading } = useAuth();

  useEffect(() => {
    if (!isAuthLoading && !session) {
      router.push("/login");
    }
  }, [session, isAuthLoading, router]);

  const { data, isLoading, error } = useQuery({
    queryKey: ["goals"],
    queryFn: async () => {
      const { data, error } = await apiClient.GET("/api/v1/goals");
      if (error) throw error;
      return data;
    },
    enabled: !!session,
  });

  if (isAuthLoading || isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4 bg-gray-50 dark:bg-gray-950">
        <div className="w-full max-w-4xl space-y-4">
          <Skeleton className="h-10 w-1/3" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map(i => <Skeleton key={i} className="h-32 w-full" />)}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-2xl border-red-500">
          <CardHeader>
            <CardTitle className="text-red-500">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{(error as Error)?.message || "Failed to load goals"}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const goals = data?.data || [];

  return (
    <div className="flex min-h-screen p-4 bg-gray-50 dark:bg-gray-950">
      <div className="w-full max-w-5xl mx-auto mt-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
              Your Goals
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Select an existing goal or create a new one to generate a personalized learning plan.
            </p>
          </div>
          <Button onClick={() => router.push("/goals/new")}>
            Create New Goal
          </Button>
        </div>

        {goals.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <h2 className="text-xl font-semibold mb-2">No goals yet</h2>
              <p className="text-gray-500 mb-6">Start your learning journey by setting a new goal.</p>
              <Button onClick={() => router.push("/goals/new")}>Create Your First Goal</Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {goals?.map((goal: any) => (
              <Card 
                key={goal.id} 
                className="cursor-pointer hover:border-blue-500 transition-colors"
                onClick={() => router.push(`/goals/${goal.id}`)}
              >
                <CardHeader>
                  <CardTitle className="text-lg line-clamp-2">
                    {goal.normalized_topic || goal.raw_input || "Untitled Goal"}
                  </CardTitle>
                  <CardDescription>
                    {goal.target_level ? `Target: ${goal.target_level.replace("_", " ")}` : "Analyzing..."}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-gray-500">
                    {goal.active_plan_id ? "Plan Ready" : "Requires Plan"}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
