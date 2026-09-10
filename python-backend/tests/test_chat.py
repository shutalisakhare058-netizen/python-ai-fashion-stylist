def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_chat_creates_conversation(client):
    r = client.post("/api/chat", json={"message": "Suggest an outfit for college"})
    assert r.status_code == 200
    data = r.json()
    assert data["conversation_id"]
    assert data["demo"] is True  # no API key -> demo mode
    assert "OUTFIT" in data["reply"] or len(data["reply"]) > 0


def test_chat_empty_message_rejected(client):
    r = client.post("/api/chat", json={"message": "   "})
    assert r.status_code == 422


def test_chat_history_persists(client):
    r = client.post("/api/chat", json={"message": "Hi"})
    cid = r.json()["conversation_id"]
    msgs = client.get(f"/api/chat/{cid}/messages").json()
    assert len(msgs) == 2  # user + assistant


def test_list_and_delete_chats(client):
    client.post("/api/chat", json={"message": "Hello"})
    chats = client.get("/api/chats").json()
    assert len(chats) >= 1
    cid = chats[0]["id"]
    assert client.delete(f"/api/chats/{cid}").status_code == 200
