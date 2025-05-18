import csv
import random
import numpy as np
import matplotlib.pyplot as plt
import time

# --- Parametri ---
NUM_GUESTS = 20
NUM_ROOMS = 10
GUESTS_PER_ROOM = 2

# FA Parametri
POPULATION_SIZE = 500  # Broj krijesnica (rješenja u populaciji)  # 300    # 500 je drugi
MAX_GENERATIONS = 1800 # Broj iteracija algoritma  # 900      # 1000 je drugi   # 1200
ALPHA = 0.6      # Parametar slučajnog kretanja (utječe na veličinu nasumičnog koraka) # 0.7
# U našoj diskretnoj verziji, možemo ALPHA koristiti kao vjerojatnost dodatnog nasumičnog pomaka
# Beta0 i Gamma (privlačnost) su implicitno modelirani kroz pravilo pomaka prema boljem

RELATIONS_FILE = 'relations.csv'

# --- Funkcije ---

def generate_sample_relations(filename=RELATIONS_FILE, num_guests=NUM_GUESTS, density=0.2, friend_prob=0.6):
    """Generira primjer relations.csv datoteke."""
    print(f"Generiram primjer datoteke {filename}...")
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['guest1', 'guest2', 'relationship']) # Header
        generated_pairs = set()
        for i in range(num_guests):
            for j in range(i + 1, num_guests):
                 # Generira odnos s određenom gustoćom
                 if random.random() < density:
                     if (i, j) not in generated_pairs:
                         value = 1 if random.random() < friend_prob else -1
                         writer.writerow([i, j, value])
                         generated_pairs.add((i,j))
    print(f"Datoteka {filename} generirana.")


def load_relations(filename=RELATIONS_FILE, num_guests=NUM_GUESTS):
    """Učitava odnose iz CSV datoteke u matricu."""
    relations_matrix = np.zeros((num_guests, num_guests))
    try:
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader) # Preskoči header
            for row in reader:
                if len(row) == 3:
                    try:
                        g1, g2, value = int(row[0]), int(row[1]), int(row[2])
                        if 0 <= g1 < num_guests and 0 <= g2 < num_guests:
                           # Osiguraj simetričnost
                           relations_matrix[g1, g2] = value
                           relations_matrix[g2, g1] = value
                        else:
                           print(f"Upozorenje: Gosti izvan raspona u redu {row}, preskačem.")
                    except ValueError:
                        print(f"Upozorenje: Nevažeći format broja u redu {row}, preskačem.")
                else:
                    print(f"Upozorenje: Neispravan broj stupaca u redu {row}, preskačem.")

    except FileNotFoundError:
        print(f"Greška: Datoteka {filename} nije pronađena.")
        print("Generiram primjer datoteke...")
        generate_sample_relations(filename, num_guests)
        # Ponovno pokušaj učitati nakon generiranja
        return load_relations(filename, num_guests)
    except Exception as e:
        print(f"Greška pri čitanju datoteke {filename}: {e}")
        return None # Vrati None u slučaju greške

    print(f"Odnosi uspješno učitani iz {filename}.")
    return relations_matrix

def create_random_solution(num_guests=NUM_GUESTS, num_rooms=NUM_ROOMS, guests_per_room=GUESTS_PER_ROOM):
    """Stvara nasumičan, ali valjan raspored gostiju po sobama."""
    if num_guests != num_rooms * guests_per_room:
        raise ValueError("Broj gostiju se ne poklapa s kapacitetom soba!")

    guests = list(range(num_guests))
    random.shuffle(guests)

    solution = []
    for i in range(0, num_guests, guests_per_room):
        room = tuple(sorted(guests[i:i+guests_per_room])) # Tuple sortiranih gostiju za konzistentnost
        solution.append(room)

    return solution # Vraća listu tuple-ova (soba)

def calculate_fitness(solution, relations_matrix):
    """Izračunava ukupno zadovoljstvo (fitness) za dani raspored."""
    total_fitness = 0
    for room in solution:
        guest1, guest2 = room[0], room[1] # Pretpostavka da su 2 gosta po sobi
        total_fitness += relations_matrix[guest1, guest2]
    return total_fitness

def perform_random_swap(solution):
    """Napravi jednu nasumičnu valjanu zamjenu gostiju između dvije sobe."""
    new_solution = [list(room) for room in solution] # Pretvori u listu listi za izmjenu

    # Odaberi dvije različite sobe
    room_idx1, room_idx2 = random.sample(range(len(new_solution)), 2)

    # Odaberi po jednog gosta iz svake sobe za zamjenu
    guest_idx_in_room1 = random.randrange(len(new_solution[room_idx1]))
    guest_idx_in_room2 = random.randrange(len(new_solution[room_idx2]))

    # Zamijena gosta
    guest_to_move1 = new_solution[room_idx1].pop(guest_idx_in_room1)
    guest_to_move2 = new_solution[room_idx2].pop(guest_idx_in_room2)

    new_solution[room_idx1].append(guest_to_move2)
    new_solution[room_idx2].append(guest_to_move1)

    # Pretvaranje natrag u listu sortiranih tuple-ova
    final_solution = [tuple(sorted(room)) for room in new_solution]
    return final_solution

def firefly_algorithm(relations_matrix, num_guests, num_rooms, guests_per_room,
                      pop_size, max_gen, alpha):
    """Glavna funkcija Firefly algoritma."""
    if relations_matrix is None:
        print("Greška: Matrica odnosa nije dostupna. Prekidam.")
        return None, -float('inf'), []

    # 1. Inicijalizacija populacije
    population = [create_random_solution(num_guests, num_rooms, guests_per_room) for _ in range(pop_size)]
    fitnesses = np.array([calculate_fitness(sol, relations_matrix) for sol in population])

    best_solution_overall = None
    best_fitness_overall = -float('inf')
    best_fitness_history = [] # Za praćenje najboljeg fitnessa po generaciji

    start_time = time.time()

    # 2. Glavna petlja algoritma
    for generation in range(max_gen):
        # Pronalazak trenutno najboljeg u generaciji
        current_gen_best_idx = np.argmax(fitnesses)
        current_gen_best_fitness = fitnesses[current_gen_best_idx]
        if current_gen_best_fitness > best_fitness_overall:
            best_fitness_overall = current_gen_best_fitness
            best_solution_overall = population[current_gen_best_idx]

        best_fitness_history.append(best_fitness_overall) # Prati najbolji do SAD

        new_population = [None] * pop_size

        # Kretanje krijesnica
        for i in range(pop_size):
            current_solution = population[i]
            current_fitness = fitnesses[i]

            # Kretanje prema svjetlijim krijesnicama
            moved_towards_brighter = False
            for j in range(pop_size):
                if fitnesses[j] > current_fitness:
                    # Pomak 'prema' j tako što se napravi nasumična promjena
                    candidate_solution = perform_random_swap(current_solution)
                    # Ovdje se ne provjerava fitness kandidata odmah, FA se pomiče bez obzira
                    current_solution = candidate_solution # Privremeno prihvati pomak
                    moved_towards_brighter = True
                    break # Pomakni se samo prema prvoj boljoj na koju naiđeš

            # Dodatni nasumični pomak (Alpha faktor) - uvijek se događa
            # Može se koristiti alpha kao vjerojatnost dodatnog pomaka
            if random.random() < alpha:
               final_solution = perform_random_swap(current_solution)
            else:
               final_solution = current_solution # Nema dodatnog pomaka

            new_population[i] = final_solution # Spremanje rješenja za sljedeću generaciju

        # Ažuriravanje populacije i fitness
        population = new_population
        fitnesses = np.array([calculate_fitness(sol, relations_matrix) for sol in population])

        if (generation + 1) % 10 == 0: # Ispis napretka svakih 10 generacija
             print(f"Generacija {generation+1}/{max_gen}, Najbolji fitness dosad: {best_fitness_overall:.2f}")

    end_time = time.time()
    print(f"\nAlgoritam završen za {end_time - start_time:.2f} sekundi.")

    # Pronađi konačno najboljeg u posljednjoj populaciji
    final_best_idx = np.argmax(fitnesses)
    if fitnesses[final_best_idx] > best_fitness_overall:
        best_solution_overall = population[final_best_idx]
        best_fitness_overall = fitnesses[final_best_idx]
        # Ažuriravanje zadnje vrijednosti u history ako je zadnja populacija dala boljeg
        if best_fitness_history:
             best_fitness_history[-1] = best_fitness_overall


    return best_solution_overall, best_fitness_overall, best_fitness_history

def plot_fitness(fitness_history):
    """Crtanje graf promjene najboljeg fitnessa kroz generacije."""
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(fitness_history) + 1), fitness_history, marker='o', linestyle='-')
    plt.title('Promjena Najboljeg Fitnessa Kroz Generacije (Firefly Algoritam)')
    plt.xlabel('Generacija')
    plt.ylabel('Najbolji Fitness (Ukupno Zadovoljstvo)')
    plt.grid(True)
    plt.show()

# --- Glavni dio skripte ---
if __name__ == "__main__":
    # 1. Učitava ili generira odnose
    relations = load_relations(RELATIONS_FILE, NUM_GUESTS)

    if relations is not None:
        # 2. Pokreće Firefly algoritam
        best_solution, best_fitness, fitness_history = firefly_algorithm(
            relations_matrix=relations,
            num_guests=NUM_GUESTS,
            num_rooms=NUM_ROOMS,
            guests_per_room=GUESTS_PER_ROOM,
            pop_size=POPULATION_SIZE,
            max_gen=MAX_GENERATIONS,
            alpha=ALPHA
        )

        # 3. Ispis rezultata
        if best_solution:
            print("\n--- Najbolji pronađeni raspored ---")
            print(f"Ukupni fitness (zadovoljstvo): {best_fitness:.2f}")
            print("Raspored po sobama (Gost1, Gost2):")
            for i, room in enumerate(best_solution):
                g1, g2 = room
                rel_value = relations[g1, g2]
                rel_desc = "Prijatelji" if rel_value > 0 else ("Neprijatelji" if rel_value < 0 else "Neutralni")
                print(f"  Soba {i+1}: Gosti ({g1}, {g2}) - Odnos: {rel_value} ({rel_desc})")

            # 4. Vizualiziranje promjena fitnessa
            if fitness_history:
                plot_fitness(fitness_history)
            else:
                print("Nema podataka za crtanje grafa.")
        else:
            print("Nije pronađeno rješenje.")
    else:
        print("Izvršavanje prekinuto zbog greške s učitavanjem odnosa.")