import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Scrapbox RAG",
  description: "Search your Scrapbox knowledge with Local LLM",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja" data-theme="cupcake">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
