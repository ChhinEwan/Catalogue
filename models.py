class Livre:

    def __init__(self, titre, auteur, description, genre, date_parution, image, isbn, editeur=""):
        self.titre = titre
        self.auteur = auteur
        self.description = description
        self.genre = genre
        self.date_parution = date_parution
        self.image = image
        self.isbn = isbn
        self.editeur = editeur

    def __str__(self):
        return f"{self.titre} - {self.auteur}"
    
    def afficher_details(self):
        print("Titre :", self.titre)
        print("Auteur :", self.auteur)
        print("Éditeur :", self.editeur or "Éditeur non repertorié")
        print("Genre :", self.genre or "Genre non repertorie")
        print("Date de parution :", self.date_parution or "Date inconnu")
        print("ISBN :", self.isbn or "ISBN non repertorié")
        print("Description :", self.description or "Description non repertorié")
        print("Image :", self.image or "img non repertorie")

    def preview_description(self, max_len=700):
        """Return a truncated description for previews (adds '...' when cut)."""
        if not self.description:
            return ""
        desc = self.description
        if len(desc) > max_len:
            return desc[:max_len].rstrip() + "..."
        return desc