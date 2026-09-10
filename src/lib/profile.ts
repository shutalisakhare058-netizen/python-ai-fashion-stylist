import { db } from "@/db";
import { users } from "@/db/schema";
import { eq } from "drizzle-orm";
import type { UserProfile } from "@/lib/stylist";

// Single-profile app: always id = 1. Ensures a row exists.
export async function getOrCreateProfile() {
  const existing = await db.select().from(users).where(eq(users.id, 1)).limit(1);
  if (existing.length) return existing[0];
  const inserted = await db
    .insert(users)
    .values({ id: 1, name: "Guest" })
    .returning();
  return inserted[0];
}

export function toUserProfile(row: {
  name: string;
  stylePreferences: string;
  favoriteColors: string;
  dislikedColors: string;
  preferredOccasions: string;
  clothingItems: string;
}): UserProfile {
  return {
    name: row.name,
    stylePreferences: row.stylePreferences,
    favoriteColors: row.favoriteColors,
    dislikedColors: row.dislikedColors,
    preferredOccasions: row.preferredOccasions,
    clothingItems: row.clothingItems,
  };
}
