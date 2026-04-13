"""
TP1 — Tests Unitaires avec pytest · API GameStore
==================================================
Objectif : écrire 10 tests unitaires couvrant les fonctions de l'API GameStore.
Coverage cible : > 80 %

Lancement :
  pytest test_tp1_unit.py -v --cov=app_gamestore --cov-report=html
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# On importe l'application en mode test (BDD en mémoire)
from app_gamestore import app, init_db, get_db

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """
    Crée un client de test Flask avec une BDD SQLite en mémoire.
    La BDD est réinitialisée à chaque test grâce au scope par défaut (function).
    """
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'   # BDD en mémoire, isolée par test

    with app.test_client() as c:
        with app.app_context():
            init_db()
        yield c


@pytest.fixture
def sample_game():
    """Données d'un jeu valide pour les tests."""
    return {
        'title':  'The Zelda : Legacy',
        'genre':  'RPG',
        'price':  59.99,
        'rating': 4.9,
        'stock':  100,
    }


# Avec pytest.mark.parametrize
@pytest.mark.parametrize("title, genre,price, expected_status",[
    ("UFC 22", "Sport", 59.99, 201), #cas valide
    ("", "Sport", 59.99, 400), #titre vide -> erreur
    ("Asseto Corsa", "Sport", -59.99, 400), #prix négatif -> erreur
    ("GTA V", None, -59.99, 400), #genre absent -> erreur

])

# Test test_create_game_validation
def test_create_game_validation(client, title, genre, price, expected_status):
    request = client.post("/games", json={"title": title, "genre": genre, "price": price, })
    assert request.status_code == expected_status
# ── Tests à compléter ─────────────────────────────────────────────────────────

class TestListGames:

    def test_get_all_games_returns_200(self, client):
        """GET /games doit retourner le status 200."""
        result = client.get("/games")

        assert result.status_code == 200

    def test_get_all_games_returns_list(self, client):
        """GET /games doit retourner une liste (même vide)."""
        result = client.get("/games")

        data = result.get_json()

        assert isinstance(data, list)

    def test_get_games_filter_by_genre(self, client, sample_game):
        """GET /games?genre=RPG ne doit retourner que les RPG."""
        
        request = client.get("/games?genre=RPG")

        data = request.get_json()

        assert isinstance(data, list)

        for game in data:
            assert game['genre'] == "RPG"


class TestCreateGame:

    def test_create_valid_game_returns_201(self, client, sample_game):
        """POST /games avec données valides doit retourner 201."""
        request = client.post("/games", json=sample_game)

        data = request.get_json()
        assert request.status_code == 201

        assert "id" in data
       
    def test_create_game_returns_id(self, client, sample_game):
        """Le jeu créé doit avoir un 'id' dans la réponse."""
        request = client.post("/games", json={"title": "Football Manager 2021", "genre": "Sport", "price": 49.99, "rating": 3.5, "stock": 45})

        data = request.get_json()

        assert "id" in data

        delete = client.delete(f"/games/{data["id"]}")
        
    def test_create_game_without_title_returns_400(self, client):
        """POST /games sans titre doit retourner 400."""
        request = client.post("/games", json={"genre": "Sport", "price": 59.99, "rating": 4.5, "stock": 50})
        assert request.status_code == 400

    def test_create_game_with_negative_price_returns_400(self, client):
        """Un prix négatif doit être rejeté avec un 400."""
        request = client.post("/games", json={"genre": "Sport", "price": -59.99, "rating": 4.5, "stock": 50})
        assert request.status_code == 400

    def test_create_duplicate_title_returns_409(self, client, sample_game):
        """Créer deux jeux avec le même titre doit retourner 409."""
        request = client.post("/games", json=sample_game)
        assert request.status_code == 409
    

class TestGetGame:

    def test_get_existing_game_returns_200(self, client, sample_game):
        """GET /games/1 pour un jeu existant doit retourner 200."""

        request = client.post("/games", json={"title": "Football Manager 2022", "genre": "Sport", "price": 49.99, "rating": 3.5, "stock": 45})

        id_game = request.get_json()["id"]
        
        response = client.get(f"/games/{id_game}")

        assert response.status_code == 200

        delete = client.delete(f"/games/{id_game}")

    def test_get_nonexistent_game_returns_404(self, client):
        """GET /games/9999 pour un jeu inexistant doit retourner 404."""
        request = client.get("/games/99999")

        assert request.status_code == 404


class TestDeleteGame:

    def test_delete_existing_game_returns_204(self, client, sample_game):
        """DELETE /games/1 pour un jeu existant doit retourner 204."""
        request = client.post("/games", json={"title": "Football Manager 2026", "genre": "Sport", "price": 49.99, "rating": 3.5, "stock": 45})

        id_game = request.get_json()["id"]
        
        response = client.delete(f"/games/{id_game}")

        assert response.status_code == 204
    def test_delete_nonexistent_game_returns_404(self, client):
        """DELETE /games/9999 doit retourner 404."""
        request = client.delete("/games/99999")

        assert request.status_code == 404
