import { db } from "@/db";
import { conversations, messages } from "@/db/schema";
import { eq } from "drizzle-orm";

export const dynamic = "force-dynamic";

export async function DELETE(
  _req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const cid = Number(id);
    if (!cid) return Response.json({ error: "Invalid id." }, { status: 400 });
    await db.delete(messages).where(eq(messages.conversationId, cid));
    await db.delete(conversations).where(eq(conversations.id, cid));
    return Response.json({ ok: true });
  } catch {
    return Response.json({ error: "Failed to delete chat." }, { status: 500 });
  }
}

export async function PATCH(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const cid = Number(id);
    const body = (await req.json().catch(() => null)) as { title?: string } | null;
    const title = body?.title?.trim();
    if (!cid || !title)
      return Response.json({ error: "Invalid request." }, { status: 400 });
    const updated = await db
      .update(conversations)
      .set({ title })
      .where(eq(conversations.id, cid))
      .returning();
    return Response.json({ chat: updated[0] });
  } catch {
    return Response.json({ error: "Failed to rename chat." }, { status: 500 });
  }
}
