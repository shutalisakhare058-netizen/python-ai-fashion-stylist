import {
  pgTable,
  serial,
  text,
  integer,
  timestamp,
  jsonb,
} from "drizzle-orm/pg-core";

// User profile (single-profile app for simplicity; id defaults to 1)
export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  name: text("name").notNull().default("Guest"),
  stylePreferences: text("style_preferences").notNull().default(""),
  favoriteColors: text("favorite_colors").notNull().default(""),
  dislikedColors: text("disliked_colors").notNull().default(""),
  preferredOccasions: text("preferred_occasions").notNull().default(""),
  clothingItems: text("clothing_items").notNull().default(""),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const conversations = pgTable("conversations", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").notNull().default(1),
  title: text("title").notNull().default("New Chat"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const messages = pgTable("messages", {
  id: serial("id").primaryKey(),
  conversationId: integer("conversation_id").notNull(),
  role: text("role").notNull(), // "user" | "assistant"
  content: text("content").notNull(),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const savedOutfits = pgTable("saved_outfits", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").notNull().default(1),
  name: text("name").notNull(),
  outfitData: jsonb("outfit_data").notNull(),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export type User = typeof users.$inferSelect;
export type Conversation = typeof conversations.$inferSelect;
export type Message = typeof messages.$inferSelect;
export type SavedOutfit = typeof savedOutfits.$inferSelect;
