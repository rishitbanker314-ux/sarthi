"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/components/providers/Providers";
import apiClient from "@sarathi/api-client";
import { Button, Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle, Skeleton, Input, Label, Badge } from "@sarathi/ui";
import type { components } from "@sarathi/api-types";

type GoalUpdate = components["schemas"]["GoalUpdate"];

export default function GoalDetailPage() {
  const router = useRouter();
  const { id } = useParams() as { id: string };
  const { session, isLoading: isAuthLoading } = useAuth();
  const queryClient = useQueryClient();

  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState<GoalUpdate>({});

  useEffect(() => {
    if (!isAuthLoading && !session) {
      router.push("/login");
    }
  }, [session, isAuthLoading, router]);

  // Fetch goal
  const { data: goal, isLoading, error } = useQuery({
    queryKey: ["goal", id],
    queryFn: async () => {
      const { data, error } = await apiClient.GET("/api/v1/goals");
      if (error) throw error;
      const foundGoal = data?.data?.find((g: any) => g.id === id);
      if (!foundGoal) throw new Error("Goal not found");
      return foundGoal;
    },
    enabled: !!session && !!id,
  });

  // Patch goal
  const mutation = useMutation({
    mutationFn: async (patch: GoalUpdate) => {
      const { data, error } = await apiClient.PATCH("/api/v1/goals/{goal_id}", {
        params: { path: { goal_id: id } },
        body: patch,
      });
      if (error) throw error;
      return data;
    },
    onSuccess: (newGoal) => {
      queryClient.setQueryData(["goal", id], newGoal);
      setEditing(false);
    },
  });

  // Generate Plan
  const planMutation = useMutation({
    mutationFn: async () => {
      const { data, error } = await apiClient.POST("/api/v1/goals/{goal_id}/plan", {
        params: { path: { goal_id: id } },
      });
      if (error) throw error;
      return data;
    },
    onSuccess: (data) => {
      const resp = data as unknown as { id: string };
      if (resp?.id) {
        router.push(`/plan/generating/${resp.id}`);
      }
    },
  });

  if (isAuthLoading || isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Skeleton className="w-full max-w-2xl h-64" />
      </div>
    );
  }

  if (error || !goal) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-2xl border-red-500">
          <CardHeader>
            <CardTitle className="text-red-500">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{(error as Error)?.message || "Failed to load goal"}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const handleEditToggle = () => {
    if (editing) {
      setEditing(false);
    } else {
      setFormData({
        normalized_topic: goal.normalized_topic,
        target_level: goal.target_level as "beginner" | "intermediate" | "advanced",
        deadline: goal.deadline,
      });
      setEditing(true);
    }
  };

  const handleSave = () => {
    mutation.mutate(formData);
  };

  return (
    <div className="flex min-h-screen p-4 bg-gray-50 dark:bg-gray-950">
      <div className="w-full max-w-3xl mx-auto mt-8 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
            Goal Details
          </h1>
          <Button variant={editing ? "outline" : "default"} onClick={handleEditToggle}>
            {editing ? "Cancel" : "Edit Goal"}
          </Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Your Original Input</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="p-4 bg-gray-100 dark:bg-gray-800 rounded-md italic">
              "{goal.raw_input}"
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Interpretation</CardTitle>
            <CardDescription>This is how Sarathi understood your goal. Modify it if it missed the mark.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>Topic</Label>
              {!editing ? (
                <p className="text-lg font-medium">{goal.normalized_topic}</p>
              ) : (
                <Input 
                  value={formData.normalized_topic || ""} 
                  onChange={(e) => setFormData({ ...formData, normalized_topic: e.target.value })}
                />
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label>Target Level</Label>
                {!editing ? (
                  <div>
                    <Badge variant="secondary" className="capitalize">
                      {goal.target_level?.replace("_", " ") || "unknown"}
                    </Badge>
                  </div>
                ) : (
                  <select 
                    className="w-full p-2 border rounded dark:bg-gray-800 dark:border-gray-700"
                    value={formData.target_level || ""}
                    onChange={(e) => setFormData({ ...formData, target_level: e.target.value as any })}
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                )}
              </div>

              <div className="space-y-2">
                <Label>Deadline</Label>
                {!editing ? (
                  <p>{goal.deadline ? new Date(goal.deadline).toLocaleDateString() : "No deadline"}</p>
                ) : (
                  <Input 
                    type="date"
                    value={formData.deadline ? formData.deadline.split('T')[0] : ""} 
                    onChange={(e) => setFormData({ ...formData, deadline: e.target.value ? new Date(e.target.value).toISOString() : null })}
                  />
                )}
              </div>
            </div>
            
            {mutation.isError && (
              <div className="p-3 bg-red-100 text-red-700 rounded text-sm">
                {(mutation.error as Error)?.message || "Failed to update goal"}
              </div>
            )}
          </CardContent>
          
          {editing ? (
            <CardFooter className="flex justify-end border-t pt-4">
              <Button onClick={handleSave} disabled={mutation.isPending}>
                {mutation.isPending ? "Saving..." : "Save Changes"}
              </Button>
            </CardFooter>
          ) : (
            <CardFooter className="flex justify-end border-t pt-4">
              <Button 
                onClick={() => planMutation.mutate()} 
                disabled={planMutation.isPending}
              >
                {planMutation.isPending ? "Starting..." : goal.status === "planned" ? "Regenerate Plan" : "Generate Plan"}
              </Button>
            </CardFooter>
          )}
        </Card>
      </div>
    </div>
  );
}
