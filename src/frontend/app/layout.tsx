import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import "./globals.css"
import { Sidebar } from "@/components/sidebar"
import { Suspense } from "react"
import { ThemeProvider } from "@/components/theme-provider"

export const metadata: Metadata = {
  title: "Antagonist",
  description: "Post-mortem system for anomaly detection",
    generator: 'v0.app'
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`font-sans ${GeistSans.variable} ${GeistMono.variable}`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          <Suspense fallback={<div>Loading...</div>}>
            <div className="flex h-screen">
              <Sidebar />
              <main className="flex-1 overflow-auto">{children}</main>
            </div>
          </Suspense>
        </ThemeProvider>
      </body>
    </html>
  )
}
