import Link from "next/link";
import NavBar from "@/components/NavBar";

const features = [
  {
    icon: "🤖",
    title: "AI Personal Stylist",
    desc: "Chat with StyleMate AI in plain language and get expert, friendly styling advice.",
  },
  {
    icon: "✨",
    title: "Personalized Recommendations",
    desc: "Outfits tailored to your occasion, wardrobe, season, and personal taste.",
  },
  {
    icon: "🎨",
    title: "Smart Color Matching",
    desc: "Discover color combinations that flatter your look and work with what you own.",
  },
  {
    icon: "💾",
    title: "Save Your Favorite Looks",
    desc: "Keep, rename, and revisit the outfits you love most, any time.",
  },
];

export default function Home() {
  return (
    <div className="min-h-screen">
      <NavBar />

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 -z-10 bg-gradient-to-br from-[#3b1d3a] via-[#5a2a52] to-[#e0577d]" />
        <div className="absolute -right-24 -top-24 -z-10 h-96 w-96 rounded-full bg-[#d8a24a]/30 blur-3xl" />
        <div className="mx-auto grid max-w-6xl gap-8 px-4 py-20 md:grid-cols-2 md:items-center md:py-28">
          <div className="text-white">
            <span className="inline-block rounded-full bg-white/15 px-3 py-1 text-xs font-semibold tracking-wide">
              👗 Powered by AI
            </span>
            <h1 className="mt-4 font-serif-display text-4xl font-bold leading-tight md:text-6xl">
              Your Personal AI Fashion Stylist
            </h1>
            <p className="mt-4 max-w-md text-lg text-white/85">
              Discover outfits that match your style, occasion and wardrobe —
              powered by AI.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/chat"
                className="rounded-full bg-white px-6 py-3 font-semibold text-[#3b1d3a] shadow-lg transition hover:scale-[1.03]"
              >
                Start Styling
              </Link>
              <Link
                href="/generate"
                className="rounded-full border border-white/60 px-6 py-3 font-semibold text-white transition hover:bg-white/10"
              >
                Generate Outfit
              </Link>
            </div>
          </div>

          <div className="relative">
            <div className="mx-auto max-w-sm rotate-2 rounded-3xl bg-white p-5 shadow-2xl">
              <div className="rounded-2xl bg-[#fbf7f2] p-4">
                <p className="text-xs font-semibold text-[#e0577d]">
                  STYLEMATE AI
                </p>
                <p className="mt-2 text-sm font-medium text-[#3b1d3a]">
                  &ldquo;What should I wear to an interview?&rdquo;
                </p>
                <div className="mt-3 space-y-1 rounded-xl bg-white p-3 text-xs text-[#241322] shadow">
                  <p className="font-bold">OUTFIT: Polished Professional</p>
                  <p>👔 White button-down shirt</p>
                  <p>👖 Tailored navy trousers</p>
                  <p>👞 Clean leather loafers</p>
                  <p>⌚ Minimal watch</p>
                  <p className="text-[#e0577d]">
                    ✨ Tidy fit signals confidence.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-4 py-16">
        <h2 className="text-center font-serif-display text-3xl font-bold text-[#3b1d3a]">
          Everything you need to look your best
        </h2>
        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((f) => (
            <div
              key={f.title}
              className="rounded-2xl border border-black/5 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-md"
            >
              <div className="grid h-12 w-12 place-items-center rounded-xl bg-gradient-to-br from-[#e0577d]/15 to-[#d8a24a]/15 text-2xl">
                {f.icon}
              </div>
              <h3 className="mt-4 text-lg font-bold text-[#3b1d3a]">
                {f.title}
              </h3>
              <p className="mt-2 text-sm text-[#241322]/70">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-6xl px-4 pb-20">
        <div className="rounded-3xl bg-gradient-to-r from-[#3b1d3a] to-[#e0577d] p-10 text-center text-white">
          <h2 className="font-serif-display text-3xl font-bold">
            Ready to elevate your wardrobe?
          </h2>
          <p className="mx-auto mt-2 max-w-lg text-white/85">
            Start a conversation with StyleMate AI and get personalized outfit
            ideas in seconds.
          </p>
          <Link
            href="/chat"
            className="mt-6 inline-block rounded-full bg-white px-8 py-3 font-semibold text-[#3b1d3a] shadow-lg transition hover:scale-[1.03]"
          >
            Start Styling Now
          </Link>
        </div>
      </section>

      <footer className="border-t border-black/5 py-6 text-center text-sm text-[#241322]/60">
        StyleMate AI · Built with Next.js · Python/FastAPI reference backend
        included in <code>python-backend/</code>
      </footer>
    </div>
  );
}
