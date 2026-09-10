import { db } from "@/db";
import { savedOutfits } from "@/db/schema";
import { desc, eq } from "drizzle-orm";

export const dynamic = "force-dynamic";

// GET /api/outfits -> saved outfits
export async function GET() {
  try {
    const rows = await db
      .select()
      .from(savedOutfits)
      .where(eq(savedOutfits.userId, 1))
      .orderBy(desc(savedOutfits.createdAt), desc(savedOutfits.id));
    return Response.json({ outfits: rows });
  } catch {
    return Response.json({ error: "Failed to load outfits." }, { status: 500 });
  }
}

// POST /api/outfits -> save an outfit
export async function POST(req: Request) {
  try {
    const body = (await req.json().catch(() => null)) as {
      name?: string;
      outfit_data?: unknown;
    } | null;
    if (!body?.outfit_data) {
      return Response.json({ error: "Missing outfit data." }, { status: 400 });
    }
    const name = body.name?.trim() || "My Outfit";
    const created = await db
      .insert(savedOutfits)
      .values({ userId: 1, name, outfitData: body.outfit_data })
      .returning();
    return Response.json({ outfit: created[0] });
  } catch {
    return Response.json({ error: "Failed to save outfit." }, { status: 500 });
  }
}
