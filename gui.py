import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from api_google import rechercher_livre
from database import creer_base, enregistrer_livre, lister_livres, livre_existe, supprimer_livre, vider_bibliotheque
from excel_manager import exporter_excel
from images_manager import telecharger_image, supprimer_image, creer_nom_image

LINE_WIDTH = 70


class CatalogueGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CatalogueBA - Interface graphique")
        self.geometry("1000x650")
        self.resizable(False, False)

        creer_base()
        self.livres_resultats = []
        self.livres_bibliotheque = []

        self.create_widgets()
        self.refresh_library()

    def create_widgets(self):
        self.search_frame = ttk.LabelFrame(self, text="Recherche Google Books")
        self.search_frame.place(x=10, y=10, width=480, height=200)

        ttk.Label(self.search_frame, text="Titre :").place(x=10, y=10)
        self.search_title = ttk.Entry(self.search_frame, width=55)
        self.search_title.place(x=10, y=35)

        ttk.Label(self.search_frame, text="Auteur :").place(x=10, y=70)
        self.search_author = ttk.Entry(self.search_frame, width=55)
        self.search_author.place(x=10, y=95)

        self.search_button = ttk.Button(self.search_frame, text="Rechercher", command=self.on_search)
        self.search_button.place(x=380, y=95)

        self.search_status = ttk.Label(self.search_frame, text="", foreground="blue")
        self.search_status.place(x=10, y=130)

        self.results_frame = ttk.LabelFrame(self, text="Résultats en ligne")
        self.results_frame.place(x=10, y=220, width=480, height=420)

        self.results_list = tk.Listbox(self.results_frame, height=22, width=70)
        self.results_list.place(x=10, y=10)
        self.results_list.bind("<<ListboxSelect>>", self.on_result_select)

        self.add_button = ttk.Button(self.results_frame, text="Ajouter à la bibliothèque", command=self.add_selected_book)
        self.add_button.place(x=10, y=350)

        self.refresh_button = ttk.Button(self.results_frame, text="Actualiser la bibliothèque", command=self.refresh_library)
        self.refresh_button.place(x=220, y=350)

        self.library_frame = ttk.LabelFrame(self, text="Ma bibliothèque")
        self.library_frame.place(x=500, y=10, width=490, height=380)

        self.library_list = tk.Listbox(self.library_frame, height=20, width=70)
        self.library_list.place(x=10, y=10)
        self.library_list.bind("<<ListboxSelect>>", self.on_library_select)

        self.delete_button = ttk.Button(self.library_frame, text="Supprimer le livre", command=self.delete_selected_book)
        self.delete_button.place(x=10, y=320)

        self.clear_button = ttk.Button(self.library_frame, text="Vider la bibliothèque", command=self.clear_library)
        self.clear_button.place(x=180, y=320)

        self.export_button = ttk.Button(self.library_frame, text="Exporter vers Excel", command=self.export_excel)
        self.export_button.place(x=380, y=320)

        self.details_frame = ttk.LabelFrame(self, text="Détails du livre")
        self.details_frame.place(x=500, y=400, width=490, height=240)

        self.details_text = tk.Text(self.details_frame, wrap="word", state="disabled")
        self.details_text.place(x=10, y=10, width=460, height=200)

    def on_search(self):
        titre = self.search_title.get().strip()
        auteur = self.search_author.get().strip()

        if not titre and not auteur:
            messagebox.showwarning("Recherche vide", "Veuillez saisir un titre ou un auteur.")
            return

        query = titre
        if auteur:
            query = f"intitle:{titre} inauthor:{auteur}" if titre else f"inauthor:{auteur}"

        self.set_search_enabled(False)
        self.set_status("Recherche en cours...")
        threading.Thread(target=self.perform_search, args=(query,), daemon=True).start()

    def perform_search(self, query):
        try:
            livres = rechercher_livre(query)
            self.after(0, lambda: self.on_search_success(livres))
        except Exception as err:
            self.after(0, lambda: self.on_search_error(err))

    def on_search_success(self, livres):
        self.livres_resultats = livres
        self.results_list.delete(0, tk.END)
        self.results_list.selection_clear(0, tk.END)

        if not self.livres_resultats:
            messagebox.showinfo("Aucun résultat", "Aucun livre trouvé pour cette recherche.")
            self.set_status("Aucun résultat")
        else:
            for livre in self.livres_resultats:
                label = f"{livre.titre} — {livre.auteur}"
                self.results_list.insert(tk.END, label)
            self.set_status(f"{len(self.livres_resultats)} résultat(s) trouvé(s)")

        self.after(3000, lambda: self.set_search_enabled(True))

    def on_search_error(self, err):
        messagebox.showerror("Erreur de recherche", str(err))
        self.set_status("Erreur de recherche. Réessayez dans quelques secondes.")
        self.after(5000, lambda: self.set_search_enabled(True))

    def set_status(self, text):
        self.search_status.config(text=text)

    def set_search_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.search_button.config(state=state)
        self.search_title.config(state=state)
        self.search_author.config(state=state)

    def on_result_select(self, event):
        selection = self.results_list.curselection()
        if not selection:
            return

        index = selection[0]
        if index < 0 or index >= len(self.livres_resultats):
            return

        livre = self.livres_resultats[index]
        self.show_details(livre)

    def on_library_select(self, event):
        selection = self.library_list.curselection()
        if not selection:
            return

        index = selection[0]
        if index < 0 or index >= len(self.livres_bibliotheque):
            return

        livre = self.livres_bibliotheque[index]
        self.show_details(livre)

    def show_details(self, livre):
        details = (
            f"Titre : {livre.titre}\n"
            f"Auteur : {livre.auteur}\n"
            f"Genre : {livre.genre or 'Inconnu'}\n"
            f"Date de parution : {livre.date_parution or 'N/A'}\n"
            f"ISBN : {livre.isbn or 'N/A'}\n\n"
            f"Description :\n{livre.description or 'Aucune description.'}"
        )
        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, details)
        self.details_text.configure(state="disabled")

    def add_selected_book(self):
        selection = self.results_list.curselection()
        if not selection:
            messagebox.showwarning("Aucun livre sélectionné", "Sélectionnez un livre dans les résultats pour l'ajouter.")
            return

        index = selection[0]
        if index < 0 or index >= len(self.livres_resultats):
            messagebox.showwarning("Sélection invalide", "La sélection du livre n'est plus valide. Relancez la recherche.")
            return

        livre = self.livres_resultats[index]
        if livre_existe(livre):
            messagebox.showinfo("Livre existant", "Ce livre est déjà présent dans la bibliothèque.")
            return

        enregistrer_livre(livre)
        nom_image = creer_nom_image(livre)
        telecharger_image(livre.image, nom_image)
        messagebox.showinfo("Ajouté", "Le livre a été ajouté à la bibliothèque.")
        self.refresh_library()

    def refresh_library(self):
        self.livres_bibliotheque = lister_livres()
        self.library_list.delete(0, tk.END)

        for livre in self.livres_bibliotheque:
            label = f"{livre.titre} — {livre.auteur}"
            self.library_list.insert(tk.END, label)

    def delete_selected_book(self):
        selection = self.library_list.curselection()
        if not selection:
            messagebox.showwarning("Aucun livre sélectionné", "Sélectionnez un livre dans la bibliothèque à supprimer.")
            return

        index = selection[0]
        if index < 0 or index >= len(self.livres_bibliotheque):
            messagebox.showwarning("Sélection invalide", "La sélection du livre n'est plus valide. Actualisez la bibliothèque.")
            return

        livre = self.livres_bibliotheque[index]
        if messagebox.askyesno("Confirmer", f"Supprimer '{livre.titre}' ?"):
            supprimer_livre(livre.isbn)
            supprimer_image(creer_nom_image(livre))
            messagebox.showinfo("Supprimé", "Le livre a été supprimé.")
            self.refresh_library()
            self.details_text.configure(state="normal")
            self.details_text.delete("1.0", tk.END)
            self.details_text.configure(state="disabled")

    def clear_library(self):
        if messagebox.askyesno("Vider la bibliothèque", "Voulez-vous vraiment supprimer tous les livres ?"):
            vider_bibliotheque()
            for filename in os.listdir("images"):
                chemin = os.path.join("images", filename)
                if os.path.isfile(chemin):
                    os.remove(chemin)
            self.refresh_library()
            self.details_text.configure(state="normal")
            self.details_text.delete("1.0", tk.END)
            self.details_text.configure(state="disabled")
            messagebox.showinfo("Bibliothèque vidée", "La bibliothèque a été vidée.")

    def export_excel(self):
        livres = self.livres_bibliotheque
        if not livres:
            messagebox.showwarning("Bibliothèque vide", "Il n'y a aucun livre à exporter.")
            return

        try:
            fichier = exporter_excel(livres)
            messagebox.showinfo("Export terminé", f"Fichier enregistré : {fichier}")
        except Exception as err:
            messagebox.showerror("Erreur d'export", str(err))


if __name__ == "__main__":
    app = CatalogueGUI()
    app.mainloop()
