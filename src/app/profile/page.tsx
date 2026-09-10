"use client";

import { useEffect, useState } from "react";
import NavBar from "@/components/NavBar";

interface Profile {
  name: string;
  stylePreferences: string;
  favoriteColors: string;
  dislikedColors: string;
  preferredOccasions: string;
  clothingItems: string;
}

const EMPTY: Profile = {
  name: "",
  stylePreferences: "",
  favoriteColors: "",
  dislikedColors: "",
  preferredOccasions: "",
  clothingItems: "",
};

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile>(EMPTY);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    fetch("/api/profile")
      .then((r) => r.json())
      .then((d) => {
        if (d.profile) setProfile({ ...EMPTY, ...d.profile });
        setLoading(false);
      });
  }, []);

  const update = (k: keyof Profile, v: string) =>
    setProfile((p) => ({ ...p, [k]: v }));

  const save = async () => {
    setSaving(true);
    setMsg("");
    try {
      const res = await fetch("/api/profile", {
        method: "PUT",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(profile),
      });
      if (!res.ok) throw new Error();
      setMsg("Profile saved! ✅ StyleMate AI will now personalize your looks.");
    } catch {
      setMsg("Could not save profile. Try again.");
    } finally {
      setSaving(false);
    }
  };

  const fields: {
    key: keyof Profile;
    label: string;
    placeholder: string;
    area?: boolean;
  }[] = [
    { key: "name", label: "Name", placeholder: "Your name" },
    {
      key: "stylePreferences",
      label: "Preferred Fashion Style",
      placeholder: "e.g. Minimal, streetwear, classic",
    },
    {
      key: "favoriteColors",
      label: "Favorite Colors",
      placeholder: "e.g. Navy, cream, olive",
    },
    {
      key: "dislikedColors",
      label: "Colors You Don't Prefer",
      placeholder: "e.g. Neon yellow",
    },
    {
      key: "preferredOccasions",
      label: "Preferred Occasions",
      placeholder: "e.g. College, casual outings",
    },
    {
      key: "clothingItems",
      label: "Clothing Items You Own",
      placeholder: "e.g. white shirt, blue jeans, black blazer, sneakers",
      area: true,
    },
  ];

  return (
    <div className="min-h-screen">
      <NavBar />
      <div className="mx-auto max-w-2xl px-4 py-8">
        <h1 className="font-serif-display text-3xl font-bold text-[#3b1d3a]">
          Your Style Profile
        </h1>
        <p className="mt-1 text-sm text-[#241322]/60">
          Tell us about your taste so recommendations feel truly personal. We
          only ask about clothing and preferences — never your body or
          appearance.
        </p>

        {loading ? (
          <p className="mt-8 text-sm text-[#241322]/50">Loading…</p>
        ) : (
          <div className="mt-6 grid gap-4 rounded-2xl border border-black/5 bg-white p-5 shadow-sm">
            {fields.map((f) => (
              <div key={f.key}>
                <label className="mb-1 block text-sm font-semibold text-[#3b1d3a]">
                  {f.label}
                </label>
                {f.area ? (
                  <textarea
                    value={profile[f.key]}
                    onChange={(e) => update(f.key, e.target.value)}
                    rows={3}
                    placeholder={f.placeholder}
                    className="w-full resize-none rounded-xl border border-black/10 px-3 py-2.5 text-sm outline-none focus:border-[#e0577d]"
                  />
                ) : (
                  <input
                    value={profile[f.key]}
                    onChange={(e) => update(f.key, e.target.value)}
                    placeholder={f.placeholder}
                    className="w-full rounded-xl border border-black/10 px-3 py-2.5 text-sm outline-none focus:border-[#e0577d]"
                  />
                )}
              </div>
            ))}
            <button
              onClick={save}
              disabled={saving}
              className="rounded-xl bg-[#3b1d3a] px-4 py-3 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
            >
              {saving ? "Saving…" : "Save Profile"}
            </button>
            {msg && (
              <p className="text-sm font-semibold text-[#3b1d3a]">{msg}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
