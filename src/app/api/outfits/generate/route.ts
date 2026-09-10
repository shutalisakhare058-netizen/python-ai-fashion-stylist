import { generateOutfit, type GenerateOutfitInput } from "@/lib/stylist";
import { getOrCreateProfile, toUserProfile } from "@/lib/profile";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  try {
    const body = (await req.json().catch(() => ({}))) as GenerateOutfitInput;
    const profileRow = await getOrCreateProfile();
    const { outfit, demo } = await generateOutfit(
      body || {},
      toUserProfile(profileRow)
    );
    return Response.json({ outfit, demo });
  } catch (err) {
    console.error("generate error", err);
    return Response.json(
      { error: "Failed to generate an outfit. Please try again." },
      { status: 500 }
    );
  }
}
