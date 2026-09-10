import { db } from "@/db";
import { conversations } from "@/db/schema";
import { desc, eq } from "drizzle-orm";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const rows = await db
      .select()
      .from(conversations)
      .where(eq(conversations.userId, 1))
      .orderBy(desc(conversations.createdAt), desc(conversations.id));
    return Response.json({ chats: rows });
  } catch {
    return Response.json({ error: "Failed to load chats." }, { status: 500 });
  }
}

export async function POST() {
  try {
    const created = await db
      .insert(conversations)
      .values({ userId: 1, title: "New Chat" })
      .returning();
    return Response.json({ chat: created[0] });
  } catch {
    return Response.json({ error: "Failed to create chat." }, { status: 500 });
  }
}
