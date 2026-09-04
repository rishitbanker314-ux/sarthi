import type { Metadata } from "next";
import { Inter, Lora } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers/Providers";
import { ThemeToggle } from "@/components/ThemeToggle";
import { ServiceWorkerRegistration } from "@/components/ServiceWorkerRegistration";

const fontSans = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

const fontSerif = Lora({
  variable: "--font-serif",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Sarathi | Adaptive AI Tutor",
  description: "An intelligent tutor that adapts to your learning style in real-time.",
  openGraph: {
    title: "Sarathi | Adaptive AI Tutor",
    description: "An intelligent tutor that adapts to your learning style in real-time.",
    type: "website",
    locale: "en_US",
    siteName: "Sarathi"
  },
  twitter: {
    card: "summary_large_image",
    title: "Sarathi | Adaptive AI Tutor",
    description: "An intelligent tutor that adapts to your learning style in real-time.",
  },
  robots: {
    index: true,
    follow: true
  }
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en" 
      className={`${fontSans.variable} ${fontSerif.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{
          __html: `
            try {
              if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
                document.documentElement.classList.add('dark')
                document.documentElement.style.colorScheme = 'dark'
              } else {
                document.documentElement.classList.remove('dark')
                document.documentElement.style.colorScheme = 'light'
              }
            } catch (_) {}
          `
        }} />
      </head>
      <body className="min-h-full flex flex-col font-sans">
        <Providers>
          <ServiceWorkerRegistration />
          <header className="w-full p-4 flex justify-end border-b bg-background">
            <ThemeToggle />
          </header>
          {children}
        </Providers>
      </body>
    </html>
  );
}
