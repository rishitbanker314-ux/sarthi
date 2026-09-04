import Link from "next/link";
import { Button } from "@sarathi/ui";
import { Compass, BookOpen, BrainCircuit } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <main className="flex-1">
        <section className="w-full py-24 md:py-32 lg:py-48 flex items-center justify-center">
          <div className="container px-4 md:px-6 flex flex-col items-center text-center max-w-4xl mx-auto space-y-8">
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl">
              An intelligent tutor that <span className="text-primary">adapts to you.</span>
            </h1>
            <p className="max-w-[700px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
              Sarathi builds custom learning paths and adapts them in real-time as you learn, struggle, and master new concepts.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <Button asChild size="lg" className="h-12 px-8 text-base">
                <Link href="/register">Get Started</Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="h-12 px-8 text-base">
                <Link href="/login">Sign In</Link>
              </Button>
            </div>
          </div>
        </section>

        <section className="w-full py-12 md:py-24 lg:py-32 bg-muted/40 border-y">
          <div className="container px-4 md:px-6 mx-auto">
            <div className="grid gap-12 sm:grid-cols-2 md:grid-cols-3 max-w-5xl mx-auto">
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="p-4 bg-primary/10 rounded-full">
                  <Compass className="w-8 h-8 text-primary" />
                </div>
                <h3 className="text-xl font-bold">Personalized Paths</h3>
                <p className="text-muted-foreground">
                  Define your learning goal and Sarathi creates a structured, multi-module plan tailored exactly to your baseline.
                </p>
              </div>
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="p-4 bg-primary/10 rounded-full">
                  <BookOpen className="w-8 h-8 text-primary" />
                </div>
                <h3 className="text-xl font-bold">Active Learning</h3>
                <p className="text-muted-foreground">
                  Lessons stream in real-time. Built-in checkpoints ensure you're actively engaging with the material, not just reading.
                </p>
              </div>
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="p-4 bg-primary/10 rounded-full">
                  <BrainCircuit className="w-8 h-8 text-primary" />
                </div>
                <h3 className="text-xl font-bold">Adaptive Loop</h3>
                <p className="text-muted-foreground">
                  Struggling with a concept? Sarathi identifies the gap and rewires your upcoming path to reinforce fundamentals.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>
      
      <footer className="w-full border-t py-6">
        <div className="container px-4 md:px-6 flex flex-col md:flex-row items-center justify-between text-sm text-muted-foreground mx-auto">
          <p>© 2026 Sarathi. All rights reserved.</p>
          <div className="flex items-center gap-4 mt-4 md:mt-0">
            <Link href="/terms" className="hover:underline">Terms</Link>
            <Link href="/privacy" className="hover:underline">Privacy</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
