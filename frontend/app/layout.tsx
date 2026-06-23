import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Recruiter Intelligence Console",
  description: "EvidenceGraph Ranker product console"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
