import { db } from "@/db";
import { savedOutfits } from "@/db/schema";
import { eq } from "drizzle-orm";

export const dynamic = "force-dynamic";

export async function DELETE(
  _req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const oid = Number(id);
    if (!oid) return Response.json({ error: "Invalid id." }, { status: 400 });
    await db.delete(savedOutfits).where(eq(savedOutfits.id, oid));
    return Response.json({ ok: true });
  } catch {
    return Response.json({ error: "Failed to delete outfit." }, { status: 500 });
  }
}

export async function PATCH(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const oid = Number(id);
    const body = (await req.json().catch(() => null)) as { name?: string } | null;
    const name = body?.name?.trim();
    if (!oid || !name)
      return Response.json({ error: "Invalid request." }, { status: 400 });
    const updated = await db
      .update(savedOutfits)
      .set({ name })
      .where(eq(savedOutfits.id, oid))
      .returning();
    return Response.json({ outfit: updated[0] });
  } catch {
    return Response.json({ error: "Failed to rename outfit." }, { status: 500 });
  }
}
