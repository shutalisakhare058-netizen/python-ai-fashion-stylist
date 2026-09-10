"use client";

import { useCallback, useEffect, useState } from "react";
import NavBar from "@/components/NavBar";
import OutfitCard, { type OutfitData } from "@/components/OutfitCard";

interface SavedOutfit {
  id: number;
  name: string;
  outfitData: OutfitData;
}

export default function OutfitsPage() {
  const [outfits, setOutfits] = useState<SavedOutfit[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    const res = await fetch("/api/outfits");
    const data = await res.json();
    setOutfits(data.outfits || []);
    setLoading(false);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const remove = async (id: number) => {
    await fetch(`/api/outfits/${id}`, { method: "DELETE" });
    load();
  };

  const rename = async (id: number, current: string) => {
    const name = window.prompt("Rename outfit:", current);
    if (!name) return;
    await fetch(`/api/outfits/${id}`, {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ name }),
    });
    load();
  };

  return (
    <div className="min-h-screen">
      <NavBar />
      <div className="mx-auto max-w-5xl px-4 py-8">
        <h1 className="font-serif-display text-3xl font-bold text-[#3b1d3a]">
          Saved Outfits
        </h1>
        <p className="mt-1 text-sm text-[#241322]/60">
          Your favorite looks, ready whenever you need them.
        </p>

        {loading ? (
          <p className="mt-8 text-sm text-[#241322]/50">Loading…</p>
        ) : outfits.length === 0 ? (
          <div className="mt-8 rounded-2xl border border-dashed border-black/15 bg-white/50 p-10 text-center text-sm text-[#241322]/50">
            No saved outfits yet. Generate one and hit{" "}
            <span className="font-semibold">Save Outfit</span>!
          </div>
        ) : (
          <div className="mt-6 grid gap-6 md:grid-cols-2">
            {outfits.map((o) => (
              <div key={o.id} className="space-y-2">
                <OutfitCard data={{ ...o.outfitData, outfit: o.name }} />
                <div className="flex gap-2">
                  <button
                    onClick={() => rename(o.id, o.name)}
                    className="rounded-full border border-[#3b1d3a]/30 px-4 py-1.5 text-xs font-semibold text-[#3b1d3a] transition hover:bg-black/5"
                  >
                    ✏️ Rename
                  </button>
                  <button
                    onClick={() => remove(o.id)}
                    className="rounded-full border border-red-300 px-4 py-1.5 text-xs font-semibold text-red-600 transition hover:bg-red-50"
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
