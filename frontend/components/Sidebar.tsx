"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/requests", label: "Requests" },
  { href: "/customers", label: "Customers" },
  { href: "/approvals", label: "Approvals" },
  { href: "/audit-logs", label: "Audit Logs" },
];

export default function Sidebar() {
  const pathname = usePathname();

  function isActive(href: string) {
    if (href === "/") {
      return pathname === "/";
    }

    return pathname === href || pathname.startsWith(`${href}/`);
  }

  return (
    <aside className="w-64 border-r border-zinc-200 bg-white p-6">
      <div className="mb-10">
        <h1 className="text-xl font-bold text-zinc-900">
          AI Automation
        </h1>

        <p className="mt-1 text-sm text-zinc-500">
          Business Operations
        </p>
      </div>

      <nav className="space-y-2">
        {LINKS.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            aria-current={isActive(link.href) ? "page" : undefined}
            className={`block rounded-lg px-4 py-2.5 text-sm font-medium ${
              isActive(link.href)
                ? "bg-zinc-900 text-white"
                : "text-zinc-600 hover:bg-zinc-100"
            }`}
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
