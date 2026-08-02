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
        self.current_query = ""
        self.current_start_index = 0
        self.current_total_items = 0
        self.drag_data = {"source": None, "index": None, "text": None}
        self.drag_label = None

        self.create_widgets()
        self.refresh_library()

    def create_widgets(self):
        self.search_frame = ttk.LabelFrame(self, text="Recherche Google Books")
        self.search_frame.place(x=10, y=10, width=480, height=200)

        ttk.Label(self.search_frame, text="Titre :").place(x=10, y=10)
        self.search_title = ttk.Entry(self.search_frame, width=55)
        self.search_title.place(x=10, y=35)
        self.search_title.bind("<Return>", lambda event: self.on_search())

        ttk.Label(self.search_frame, text="Auteur :").place(x=10, y=70)
        self.search_author = ttk.Entry(self.search_frame, width=55)
        self.search_author.place(x=10, y=95)
        self.search_author.bind("<Return>", lambda event: self.on_search())

        self.search_button = ttk.Button(self.search_frame, text="Rechercher", command=self.on_search)
        self.search_button.place(x=380, y=95)

        self.search_status = ttk.Label(self.search_frame, text="", foreground="blue")
        self.search_status.place(x=10, y=130)

        self.results_frame = ttk.LabelFrame(self, text="Résultats en ligne")
        self.results_frame.place(x=10, y=220, width=480, height=420)

        self.results_list = tk.Listbox(self.results_frame, height=22, width=70)
        self.results_list.place(x=10, y=10)
        self.results_list.bind("<<ListboxSelect>>", self.on_result_select)
        self.results_list.bind("<ButtonPress-1>", self.on_drag_start)
        self.results_list.bind("<B1-Motion>", self.on_drag_motion)
        self.bind("<ButtonRelease-1>", self.on_drag_end)

        self.add_button = ttk.Button(self.results_frame, text="Ajouter à la bibliothèque", command=self.add_selected_book)
        self.add_button.place(x=10, y=350)

        self.load_more_button = ttk.Button(self.results_frame, text="Charger plus", command=self.load_more_results, state="disabled")
        self.load_more_button.place(x=220, y=350)

        self.refresh_button = ttk.Button(self.results_frame, text="Actualiser la bibliothèque", command=self.refresh_library)
        self.refresh_button.place(x=360, y=350)

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

        self.current_query = query
        self.current_start_index = 0
        self.current_total_items = 0

        self.set_search_enabled(False)
        self.set_status("Recherche en cours...")
        threading.Thread(target=self.perform_search, args=(query, 0), daemon=True).start()

    def perform_search(self, query, start_index):
        try:
            livres, total = rechercher_livre(query, start_index=start_index, return_total=True)
            self.after(0, lambda: self.on_search_success(livres, total, append=start_index > 0))
        except Exception as err:
            self.after(0, lambda: self.on_search_error(err))

    def on_search_success(self, livres, total, append=False):
        if append:
            self.livres_resultats.extend(livres)
        else:
            self.livres_resultats = livres
            self.results_list.delete(0, tk.END)
            self.results_list.selection_clear(0, tk.END)

        self.current_total_items = total
        self.current_start_index = len(self.livres_resultats)

        if not self.livres_resultats:
            messagebox.showinfo("Aucun résultat", "Aucun livre trouvé pour cette recherche.")
            self.set_status("Aucun résultat")
            self.load_more_button.config(state="disabled")
        else:
            for livre in livres:
                label = f"{livre.titre} — {livre.auteur}"
                self.results_list.insert(tk.END, label)
            if total:
                self.set_status(f"{len(self.livres_resultats)}/{total} résultat(s)")
                more_state = "normal" if len(self.livres_resultats) < total else "disabled"
                self.load_more_button.config(state=more_state)
            else:
                self.set_status(f"{len(self.livres_resultats)} résultat(s) trouvé(s)")
                self.load_more_button.config(state="disabled")

        self.set_search_enabled(True)

    def on_search_error(self, err):
        messagebox.showerror("Erreur de recherche", str(err))
        self.set_status("Erreur de recherche.")
        self.load_more_button.config(state="disabled")
        self.set_search_enabled(True)

    def load_more_results(self):
        if not self.current_query or len(self.livres_resultats) >= self.current_total_items:
            return

        self.set_search_enabled(False)
        self.set_status("Chargement de plus de résultats...")
        start_index = len(self.livres_resultats)
        threading.Thread(target=self.perform_search, args=(self.current_query, start_index), daemon=True).start()

    def set_status(self, text):
        self.search_status.config(text=text)

    def on_drag_start(self, event):
        index = self.results_list.nearest(event.y)
        if index < 0 or index >= len(self.livres_resultats):
            return

        self.drag_data["source"] = self.results_list
        self.drag_data["index"] = index
        self.drag_data["text"] = self.results_list.get(index)
        self.create_drag_label(event.x_root, event.y_root, self.drag_data["text"])
        self.set_status("Faites glisser vers la bibliothèque pour ajouter le livre.")

    def on_drag_motion(self, event):
        if self.drag_label is None:
            return
        x = event.x_root + 10
        y = event.y_root + 10
        self.drag_label.geometry(f"+{x}+{y}")

    def on_drag_end(self, event):
        if not self.drag_data["text"]:
            return

        target = self.winfo_containing(event.x_root, event.y_root)
        if target == self.library_list:
            self.add_book_from_drag(self.drag_data["index"])

        self.clear_drag()

    def create_drag_label(self, x, y, text):
        if self.drag_label:
            self.drag_label.destroy()

        self.drag_label = tk.Toplevel(self)
        self.drag_label.overrideredirect(True)
        self.drag_label.attributes("-topmost", True)
        label = ttk.Label(self.drag_label, text=text, background="#fff8b0", relief="solid", borderwidth=1)
        label.pack(ipadx=5, ipady=3)
        self.drag_label.geometry(f"+{x+10}+{y+10}")

    def clear_drag(self):
        if self.drag_label:
            self.drag_label.destroy()
            self.drag_label = None

        self.drag_data = {"source": None, "index": None, "text": None}
        self.set_status("")

    def add_book_from_drag(self, index):
        if index < 0 or index >= len(self.livres_resultats):
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
            f"Genre : {livre.genre or 'Genre non repertorié'}\n"
            f"Date de parution : {livre.date_parution or 'Date inconnu'}\n"
            f"ISBN : {livre.isbn or 'ISBN non repertorié'}\n"
            f"Image : {livre.image or 'img non repertorie'}\n\n"
            f"Description :\n{livre.description or 'Description non repertorié'}"
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
