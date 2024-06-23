import threading
import time
import random
import logging
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, simpledialog
from tkinter import Scrollbar

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class Fourchette(threading.Semaphore):
    def __init__(self):
        super().__init__(1)

class Philosophe(threading.Thread):
    def __init__(self, nom, gauche, droite, callback, global_semaphore, hunger_threshold=10):
        super().__init__()
        self.nom = nom
        self.gauche = gauche
        self.droite = droite
        self.global_semaphore = global_semaphore
        self.manger_count = 0
        self.total_waiting_time = 0
        self.callback = callback
        self.hunger_threshold = hunger_threshold
        self.running = True
        self.paused = False
        self.last_meal_time = time.time()
        self.speed = 1.0
        self.forced_action = None

    def run(self):            
        while self.running:
            if not self.paused:
                if self.forced_action == "prendre":
                    self.prendre_fourchettes()
                    self.forced_action = None
                elif self.forced_action == "poser":
                    self.poser_fourchettes()
                    self.forced_action = None
                elif self.forced_action == "prendre_gauche":
                    self.prendre_fourchette_gauche()
                    self.forced_action = None
                elif self.forced_action == "prendre_droite":
                    self.prendre_fourchette_droite()
                    self.forced_action = None
                elif self.forced_action == "lacher_fourchettes":
                    self.lacher_fourchettes()
                    self.forced_action = None
                else:
                    self.penser()
                    start_waiting_time = time.time()
                    self.global_semaphore.acquire()
                    self.prendre_fourchettes()
                    waiting_time = time.time() - start_waiting_time
                    if waiting_time > 5:
                        self.callback(self.nom, "starve")
                        break
                    self.total_waiting_time += waiting_time
                    self.manger()
                    self.poser_fourchettes()
                    self.global_semaphore.release()
            time.sleep(0.1 / self.speed)

    def penser(self):
        self.callback(self.nom, "pense")
        time.sleep(random.uniform(1, 3) / self.speed)
        if time.time() - self.last_meal_time > self.hunger_threshold:
            self.callback(self.nom, "starve")
    
    def quitter_table_avec_fourchettes(self):
        self.callback(self.nom, "starve_with_forks")
        self.lacher_fourchettes()
        self.stop()

    def prendre_fourchettes(self):
        self.callback(self.nom, "attend")
        self.gauche.acquire()
        self.droite.acquire()

    def manger(self):
        self.manger_count += 1
        self.last_meal_time = time.time()
        self.callback(self.nom, "mange")
        time.sleep(random.uniform(1, 2) / self.speed)

    def poser_fourchettes(self):
        self.gauche.release()
        self.droite.release()
        self.callback(self.nom, "pose")

    def get_stats(self):
        if self.manger_count == 0:
            avg_waiting_time = 0
        else:
            avg_waiting_time = self.total_waiting_time / self.manger_count
        return self.manger_count, avg_waiting_time

    def reset_stats(self):
        self.manger_count = 0
        self.total_waiting_time = 0

    def stop(self):
        self.running = False

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def set_speed(self, speed):
        self.speed = speed

    def force_prendre(self):
        self.forced_action = "prendre"

    def force_poser(self):
        self.forced_action = "poser"
    
    def force_prendre_gauche(self):
        self.forced_action = "prendre_gauche"

    def force_prendre_droite(self):
        self.forced_action = "prendre_droite"

    def force_lacher_fourchettes(self):
        self.forced_action = "lacher_fourchettes"

    def prendre_fourchette_gauche(self):
        self.callback(self.nom, "attend_gauche")
        self.gauche.acquire()
        self.callback(self.nom, "prend_gauche")
        
    def prendre_fourchette_droite(self):
        self.callback(self.nom, "attend_droite")
        self.droite.acquire()
        self.callback(self.nom, "prend_droite")

    def lacher_fourchettes(self):
        if self.gauche.locked():
            self.gauche.release()
        if self.droite.locked():
            self.droite.release()
        self.callback(self.nom, "pose")

class Strategie:
    def __init__(self, table_philosophes):
        self.table_philosophes = table_philosophes
        
    def strategie_chandy_misra(self):
        for philo in self.table_philosophes.philosophes:
            philo.force_prendre_gauche()  # Philosophe prend d'abord la fourchette gauche
            time.sleep(0.1)  # Attente courte pour éviter les blocages potentiels
            philo.force_prendre_droite()  # Puis prend la fourchette droite

    def strategie_cas_pair(self):
        for i, philo in enumerate(self.table_philosophes.philosophes):
            if i % 2 == 0:
                philo.force_prendre_gauche()
                time.sleep(0.1)  # Attente courte pour éviter les blocages potentiels
                philo.force_prendre_droite()
            else:
                philo.force_prendre_droite()
                time.sleep(0.1)  # Attente courte pour éviter les blocages potentiels
                philo.force_prendre_gauche()
"""               
    def strategie_par_defaut(self):
        for philo in self.table_philosophes.philosophes:
            philo.force_prendre()

    def strategie_asymetrique(self):
        for philo in self.table_philosophes.philosophes:
            philo.force_prendre_gauche()
            time.sleep(0.1)  # Attendre un court moment pour éviter les blocages potentiels
            philo.force_prendre_droite()
"""           

        
class TablePhilosophes(tk.Tk):
    def __init__(self, philosophes, strategie_callback):
        super().__init__()
        self.title("Problème des Philosophes à Table")
        self.geometry("800x600")

        self.strategie = Strategie(self)
        self.strategie_callback = strategie_callback
        self.philosophes = philosophes

        self.canvas = tk.Canvas(self, width=800, height=400)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.philo_labels = {}
        self.fourchette_labels = {}
        self.create_table()

        self.control_frame = ttk.Frame(self)
        self.control_frame.pack(pady=10)

        self.start_button = ttk.Button(self.control_frame, text="Démarrer", command=self.start_simulation)
        self.start_button.grid(row=0, column=0, padx=5)

        self.pause_button = ttk.Button(self.control_frame, text="Pause", command=self.pause_simulation)
        self.pause_button.grid(row=0, column=1, padx=5)

        self.resume_button = ttk.Button(self.control_frame, text="Continuer", command=self.resume_simulation)
        self.resume_button.grid(row=0, column=2, padx=5)

        self.stop_button = ttk.Button(self.control_frame, text="Arrêter", command=self.stop_simulation)
        self.stop_button.grid(row=0, column=3, padx=5)

        self.reset_button = ttk.Button(self.control_frame, text="Réinitialiser Stats", command=self.reset_stats)
        self.reset_button.grid(row=1, column=0, padx=5)

        self.save_button = ttk.Button(self.control_frame, text="Enregistrer Stats", command=self.save_stats)
        self.save_button.grid(row=1, column=1, padx=5)

        self.force_take_button = ttk.Button(self.control_frame, text="Forcer Prendre", command=self.force_take)
        self.force_take_button.grid(row=1, column=2, padx=5)

        self.force_release_button = ttk.Button(self.control_frame, text="Forcer Lâcher", command=self.force_release)
        self.force_release_button.grid(row=1, column=3, padx=5)

        self.force_take_left_button = ttk.Button(self.control_frame, text="Forcer Prendre Gauche", command=self.force_take_left)
        self.force_take_left_button.grid(row=2, column=0, padx=5)

        self.force_take_right_button = ttk.Button(self.control_frame, text="Forcer Prendre Droite", command=self.force_take_right)
        self.force_take_right_button.grid(row=2, column=1, padx=5)

        self.force_release_both_button = ttk.Button(self.control_frame, text="Forcer Lâcher les Deux", command=self.force_release_both)
        self.force_release_both_button.grid(row=2, column=2, padx=5)

        self.state_label = ttk.Label(self, text="États des Philosophes:")
        self.state_label.pack(pady=10)

        self.state_text = tk.Text(self, height=10, width=60)
        self.state_text.pack()

        self.speed_label = ttk.Label(self, text="Vitesse:")
        self.speed_label.pack(pady=10)
        
        self.create_strategy_buttons()

        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = ttk.Scale(self, from_=0.1, to=2.0, orient='horizontal', variable=self.speed_var)
        self.speed_scale.pack(pady=10)
        self.speed_scale.bind("<Motion>", self.change_speed)

        self.update_states()

    def create_table(self):
        # Positions des philosophes autour de la table
        positions = [(200, 100), (400, 100), (500, 250), (300, 400), (100, 250)]
        for i, philo in enumerate(self.philosophes):
            x, y = positions[i]
            label = self.canvas.create_oval(x-20, y-20, x+20, y+20, fill="white")
            text = self.canvas.create_text(x, y, text=philo.nom)
            self.philo_labels[philo.nom] = (label, text)
            
            # Fourchette position between philosophers
            fx, fy = (x + positions[(i+1) % 5][0]) // 2, (y + positions[(i+1) % 5][1]) // 2
            f_label = self.canvas.create_rectangle(fx-5, fy-5, fx+5, fy+5, fill="black")
            self.fourchette_labels[(i, (i+1) % 5)] = f_label

        # Historique des actions
        self.action_label = ttk.Label(self, text="Historique des actions:")
        self.action_label.pack(pady=10)

        self.action_text = tk.Text(self, height=10, width=60)
        self.action_text.pack()
        
        # Bouton pour enregistrer l'historique
        self.save_history_button = ttk.Button(self, text="Enregistrer Historique", command=self.save_history)
        self.save_history_button.pack(pady=10)
        
        scrollbar = Scrollbar(self, orient="vertical", command=self.action_text.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.action_text.config(yscrollcommand=scrollbar.set)

    def save_history(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                history = self.action_text.get("1.0", tk.END)
                file.write(history)
        
    def mettre_a_jour(self, nom, action):
        label, text = self.philo_labels[nom]
        if action == "pense":
            self.canvas.itemconfig(label, fill="white")
        elif action == "mange":
            self.canvas.itemconfig(label, fill="green")
        elif action == "attend":
            self.canvas.itemconfig(label, fill="red")
        elif action == "pose":
            self.canvas.itemconfig(label, fill="white")
        elif action == "starve":
            self.canvas.itemconfig(label, fill="black")
            self.after(100, lambda: self.callback(nom, "starve"))  # Mettre à jour après 100 ms pour éviter les problèmes de thread
        elif action == "starve_with_forks":
            self.canvas.itemconfig(label, fill="black")
            self.after(100, lambda: self.callback(nom, "starve_with_forks"))  # Mettre à jour après 100 ms pour éviter les problèmes de thread
        elif action.startswith("attend_"):
            # Historique des actions
            self.after_idle(lambda: self.action_text.insert(tk.END, f"{nom}: {action}\n"))
            self.action_text.see(tk.END)  # Faire défiler jusqu'à la fin pour voir la dernière action

        self.update_states()

    def create_strategy_buttons(self):
        strategy_frame = ttk.Frame(self.control_frame)
        strategy_frame.grid(row=0, column=4, padx=5)

        ttk.Label(strategy_frame, text="Stratégie:").pack(side=tk.TOP, padx=5, pady=5)

        self.strategy_var = tk.StringVar()
        self.strategy_var.set("par_defaut")  # Par défaut

        ttk.Radiobutton(strategy_frame, text="Chandy/Misra", variable=self.strategy_var, value="chandy_misra",
                    command=self.changer_strategie).pack(anchor=tk.W, padx=5)

        ttk.Radiobutton(strategy_frame, text="Cas Pair", variable=self.strategy_var, value="cas_pair",
                    command=self.changer_strategie).pack(anchor=tk.W, padx=5)
        """
        ttk.Radiobutton(strategy_frame, text="Par défaut", variable=self.strategy_var, value="par_defaut",
                        command=self.changer_strategie).pack(anchor=tk.W, padx=5)

        ttk.Radiobutton(strategy_frame, text="Asymétrique", variable=self.strategy_var, value="asymetrique",
                        command=self.changer_strategie).pack(anchor=tk.W, padx=5)
        """
    def changer_strategie(self):
        nouvelle_strategie = self.strategy_var.get()
        self.strategie_callback(nouvelle_strategie)

    def update_states(self):
        states = ""
        for philo in self.philosophes:
            count, avg_wait = philo.get_stats()
            states += f"{philo.nom} - Nombre de fois mangé: {count}, Temps moyen d'attente: {avg_wait:.2f} secondes\n"
        self.state_text.delete(1.0, tk.END)
        self.state_text.insert(tk.END, states)

    def start_simulation(self):
        for philo in self.philosophes:
            if not philo.is_alive():
                philo.running = True
                philo.start()

    def stop_simulation(self):
        for philo in self.philosophes:
            philo.stop()

    def pause_simulation(self):
        for philo in self.philosophes:
            philo.pause()

    def resume_simulation(self):
        for philo in self.philosophes:
            philo.resume()

    def reset_stats(self):
        for philo in self.philosophes:
            philo.reset_stats()
        self.update_states()

    def save_stats(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                states = ""
                for philo in self.philosophes:
                    count, avg_wait = philo.get_stats()
                    states += f"{philo.nom} - Nombre de fois mangé: {count}, Temps moyen d'attente: {avg_wait:.2f} secondes\n"
                file.write(states)

    def force_take(self):
        nom = simpledialog.askstring("Forcer Prendre", "Entrez le nom du philosophe:")
        if nom:
            for philo in self.philosophes:
                if philo.nom == nom:
                    philo.force_prendre()
                    break

    def force_release(self):
        nom = simpledialog.askstring("Forcer Lâcher", "Entrez le nom du philosophe:")
        if nom:
            for philo in self.philosophes:
                if philo.nom == nom:
                    philo.force_poser()
                    break

    def change_speed(self, event):
        new_speed = self.speed_var.get()
        for philo in self.philosophes:
            philo.set_speed(new_speed)      

    def force_take_left(self):
        nom = simpledialog.askstring("Forcer Prendre Gauche", "Entrez le nom du philosophe:")
        if nom:
            for philo in self.philosophes:
                if philo.nom == nom:
                    philo.force_prendre_gauche()
                    break

    def force_take_right(self):
        nom = simpledialog.askstring("Forcer Prendre Droite", "Entrez le nom du philosophe:")
        if nom:
            for philo in self.philosophes:
                if philo.nom == nom:
                    philo.force_prendre_droite()
                    break

    def force_release_both(self):
        nom = simpledialog.askstring("Forcer Lâcher les Deux", "Entrez le nom du philosophe:")
        if nom:
            for philo in self.philosophes:
                if philo.nom == nom:
                    philo.force_lacher_fourchettes()
                    break
    """
    def changer_strategie(self, nouvelle_strategie):
        if nouvelle_strategie == "par_defaut":
            self.strategie.strategie_par_defaut()
        elif nouvelle_strategie == "asymetrique":
            self.strategie.strategie_asymetrique()
        else:
            logging.warning(f"Stratégie inconnue : {nouvelle_strategie}")
    """
    def create_control_buttons(self):
       # Ajouter des boutons pour changer de stratégie
       self.strategy_var = tk.StringVar()
       self.strategy_var.set("par_defaut")  # Par défaut
       strategy_frame = ttk.Frame(self.control_frame)
       strategy_frame.grid(row=0, column=4, padx=5)

       ttk.Label(strategy_frame, text="Stratégie:").pack(side=tk.TOP, padx=5, pady=5)
       
       ttk.Radiobutton(strategy_frame, text="Chandy/Misra", variable=self.strategy_var, value="chandy_misra",
                    command=self.changer_strategie).pack(anchor=tk.W, padx=5)

       ttk.Radiobutton(strategy_frame, text="Cas Pair", variable=self.strategy_var, value="cas_pair",
                    command=self.changer_strategie).pack(anchor=tk.W, padx=5)
       """
       ttk.Radiobutton(strategy_frame, text="Par défaut", variable=self.strategy_var, value="par_defaut",
                       command=self.changer_strategie).pack(anchor=tk.W, padx=5)
       ttk.Radiobutton(strategy_frame, text="Asymétrique", variable=self.strategy_var, value="asymetrique",
                       command=self.changer_strategie).pack(anchor=tk.W, padx=5)
       """
       def changer_strategie(self):
        nouvelle_strategie = self.strategy_var.get()
        self.strategie_callback(nouvelle_strategie)

def main():
    fourchettes = [Fourchette() for _ in range(5)]
    global_semaphore = threading.Semaphore(4)  # Limiter à 4 philosophes pour éviter le deadlock
    philosophes = []

    def callback(nom, action):
        table.mettre_a_jour(nom, action)

    philosopher_data = [
        ("Aristotle", "white"),
        ("Plato", "white"),
        ("Socrates", "white"),
        ("Confucius", "white"),
        ("Descartes", "white")
    ]

    for i, (nom, color) in enumerate(philosopher_data):
        philosophe = Philosophe(nom, fourchettes[i], fourchettes[(i+1) % 5], callback, global_semaphore)
        philosophes.append(philosophe)

    def changer_strategie(nouvelle_strategie):
        table.changer_strategie(nouvelle_strategie)

    table = TablePhilosophes(philosophes, changer_strategie)
    table.mainloop()

if __name__ == "__main__":
    main()
