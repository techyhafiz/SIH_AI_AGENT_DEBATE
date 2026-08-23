import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Consensus Arena | SIH Multi-Model Workspace",
  description: "Collaborative multi-LLM debate, stress-testing, and consensus synthesis platform for Smart India Hackathon.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light">
      <body className="bg-[#f8fafc] text-[#0f172a] min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
