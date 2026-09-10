// StyleMate AI — chat frontend logic
let activeId = null;

const QUICK = [
  ["College Outfit", "What should I wear to college tomorrow?"],
  ["Party Outfit", "Suggest an outfit for a birthday party."],
  ["Interview Outfit", "I need an outfit for a job interview."],
  ["Casual Outfit", "Suggest a comfy casual outfit for the weekend."],
  ["Travel Outfit", "What should I wear for a long travel day?"],
  ["Formal Outfit", "Help me put together a formal evening outfit."],
  ["Date/Function Outfit", "Suggest a stylish outfit for a dinner date."],
  ["Match My Clothes", "I have a black top and blue jeans. How can I style them?"],
];

const $ = (id) => document.getElementById(id);

function renderQuick() {
  $("quick-prompts").innerHTML = QUICK.map(
    ([label, p]) => `<button class="qp" data-p="${p}">${label}</button>`
  ).join("");
  document.querySelectorAll(".qp").forEach((b) =>
    b.addEventListener("click", () => send(b.dataset.p))
  );
}

function addBubble(role, text) {
  const div = document.createElement("div");
  div.className = "bubble " + role;
  div.textContent = text;
  $("messages").appendChild(div);
  $("messages").scrollTop = $("messages").scrollHeight;
  return div;
}

async function send(text) {
  text = (text || $("input").value).trim();
  if (!text) return;
  $("input").value = "";
  addBubble("user", text);
  const typing = addBubble("assistant", "…");
  typing.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
  try {
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, conversation_id: activeId }),
    });
    const data = await r.json();
    typing.remove();
    if (!r.ok) throw new Error(data.detail || "Request failed");
    addBubble("assistant", data.reply);
    activeId = data.conversation_id;
    loadChats();
  } catch (e) {
    typing.remove();
    addBubble("assistant", "⚠️ " + e.message + " Please try again.");
  }
}

async function loadChats() {
  const r = await fetch("/api/chats");
  const chats = await r.json();
  $("chat-list").innerHTML = chats
    .map(
      (c) =>
        `<div class="chat-item"><span data-id="${c.id}">💬 ${c.title}</span>
         <button data-del="${c.id}">🗑️</button></div>`
    )
    .join("");
  document.querySelectorAll("[data-id]").forEach((el) =>
    el.addEventListener("click", () => openChat(+el.dataset.id))
  );
  document.querySelectorAll("[data-del]").forEach((el) =>
    el.addEventListener("click", async () => {
      await fetch("/api/chats/" + el.dataset.del, { method: "DELETE" });
      if (activeId == el.dataset.del) newChat();
      loadChats();
    })
  );
}

async function openChat(id) {
  activeId = id;
  const r = await fetch(`/api/chat/${id}/messages`);
  const msgs = await r.json();
  $("messages").innerHTML = "";
  msgs.forEach((m) => addBubble(m.role, m.content));
}

function newChat() {
  activeId = null;
  $("messages").innerHTML = "";
}

$("composer").addEventListener("submit", (e) => {
  e.preventDefault();
  send();
});
$("new-chat").addEventListener("click", newChat);
$("clear-chat").addEventListener("click", () => ($("messages").innerHTML = ""));

renderQuick();
loadChats();
