"use client";

import { useState } from "react";
import NavBar from "@/components/NavBar";
import OutfitCard, { type OutfitData } from "@/components/OutfitCard";

export default function GeneratePage() {
  const [form, setForm] = useState({
    occasion: "",
    season: "",
    style: "",
    clothes: "",
    colors: "",
  });
  const [outfit, setOutfit] = useState<OutfitData | null>(null);
  const [demo, setDemo] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [savedMsg, setSavedMsg] = useState("");

  const update = (k: string, v: string) =>
    setForm((f) => ({ ...f, [k]: v }));

  const generate = async () => {
    setLoading(true);
    setError("");
    setSavedMsg("");
    try {
      const res = await fetch("/api/outfits/generate", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to generate outfit");
      setOutfit(data.outfit);
      setDemo(data.demo);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const save = async () => {
    if (!outfit) return;
    setSaving(true);
    setSavedMsg("");
    try {
      const res = await fetch("/api/outfits", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ name: outfit.outfit, outfit_data: outfit }),
      });
      if (!res.ok) throw new Error();
      setSavedMsg("Saved to your outfits! ✅");
    } catch {
      setSavedMsg("Could not save. Try again.");
    } finally {
      setSaving(false);
    }
  };

  const fields: { key: keyof typeof form; label: string; placeholder: string }[] =
    [
      { key: "occasion", label: "Occasion", placeholder: "e.g. Job interview" },
      { key: "season", label: "Weather / Season", placeholder: "e.g. Cool autumn" },
      { key: "style", label: "Fashion Style", placeholder: "e.g. Smart casual" },
      { key: "colors", label: "Preferred Colors", placeholder: "e.g. Navy, cream" },
    ];

  return (
    <div className="min-h-screen">
      <NavBar />
      <div className="mx-auto max-w-5xl px-4 py-8">
        <h1 className="font-serif-display text-3xl font-bold text-[#3b1d3a]">
          Generate an Outfit
        </h1>
        <p className="mt-1 text-sm text-[#241322]/60">
          Tell us the details and StyleMate AI will assemble a complete look.
        </p>

        <div className="mt-6 grid gap-6 md:grid-cols-2">
          {/* Form */}
          <div className="rounded-2xl border border-black/5 bg-white p-5 shadow-sm">
            <div className="grid gap-4">
              {fields.map((f) => (
                <div key={f.key}>
                  <label className="mb-1 block text-sm font-semibold text-[#3b1d3a]">
                    {f.label}
                  </label>
                  <input
                    value={form[f.key]}
                    onChange={(e) => update(f.key, e.target.value)}
                    placeholder={f.placeholder}
                    className="w-full rounded-xl border border-black/10 px-3 py-2.5 text-sm outline-none focus:border-[#e0577d]"
                  />
                </div>
              ))}
              <div>
                <label className="mb-1 block text-sm font-semibold text-[#3b1d3a]">
                  Available Clothes
                </label>
                <textarea
                  value={form.clothes}
                  onChange={(e) => update("clothes", e.target.value)}
                  rows={3}
                  placeholder="e.g. white shirt, blue jeans, black blazer, white sneakers"
                  className="w-full resize-none rounded-xl border border-black/10 px-3 py-2.5 text-sm outline-none focus:border-[#e0577d]"
                />
              </div>
              <button
                onClick={generate}
                disabled={loading}
                className="rounded-xl bg-gradient-to-r from-[#3b1d3a] to-[#e0577d] px-4 py-3 text-sm font-semibold text-white transition hover:opacity-95 disabled:opacity-50"
              >
                {loading ? "Styling your look…" : "✨ Generate Outfit"}
              </button>
              {error && (
                <p className="text-sm text-red-600">⚠️ {error}</p>
              )}
            </div>
          </div>

          {/* Result */}
          <div>
            {!outfit && !loading && (
              <div className="grid h-full min-h-64 place-items-center rounded-2xl border border-dashed border-black/15 bg-white/50 p-6 text-center text-sm text-[#241322]/50">
                Your generated outfit will appear here.
              </div>
            )}
            {loading && (
              <div className="grid h-full min-h-64 place-items-center rounded-2xl border border-black/5 bg-white p-6 text-center text-sm text-[#241322]/50">
                <div className="animate-pulse">Assembling your outfit… 👗</div>
              </div>
            )}
            {outfit && (
              <div className="space-y-3">
                {demo && (
                  <p className="rounded-lg bg-[#d8a24a]/15 px-3 py-2 text-xs font-semibold text-[#8a6412]">
                    🎭 DEMO MODE — set ANTHROPIC_API_KEY for live AI results.
                  </p>
                )}
                <OutfitCard
                  data={outfit}
                  onSave={save}
                  onAnother={generate}
                  saving={saving}
                />
                {savedMsg && (
                  <p className="text-sm font-semibold text-[#3b1d3a]">
                    {savedMsg}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
