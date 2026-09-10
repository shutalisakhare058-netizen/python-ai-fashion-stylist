"use client";

export interface OutfitData {
  outfit: string;
  top: string;
  bottom: string;
  dress?: string;
  shoes: string;
  accessories: string;
  bag: string;
  layering?: string;
  styleTip: string;
}

const rows: { key: keyof OutfitData; icon: string; label: string }[] = [
  { key: "top", icon: "👕", label: "Top" },
  { key: "bottom", icon: "👖", label: "Bottom" },
  { key: "dress", icon: "👗", label: "Dress / Alt" },
  { key: "shoes", icon: "👞", label: "Shoes" },
  { key: "accessories", icon: "⌚", label: "Accessories" },
  { key: "bag", icon: "👜", label: "Bag" },
  { key: "layering", icon: "🧥", label: "Layering" },
];

export default function OutfitCard({
  data,
  onSave,
  onAnother,
  onAsk,
  saving,
}: {
  data: OutfitData;
  onSave?: () => void;
  onAnother?: () => void;
  onAsk?: () => void;
  saving?: boolean;
}) {
  return (
    <div className="overflow-hidden rounded-2xl border border-black/5 bg-white shadow-sm">
      <div className="bg-gradient-to-r from-[#3b1d3a] to-[#e0577d] px-5 py-4 text-white">
        <p className="text-xs font-semibold uppercase tracking-wide text-white/70">
          Outfit
        </p>
        <h3 className="font-serif-display text-xl font-bold">{data.outfit}</h3>
      </div>
      <div className="divide-y divide-black/5 px-5">
        {rows
          .filter((r) => data[r.key])
          .map((r) => (
            <div key={r.key} className="flex gap-3 py-2.5 text-sm">
              <span className="text-lg">{r.icon}</span>
              <span className="w-24 shrink-0 font-semibold text-[#3b1d3a]">
                {r.label}
              </span>
              <span className="text-[#241322]/80">{data[r.key]}</span>
            </div>
          ))}
      </div>
      <div className="bg-[#fbf7f2] px-5 py-3 text-sm">
        <span className="font-semibold text-[#e0577d]">✨ Style Tip: </span>
        <span className="text-[#241322]/80">{data.styleTip}</span>
      </div>
      {(onSave || onAnother || onAsk) && (
        <div className="flex flex-wrap gap-2 px-5 py-4">
          {onSave && (
            <button
              onClick={onSave}
              disabled={saving}
              className="rounded-full bg-[#3b1d3a] px-4 py-2 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
            >
              {saving ? "Saving…" : "💾 Save Outfit"}
            </button>
          )}
          {onAnother && (
            <button
              onClick={onAnother}
              className="rounded-full border border-[#3b1d3a]/30 px-4 py-2 text-sm font-semibold text-[#3b1d3a] transition hover:bg-[#3b1d3a]/5"
            >
              🔁 Try Another
            </button>
          )}
          {onAsk && (
            <button
              onClick={onAsk}
              className="rounded-full border border-[#e0577d]/40 px-4 py-2 text-sm font-semibold text-[#e0577d] transition hover:bg-[#e0577d]/5"
            >
              💬 Ask AI
            </button>
          )}
        </div>
      )}
    </div>
  );
}
