"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/components/providers/Providers";
import apiClient from "@sarathi/api-client";
import { Button, Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle, Skeleton } from "@sarathi/ui";
import type { components } from "@sarathi/api-types";

type LearnerProfileResponse = components["schemas"]["LearnerProfileResponse"];
type LearnerProfilePatchRequest = components["schemas"]["LearnerProfilePatchRequest"];

export default function ProfilePage() {
  const router = useRouter();
  const { session, isLoading: isAuthLoading } = useAuth();
  const queryClient = useQueryClient();

  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState<LearnerProfilePatchRequest>({});

  useEffect(() => {
    if (!isAuthLoading && !session) {
      router.push("/login");
    }
  }, [session, isAuthLoading, router]);

  const { data: profile, isLoading, error } = useQuery({
    queryKey: ["learnerProfile"],
    queryFn: async () => {
      const { data, error } = await apiClient.GET("/api/v1/profile/learner");
      if (error) throw error;
      return data;
    },
    enabled: !!session,
  });

  const mutation = useMutation({
    mutationFn: async (patch: LearnerProfilePatchRequest) => {
      const { data, error } = await apiClient.PATCH("/api/v1/profile/learner", {
        body: patch,
      });
      if (error) throw error;
      return data;
    },
    onSuccess: (newProfile) => {
      queryClient.setQueryData(["learnerProfile"], newProfile);
      setEditing(false);
    },
  });

  if (isAuthLoading || isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-2xl">
          <CardHeader>
            <Skeleton className="h-8 w-1/3" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-6 w-full" />
            <Skeleton className="h-6 w-5/6" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-2xl border-red-500">
          <CardHeader>
            <CardTitle className="text-red-500">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{(error as Error)?.message || "Failed to load profile"}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const handleEditToggle = () => {
    if (editing) {
      // cancel
      setEditing(false);
    } else {
      setFormData({
        pace: profile.pace,
        representation_pref: profile.representation_pref,
        scaffolding_pref: profile.scaffolding_pref,
        depth_pref: profile.depth_pref,
      });
      setEditing(true);
    }
  };

  const handleSave = () => {
    mutation.mutate(formData);
  };

  return (
    <div className="flex min-h-screen p-4 bg-gray-50 dark:bg-gray-950">
      <div className="w-full max-w-4xl mx-auto mt-8 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
            Your Learner Profile
          </h1>
          <Button variant={editing ? "outline" : "default"} onClick={handleEditToggle}>
            {editing ? "Cancel" : "Edit Preferences"}
          </Button>
        </div>
        
        <p className="text-gray-600 dark:text-gray-400">
          This profile was generated based on your diagnostic answers. Sarathi uses these settings to adapt the pacing, explanations, and structure of every lesson.
        </p>

        <Card>
          <CardHeader>
            <CardTitle>Learning Dimensions</CardTitle>
            <CardDescription>Adjust how Sarathi delivers content to you.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="font-semibold text-gray-800 dark:text-gray-200 block">Pace</label>
                {!editing ? (
                  <p className="text-gray-600 dark:text-gray-400 capitalize">{profile.pace}</p>
                ) : (
                  <select 
                    className="w-full p-2 border rounded dark:bg-gray-800 dark:border-gray-700"
                    value={formData.pace || ""}
                    onChange={(e) => setFormData({ ...formData, pace: e.target.value as any })}
                  >
                    <option value="deliberate">Deliberate</option>
                    <option value="standard">Standard</option>
                    <option value="fast">Fast</option>
                  </select>
                )}
              </div>

              <div className="space-y-2">
                <label className="font-semibold text-gray-800 dark:text-gray-200 block">Representation Preference</label>
                {!editing ? (
                  <p className="text-gray-600 dark:text-gray-400 capitalize">{profile.representation_pref?.replace("_", " ")}</p>
                ) : (
                  <select 
                    className="w-full p-2 border rounded dark:bg-gray-800 dark:border-gray-700"
                    value={formData.representation_pref || ""}
                    onChange={(e) => setFormData({ ...formData, representation_pref: e.target.value as any })}
                  >
                    <option value="concrete_first">Concrete First</option>
                    <option value="abstract_first">Abstract First</option>
                  </select>
                )}
              </div>

              <div className="space-y-2">
                <label className="font-semibold text-gray-800 dark:text-gray-200 block">Scaffolding Preference</label>
                {!editing ? (
                  <p className="text-gray-600 dark:text-gray-400 capitalize">{profile.scaffolding_pref?.replace("_", " ")}</p>
                ) : (
                  <select 
                    className="w-full p-2 border rounded dark:bg-gray-800 dark:border-gray-700"
                    value={formData.scaffolding_pref || ""}
                    onChange={(e) => setFormData({ ...formData, scaffolding_pref: e.target.value as any })}
                  >
                    <option value="worked_examples">Worked Examples</option>
                    <option value="guided_discovery">Guided Discovery</option>
                  </select>
                )}
              </div>

              <div className="space-y-2">
                <label className="font-semibold text-gray-800 dark:text-gray-200 block">Depth Preference</label>
                {!editing ? (
                  <p className="text-gray-600 dark:text-gray-400 capitalize">{profile.depth_pref?.replace("_", " ")}</p>
                ) : (
                  <select 
                    className="w-full p-2 border rounded dark:bg-gray-800 dark:border-gray-700"
                    value={formData.depth_pref || ""}
                    onChange={(e) => setFormData({ ...formData, depth_pref: e.target.value as any })}
                  >
                    <option value="breadth_survey">Breadth Survey</option>
                    <option value="depth_mastery">Depth Mastery</option>
                  </select>
                )}
              </div>
            </div>

          </CardContent>
          {editing && (
            <CardFooter className="flex justify-end border-t pt-4">
              <Button onClick={handleSave} disabled={mutation.isPending}>
                {mutation.isPending ? "Saving..." : "Save Preferences"}
              </Button>
            </CardFooter>
          )}
        </Card>
      </div>
    </div>
  );
}
