import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Portfolio Builder",
  description: "Build your stock portfolio dynamically",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body
        className={`bg-gray-100 text-gray-900 min-h-screen ${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <div className="max-w-4xl mx-auto p-6">{children}</div>
      </body>
    </html>
  );
}
