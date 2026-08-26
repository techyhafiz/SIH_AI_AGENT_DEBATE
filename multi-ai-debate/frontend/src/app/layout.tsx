import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Consensus Arena | SIH Multi-Model Workspace",
  description: "Collaborative multi-LLM debate, stress-testing, and consensus synthesis platform for Smart India Hackathon.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light">
      <body className="min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
