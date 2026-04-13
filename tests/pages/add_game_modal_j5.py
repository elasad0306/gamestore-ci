"""
pages/add_game_modal_j5.py — Page Object : modal d'ajout de jeu
================================================================
Complétez les TODO avant d'utiliser cette classe dans test_playwright_j5.py.
"""
from playwright.sync_api import Page


class AddGameModal:

    def __init__(self, page: Page):
        self.page = page

        self.modal        = page.locator("[data-testid=add-game-modal]")
        self.input_title  = page.locator("[data-testid=modal-title]")
        self.input_genre  = page.locator("[data-testid=modal-genre]")
        self.input_price  = page.locator("[data-testid=modal-price]")
        self.submit_btn   = page.locator("[data-testid=modal-submit]")
        self.cancel_btn   = page.locator("[data-testid=modal-cancel]")

    def fill_and_submit(self, title: str, genre: str, price: float):
        self.input_title.fill(title)
        self.input_genre.fill(genre)
        self.input_price.fill(str(price))
        self.submit_btn.click()

    def cancel(self):
        self.cancel_btn.click()

    def is_visible(self) -> bool:
        return self.modal.is_visible()