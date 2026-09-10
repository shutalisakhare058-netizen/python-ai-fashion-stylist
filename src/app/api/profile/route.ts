import { db } from "@/db";
import { users } from "@/db/schema";
import { eq } from "drizzle-orm";
import { getOrCreateProfile } from "@/lib/profile";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const row = await getOrCreateProfile();
    return Response.json({ profile: row });
  } catch {
    return Response.json({ error: "Failed to load profile." }, { status: 500 });
  }
}

export async function PUT(req: Request) {
  try {
    await getOrCreateProfile();
    const body = (await req.json().catch(() => ({}))) as Record<string, string>;
    const updated = await db
      .update(users)
      .set({
        name: (body.name ?? "").toString() || "Guest",
        stylePreferences: (body.stylePreferences ?? "").toString(),
        favoriteColors: (body.favoriteColors ?? "").toString(),
        dislikedColors: (body.dislikedColors ?? "").toString(),
        preferredOccasions: (body.preferredOccasions ?? "").toString(),
        clothingItems: (body.clothingItems ?? "").toString(),
      })
      .where(eq(users.id, 1))
      .returning();
    return Response.json({ profile: updated[0] });
  } catch {
    return Response.json({ error: "Failed to save profile." }, { status: 500 });
  }
}
