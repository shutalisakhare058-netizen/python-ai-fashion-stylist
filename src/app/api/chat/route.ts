import { db } from "@/db";
import { conversations, messages } from "@/db/schema";
import { and, eq, asc } from "drizzle-orm";
import { getChatReply, type ChatTurn } from "@/lib/stylist";
import { getOrCreateProfile, toUserProfile } from "@/lib/profile";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  try {
    const body = (await req.json().catch(() => null)) as {
      message?: string;
      conversation_id?: number;
    } | null;

    const message = body?.message?.trim();
    if (!message) {
      return Response.json(
        { error: "Message cannot be empty." },
        { status: 400 }
      );
    }

    const profileRow = await getOrCreateProfile();

    // Resolve or create conversation
    let conversationId = body?.conversation_id;
    if (conversationId) {
      const found = await db
        .select()
        .from(conversations)
        .where(eq(conversations.id, conversationId))
        .limit(1);
      if (!found.length) conversationId = undefined;
    }
    if (!conversationId) {
      const title = message.slice(0, 40) + (message.length > 40 ? "…" : "");
      const created = await db
        .insert(conversations)
        .values({ userId: 1, title })
        .returning();
      conversationId = created[0].id;
    }

    // Save user message
    await db.insert(messages).values({
      conversationId: conversationId!,
      role: "user",
      content: message,
    });

    // Build history for the AI
    const history = await db
      .select()
      .from(messages)
      .where(eq(messages.conversationId, conversationId!))
      .orderBy(asc(messages.createdAt), asc(messages.id));

    const turns: ChatTurn[] = history.map((h) => ({
      role: h.role === "assistant" ? "assistant" : "user",
      content: h.content,
    }));

    const { reply, demo } = await getChatReply(
      turns,
      toUserProfile(profileRow)
    );

    await db.insert(messages).values({
      conversationId: conversationId!,
      role: "assistant",
      content: reply,
    });

    return Response.json({ reply, conversation_id: conversationId, demo });
  } catch (err) {
    console.error("chat error", err);
    return Response.json(
      { error: "Something went wrong while generating a reply. Please try again." },
      { status: 500 }
    );
  }
}

// Fetch messages for a conversation
export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const id = Number(searchParams.get("conversation_id"));
    if (!id) return Response.json({ messages: [] });
    const rows = await db
      .select()
      .from(messages)
      .where(and(eq(messages.conversationId, id)))
      .orderBy(asc(messages.createdAt), asc(messages.id));
    return Response.json({ messages: rows });
  } catch {
    return Response.json({ error: "Failed to load messages." }, { status: 500 });
  }
}
