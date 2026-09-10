"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Home" },
  { href: "/chat", label: "Chat" },
  { href: "/generate", label: "Generate Outfit" },
  { href: "/outfits", label: "Saved Outfits" },
  { href: "/profile", label: "Profile" },
];

export default function NavBar() {
  const pathname = usePathname();
  return (
    <header className="sticky top-0 z-40 border-b border-black/5 bg-[#fbf7f2]/90 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2">
          <span className="grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-[#e0577d] to-[#d8a24a] text-lg">
            👗
          </span>
          <span className="font-serif-display text-xl font-bold text-[#3b1d3a]">
            StyleMate<span className="text-[#e0577d]"> AI</span>
          </span>
        </Link>
        <div className="flex items-center gap-1 text-sm">
          {links.map((l) => {
            const active =
              l.href === "/" ? pathname === "/" : pathname.startsWith(l.href);
            return (
              <Link
                key={l.href}
                href={l.href}
                className={`rounded-full px-3 py-1.5 font-medium transition ${
                  active
                    ? "bg-[#3b1d3a] text-white"
                    : "text-[#3b1d3a] hover:bg-[#3b1d3a]/10"
                }`}
              >
                {l.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </header>
  );
}
