"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { supabase } from "@/lib/supabase";
import { Button, Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle, Input, Label } from "@sarathi/ui";
import { useAuth } from "@/components/providers/Providers";
import apiClient from "@sarathi/api-client";
import Link from "next/link";

const registerSchema = z.object({
  email: z.string().email({ message: "Please enter a valid email address." }),
  password: z.string().min(6, { message: "Password must be at least 6 characters." }),
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const { session } = useAuth();
  const [globalError, setGlobalError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  useEffect(() => {
    if (session) {
      router.replace("/diagnostic");
    }
  }, [session, router]);

  if (session) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4 bg-gray-50 dark:bg-gray-950">
        <div className="animate-pulse flex flex-col items-center space-y-4">
          <div className="h-12 w-12 bg-gray-200 dark:bg-gray-800 rounded-full"></div>
          <div className="h-4 w-32 bg-gray-200 dark:bg-gray-800 rounded"></div>
        </div>
      </div>
    );
  }

  const onSubmit = async (data: RegisterFormValues) => {
    setGlobalError(null);
    try {
      const { data: authData, error } = await supabase.auth.signUp({
        email: data.email,
        password: data.password,
      });

      if (error) {
        // friendly mapped error copy
        if (error.message.includes("already registered")) {
          setGlobalError("An account with this email already exists. Please log in.");
        } else {
          setGlobalError(error.message);
        }
        return;
      }

      // after success call GET /me exactly once before routing on
      if (authData.session) {
        try {
          await apiClient.GET("/api/v1/me");
        } catch (meError) {
          console.error("Failed to fetch /me after registration", meError);
        }
      }

      router.push("/diagnostic");
    } catch (err: any) {
      setGlobalError(err.message || "An unexpected error occurred");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4 bg-gray-50 dark:bg-gray-950">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Create an Account</CardTitle>
          <CardDescription>
            Join Sarathi to start your adaptive learning journey.
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit(onSubmit)}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                {...register("email")}
                className={errors.email ? "border-red-500 focus-visible:ring-red-500" : ""}
              />
              {errors.email && (
                <p className="text-sm text-red-500 font-medium">{errors.email.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                {...register("password")}
                className={errors.password ? "border-red-500 focus-visible:ring-red-500" : ""}
              />
              {errors.password && (
                <p className="text-sm text-red-500 font-medium">{errors.password.message}</p>
              )}
            </div>
            {globalError && (
              <p className="text-sm text-red-500 font-medium">{globalError}</p>
            )}
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            <Button
              type="submit"
              className="w-full"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Creating account..." : "Sign Up"}
            </Button>
            <div className="text-sm text-center text-gray-500 dark:text-gray-400">
              Already have an account?{" "}
              <Link href="/login" className="text-blue-600 hover:underline">
                Sign In
              </Link>
            </div>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
