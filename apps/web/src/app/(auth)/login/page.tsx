"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { Button, Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle, Input, Label } from "@sarathi/ui";
import { useAuth } from "@/components/providers/Providers";

export default function LoginPage() {
  const router = useRouter();
  const { session } = useAuth();
  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  const handleAuth = async (isLogin: boolean) => {
    setLoading(true);
    setError(null);
    
    try {
      const { error } = isLogin
        ? await supabase.auth.signInWithPassword({ email, password })
        : await supabase.auth.signUp({ email, password });

      if (error) {
        setError(error.message);
      } else {
        router.push("/diagnostic");
      }
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4 bg-gray-50 dark:bg-gray-950">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Welcome to Sarathi</CardTitle>
          <CardDescription>
            Sign in to continue your learning journey.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input 
              id="email" 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com" 
              required 
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input 
              id="password" 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>
          {error && <p className="text-sm text-red-500 font-medium">{error}</p>}
        </CardContent>
        <CardFooter className="flex flex-col space-y-2">
          <Button 
            className="w-full" 
            onClick={() => handleAuth(true)} 
            disabled={loading || !email || !password}
          >
            {loading ? "Signing in..." : "Sign In"}
          </Button>
          <Button 
            variant="outline" 
            className="w-full" 
            onClick={() => handleAuth(false)} 
            disabled={loading || !email || !password}
          >
            Create Account
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
