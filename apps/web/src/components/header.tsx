"use client";

import Link from "next/link";
import { env } from "@/lib/env";
import { HealthBadge } from "@/components/health-badge";
import { Button } from "@/components/ui/button";
import { FileText, Database, BarChart3 } from "lucide-react";

export function Header() {
  return (
    <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <FileText className="h-6 w-6" />
            <span className="font-bold">{env.NEXT_PUBLIC_APP_NAME}</span>
          </Link>
        </div>

        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <nav className="flex items-center space-x-2">
            <Button variant="ghost" size="sm" asChild>
              <Link href="/">
                <FileText className="h-4 w-4 mr-2" />
                Chat
              </Link>
            </Button>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/ingest">
                <Database className="h-4 w-4 mr-2" />
                Ingest
              </Link>
            </Button>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/evals">
                <BarChart3 className="h-4 w-4 mr-2" />
                Evals
              </Link>
            </Button>
          </nav>

          <div className="flex items-center space-x-2">
            <HealthBadge />
          </div>
        </div>
      </div>
    </header>
  );
}
