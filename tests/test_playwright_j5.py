"""
test_playwright_j5.py — TP J5 · Tests UI GameStore
====================================================
Complétez les TODO dans l'ordre.

Lancement :
    pytest tests/test_playwright_j5.py -v --headed
    pytest tests/test_playwright_j5.py -v          # headless (CI)
"""
from playwright.sync_api import Page, expect
from tests.pages.home_page_j5 import HomePage
from tests.pages.add_game_modal_j5 import AddGameModal

BASE_URL = "http://localhost:5000"


# ══════════════════════════════════════════════════════════════════════════════
# PARTIE 1 — Tests basiques (sans POM)
# Vous écrivez les sélecteurs directement dans les tests.
# Objectif : comprendre les locators Playwright avant de les encapsuler.
# ══════════════════════════════════════════════════════════════════════════════

def test_page_charge(page: Page):
    """
    TODO :
    1. page.goto(BASE_URL)
    2. assert page.title() == "GameStore"
    3. expect(page.locator("[data-testid=game-list]")).to_be_visible()
    """
    page.goto(BASE_URL)

    assert page.title() == "GameStore"

    expect(page.locator("[data-testid=game-list]")).to_be_visible()


def test_compteur_affiche_nombre_positif(page: Page):
    """
    TODO :
    1. Naviguer vers BASE_URL
    2. Attendre que [data-testid=game-count] soit visible
    3. Extraire le texte → "20 jeux" → extraire 20
    4. assert count > 0
    """
    page.goto(BASE_URL)

    game_count_element = page.locator("[data-testid=game-count]")
    game_count_element.wait_for(state="visible")

    text = game_count_element.text_content()

    numbers = re.findall(r'\d+', text)
    assert len(numbers) > 0, f"Aucun nombre trouvé dans le texte: {text}"

    count = int(numbers[0])

    assert count > 0, f"Le compteur doit être positif, reçu: {count}"


def test_recherche_filtre_resultats(page: Page):
    """
    TODO :
    1. Naviguer vers BASE_URL
    2. page.locator("[data-testid=search-input]").fill("Zelda")
    3. Attendre que les résultats se mettent à jour
    4. Vérifier que le premier game-title contient "Zelda"
    """
    page.goto(BASE_URL)

    search_input = page.locator("[data-testid=search-input]").fill("Zelda")

    first_game_title = page.locator("[data-testid=game-title]").first
    first_game_title.wait_for(state="visible")

    title_text = first_game_title.text_content()
    assert "Zelda" in title_text, f"Le titre doit contenir 'Zelda', reçu: {title_text}"



def test_filtre_genre_rpg(page: Page):
    """
    TODO :
    1. Naviguer vers BASE_URL
    2. page.locator("[data-testid=genre-filter]").select_option("RPG")
    3. Récupérer toutes les cartes avec locator("[data-testid=game-card]")
    4. Pour chaque carte, vérifier que game-genre contient "RPG"
    """
    page.goto(BASE_URL)

    page.locator("[data-testid=genre-filter]").select_option("RPG")

    game_cards = page.locator("[data-testid=game-card]")
    game_cards.first.wait_for(state="visible")

    game_cards = page.locator("[data-testid=game-card]")

    assert game_cards.count() > 0, "Aucun jeu RPG trouvé après le filtrage"

    for i in range(game_cards.count()):
        card = game_cards.nth(i)
        genre_element = card.locator("[data-testid=game-genre]")

        assert genre_element.count() > 0, f"Carte {i}: pas d'élément genre trouvé"

        genre_text = genre_element.text_content()
        assert "RPG" in genre_text, f"Carte {i}: genre '{genre_text}' ne contient pas 'RPG'"


# ══════════════════════════════════════════════════════════════════════════════
# PARTIE 2 — Page Object Model
# Mêmes scénarios mais via les classes POM.
# Plus aucun sélecteur dans les tests — tout passe par HomePage / AddGameModal.
# ══════════════════════════════════════════════════════════════════════════════

from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:3000"


class HomePage:
    def __init__(self, page: Page):
        self.page = page
        self.game_list = page.locator("[data-testid=game-list]")
        self.search_input = page.locator("[data-testid=search-input]")
        self.add_game_button = page.locator("[data-testid=add-game-btn]")

    def navigate(self):
        self.page.goto(BASE_URL)

    def open_add_form(self):
        self.add_game_button.click()

    def search(self, query: str):
        self.search_input.fill(query)
        self.page.wait_for_timeout(500)


class AddGameModal:
    def __init__(self, page: Page):
        self.page = page
        self.modal = page.locator("[data-testid=add-game-modal]")
        self.title_input = page.locator("[data-testid=modal-title]")
        self.genre_select = page.locator("[data-testid=modal-genre]")
        self.price_input = page.locator("[data-testid=modal-price]")
        self.submit_button = page.locator("[data-testid=modal-submit]")
        self.cancel_button = page.locator("[data-testid=modal-cancel]")

    def fill_and_submit(self, title: str, genre: str, price: float):
        self.title_input.fill(title)
        self.genre_select.select_option(genre)
        self.price_input.fill(str(price))
        self.submit_button.click()

    def cancel(self):
        self.cancel_button.click()


def test_pom_page_charge(page: Page):
    home = HomePage(page)
    home.navigate()
    assert page.title() == "GameStore"
    expect(home.game_list).to_be_visible()


def test_pom_ajouter_jeu(page: Page):
    home = HomePage(page)
    modal = AddGameModal(page)
    home.navigate()
    home.open_add_form()
    modal.fill_and_submit("Jeu POM Test", "Action", 19.99)
    expect(home.game_list).to_contain_text("Jeu POM Test")


def test_pom_annuler_formulaire(page: Page):
    home = HomePage(page)
    modal = AddGameModal(page)
    home.navigate()
    home.open_add_form()
    modal.cancel()
    expect(modal.modal).not_to_be_visible()


def test_pom_recherche(page: Page):
    home = HomePage(page)
    home.navigate()
    home.search("Zelda")
    first_card = home.game_list.locator("[data-testid=game-title]").first
    expect(first_card).to_contain_text("Zelda")