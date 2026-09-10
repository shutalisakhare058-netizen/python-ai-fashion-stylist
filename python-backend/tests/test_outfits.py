def test_generate_outfit(client):
    r = client.post("/api/outfits/generate", json={"occasion": "interview"})
    assert r.status_code == 200
    data = r.json()
    assert data["demo"] is True
    assert data["outfit"]["top"]
    assert "Professional" in data["outfit"]["outfit"]


def test_save_and_list_and_delete_outfit(client):
    gen = client.post("/api/outfits/generate", json={"occasion": "party"}).json()
    save = client.post(
        "/api/outfits/save",
        json={"name": "My Party Look", "outfit_data": gen["outfit"]},
    )
    assert save.status_code == 200
    oid = save.json()["id"]

    saved = client.get("/api/outfits/saved").json()
    assert any(o["id"] == oid for o in saved)

    assert client.delete(f"/api/outfits/{oid}").status_code == 200


def test_profile_update(client):
    r = client.put(
        "/api/profile",
        json={"name": "Alex", "favorite_colors": "navy, cream"},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Alex"
