# Raspoređivanje Gostiju Pomoću Firefly Algoritma

- [Uvod](#uvod)
- [Ulazni podaci](#ulazni-podaci)
- [Struktura skripte](#struktura-skripte)
- [Primjer završnog izlaza](#primjer-završnog-izlaza)
- [Dependecies](#dependecies)

## 1. Uvod

Implementiran je Firefly algoritam (FA) za rješavanje optimizacijskog problema raspoređivanja gostiju u sobe. Cilj je maksimizirati ukupno zadovoljstvo gostiju na temelju njihovih međusobnih odnosa (prijatelji ili neprijatelji).

### 1.1. Opis problema

Zadan je određen broj gostiju i određen je broj soba, pri čemu svaka soba ima fiksni kapacitet (u ovom slučaju, dvoje gostiju po sobi). Za svaki par gostiju poznat je njihov odnos:

* **Prijatelji**: Pozitivna vrijednost (npr. +1)
* **Neprijatelji**: Negativna vrijednost (npr. -1)
* **Neutralni**: Nula ili nedefiniran odnos.

Potrebno je rasporediti sve goste u sobe tako da ukupna suma vrijednosti odnosa parova gostiju koji dijele sobu bude maksimalna.

### 1.2. Cilj

Maksimizirati "ukupno zadovoljstvo", koje se definira kao suma vrijednosti odnosa između gostiju smještenih u iste sobe. Idealno, prijatelji bi trebali dijeliti sobu, dok bi neprijatelji trebali biti u odvojenim sobama.

### 1.3. Korišteni algoritam: Firefly algoritam (FA)

Firefly algoritam je metaheuristički algoritam inspiriran ponašanjem krijesnica i njihovom sposobnošću privlačenja drugih krijesnica svjetlosnim signalima. Ključni koncepti su:

* **Svjetlina (Brightness)**: Intenzitet svjetlosti krijesnice proporcionalan je kvaliteti rješenja koje ona predstavlja (u ovom slučaju, "fitness" ili ukupno zadovoljstvo rasporeda).
* **Privlačnost (Attractiveness)**: Krijesnice s manjom svjetlinom privučene su krijesnicama s većom svjetlinom. Privlačnost opada s udaljenošću.
* **Kretanje (Movement)**: Krijesnice se kreću prema svjetlijim krijesnicama. Ako nema svjetlije krijesnice, krijesnica se kreće nasumično.

U ovoj skripti, Firefly algoritam je adaptiran za diskretni optimizacijski problem.

Sljedeća pravila opisuju standardni FA:

1. Sve krijesnice su uniseks, pa će jedna krijesnica biti privučena drugoj bez obzira na spol.
2. Za bilo koje dvije krijesnice koje svijetle, ona s manjom svjetlinom će ići prema onoj koja je svjetlija. Privlačnost je proporcionalna svjetlini, a obje vrijednosti opadaju kako se udaljenost između krijesnica povećava. Ako ne postoji nijedna svjetlija krijesnica od određene, ona će se kretati nasumično.
3. Svjetlina krijesnice određena je ili pod utjecajem je reljefa funkcije cilja.

**Objašnjenje algoritma**:

1. Inicijaliziranje populacije krijesnica nasumičnim pozicijama unutar prostora pretraživanja.
2. Definiranje funkcije kondicije (fitness) za svaku krijesnicu na temelju ciljne funkcije.
3. Procijenjivanje kondicije svake krijesnice pomoću ciljne funkcije.
4. Ažuriranje pozicije svake krijesnice uzimajući u obzir njezinu privlačnost prema drugim krijesnicama i njihovu svjetlosnu jačinu.
5. Ažuriranje svjetlosne jačine svake krijesnice na temelju njezine kondicije.
6. Ponavljanje koraka pomicanja i ažuriranja svjetlosne jačine dok se ne zadovolji kriterij zaustavljanja.
7. Izdvajanje najboljeg pronađenog rješenja nakon određenog broja iteracija.

<figure style="text-align: center;">
  <img src="/home/Kova/.var/app/io.typora.Typora/config/Typora/typora-user-images/image-20250503142114071.png" alt="Alt tekst slike" style="display: block; margin: 0 auto;">
  <figcaption style="text-align: center;">Firefly algoritam</figcaption>
</figure>

## 2. Ulazni podaci (`relations.csv`)

Skripta koristi CSV datoteku (standardno `relations.csv`) za definiranje odnosa između gostiju. Format datoteke je sljedeći:

* **Prvi red**: Zaglavlje (npr., `guest1,guest2,relationship`). Ovaj red se preskače prilikom učitavanja.
* **Ostali redovi**: Svaki red definira odnos između dva gosta:
  * `guest1`: Numerički ID prvog gosta (počevši od 0).
  * `guest2`: Numerički ID drugog gosta (počevši od 0).
  * `relationship`: Cjelobrojna vrijednost koja definira odnos:
    * `1`: Prijatelji
    * `-1`: Neprijatelji
    * (Druge vrijednosti ili 0 bi se mogle interpretirati kao neutralni ili drugačiji stupnjevi odnosa, ovisno o definiciji `calculate_fitness`).

Primjer sadržaja `relations.csv`:

```csv
guest1,guest2,relationship
0,1,1
0,2,-1
1,3,1
...
```



## 3. Struktura skripte

Skripta se sastoji od nekoliko glavnih dijelova: definicije parametara, pomoćnih funkcija, implementacije Firefly algoritma te glavnog dijela za izvršavanje.

### 3.1. Parametri (globalne konstante)

Na početku skripte definirani su globalni parametri koji upravljaju ponašanjem simulacije i algoritma:

* `NUM_GUESTS = 20`: Ukupan broj gostiju koje treba rasporediti.
* `NUM_ROOMS = 10`: Ukupan broj dostupnih soba.
* `GUESTS_PER_ROOM = 2`: Kapacitet svake sobe.
  * *Napomena*: Mora vrijediti `NUM_GUESTS == NUM_ROOMS * GUESTS_PER_ROOM`.
* `POPULATION_SIZE = 500`: Broj krijesnica (potencijalnih rješenja) u populaciji algoritma.
* `MAX_GENERATIONS = 1800`: Maksimalan broj iteracija (generacija) kroz koje će algoritam proći.
* `ALPHA = 0.6`: Parametar koji kontrolira komponentu nasumičnog kretanja krijesnica. U ovoj diskretnoj verziji, koristi se kao vjerojatnost da će krijesnica napraviti dodatni nasumični pomak (zamjenu gostiju).
* `RELATIONS_FILE = 'relations.csv'`: Naziv CSV datoteke koja sadrži podatke o odnosima između gostiju.

### 3.2. Glavne funkcije

#### 3.2.1. `generate_sample_relations(filename, num_guests, density, friend_prob)`

* **Svrha**: Generira primjer CSV datoteke (`relations.csv`) s nasumičnim odnosima između gostiju ako takva datoteka ne postoji.
* **Parametri**:
  * `filename` (str): Naziv datoteke za generiranje.
  * `num_guests` (int): Broj gostiju za koje se generiraju odnosi.
  * `density` (float): Gustoća odnosa; vjerojatnost da će bilo koji par gostiju imati definiran odnos (0.0 do 1.0).
  * `friend_prob` (float): Vjerojatnost da će definirani odnos biti prijateljski (+1), inače je neprijateljski (-1).
* **Ponašanje**: Kreira CSV datoteku s tri stupca: `guest1`, `guest2`, `relationship`. Vrijednost `relationship` je 1 za prijatelje i -1 za neprijatelje.
* **Povratna vrijednost**: Nema.

#### 3.2.2. `load_relations(filename, num_guests)`

* **Svrha**: Učitava odnose između gostiju iz specificirane CSV datoteke i pohranjuje ih u simetričnu NumPy matricu.
* **Parametri**:
  * `filename` (str): Naziv CSV datoteke za učitavanje.
  * `num_guests` (int): Očekivani broj gostiju (za dimenzioniranje matrice).
* **Ponašanje**:
  * Čita CSV datoteku red po red. Svaki red treba sadržavati dva gosta (identificirana brojevima od 0 do `num_guests-1`) i vrijednost njihovog odnosa.
  * Popunjava matricu odnosa (`relations_matrix`) gdje `relations_matrix[i, j]` sadrži vrijednost odnosa između gosta `i` i gosta `j`. Matrica je simetrična (`relations_matrix[i, j] = relations_matrix[j, i]`).
  * Ako datoteka nije pronađena, poziva `generate_sample_relations` da kreira primjer datoteke, a zatim je ponovno pokušava učitati.
  * Uključuje osnovno rukovanje greškama za format podataka.
* **Povratna vrijednost**: NumPy matrica (`np.array`) dimenzija `(num_guests, num_guests)` koja predstavlja odnose, ili `None` ako dođe do nepopravljive greške pri čitanju.

#### 3.2.3. `create_random_solution(num_guests, num_rooms, guests_per_room)`

* **Svrha**: Stvara nasumičan, ali valjan, raspored gostiju po sobama. Valjan raspored podrazumijeva da su svi gosti raspoređeni i da je kapacitet soba poštovan.
* **Parametri**:
  * `num_guests` (int): Ukupan broj gostiju.
  * `num_rooms` (int): Ukupan broj soba.
  * `guests_per_room` (int): Kapacitet svake sobe.
* **Ponašanje**:
  * Provjerava je li ukupan kapacitet soba jednak broju gostiju.
  * Stvara listu svih gostiju (numeriranih od 0 do `num_guests-1`).
  * Nasumično miješa listu gostiju.
  * Dijeli izmiješanu listu gostiju u grupe koje odgovaraju kapacitetu soba. Svaka grupa (soba) predstavlja tuple sortiranih ID-eva gostiju radi konzistentnosti.
* **Povratna vrijednost**: Lista tuple-ova, gdje svaki tuple predstavlja jednu sobu i sadrži ID-eve gostiju u toj sobi. Npr. `[(0, 5), (2, 10), ...]`.

#### 2.2.4. `calculate_fitness(solution, relations_matrix)`

* **Svrha**: Izračunava ukupno zadovoljstvo (fitness) za dani raspored gostiju.
* **Parametri**:
  * `solution` (list): Raspored gostiju po sobama (lista tuple-ova, gdje svaki tuple predstavlja sobu).
  * `relations_matrix` (np.array): Matrica koja sadrži vrijednosti odnosa između gostiju.
* **Ponašanje**:
  * Iterira kroz svaku sobu u rješenju.
  * Za par gostiju u sobi (pretpostavlja se dvoje po sobi), dohvaća vrijednost njihovog odnosa iz `relations_matrix`.
  * Sumira te vrijednosti za sve sobe kako bi dobila ukupni fitness rješenja.
* **Povratna vrijednost**: Float vrijednost koja predstavlja ukupni fitness rasporeda. Veća vrijednost znači bolji raspored.

#### 3.2.5. `perform_random_swap(solution)`

* **Svrha**: Generira novo, susjedno rješenje iz postojećeg rješenja tako što nasumično zamijeni dva gosta iz dvije različite sobe. Ovo je osnovni operator "kretanja" ili mutacije u algoritmu.
* **Parametri**:
  * `solution` (list): Trenutni raspored gostiju (lista tuple-ova).
* **Ponašanje**:
  * Pretvara tuple-ove soba u liste kako bi omogućila izmjene.
  * Nasumično odabire dvije različite sobe.
  * Nasumično odabire po jednog gosta iz svake od te dvije sobe.
  * Zamjenjuje odabrane goste između te dvije sobe.
  * Pretvara izmijenjene sobe natrag u sortirane tuple-ove radi konzistentnosti.
* **Povratna vrijednost**: Novo rješenje (lista tuple-ova) koje se razlikuje od ulaznog za jednu zamjenu gostiju.

#### 3.2.6. `firefly_algorithm(relations_matrix, num_guests, num_rooms, guests_per_room, pop_size, max_gen, alpha)`

* **Svrha**: Glavna funkcija koja implementira Firefly algoritam za pronalaženje optimalnog rasporeda gostiju.
* **Parametri**:
  * `relations_matrix` (np.array): Matrica odnosa.
  * `num_guests`, `num_rooms`, `guests_per_room` (int): Parametri problema.
  * `pop_size` (int): Veličina populacije (broj krijesnica).
  * `max_gen` (int): Maksimalni broj generacija.
  * `alpha` (float): Parametar nasumičnog kretanja.
* **Ponašanje**:
  1.  **Inicijalizacija**:
      * Ako `relations_matrix` nije dostupna, prekida izvršavanje.
      * Stvara inicijalnu populaciju od `pop_size` nasumičnih rješenja koristeći `create_random_solution`.
      * Izračunava fitness za svako rješenje u populaciji koristeći `calculate_fitness`.
      * Inicijalizira `best_solution_overall` i `best_fitness_overall` na najgore moguće vrijednosti.
      * `best_fitness_history` lista se koristi za praćenje najboljeg fitnessa po generaciji.
  2.  **Glavna petlja (iteracije kroz generacije)**: Ponavlja se `max_gen` puta.
      * Ažurira `best_solution_overall` i `best_fitness_overall` ako je u trenutnoj generaciji pronađeno bolje rješenje.
      * Sprema trenutni `best_fitness_overall` u `best_fitness_history`.
      * Stvara `new_population` za sljedeću generaciju.
      * **Kretanje krijesnica**: Za svaku krijesnicu `i` u trenutnoj populaciji:
        * `current_solution` i `current_fitness` su rješenje i fitness krijesnice `i`.
        * **Kretanje prema svjetlijim krijesnicama**:
          * Iterira kroz sve ostale krijesnice `j`.
          * Ako je krijesnica `j` svjetlija (tj. `fitnesses[j] > current_fitness`), krijesnica `i` se "pomiče" prema `j`.
          * U ovoj diskretnoj verziji, "pomak" se realizira izvođenjem jedne nasumične zamjene (`perform_random_swap`) na `current_solution`.
          * Krijesnica se pomiče samo prema prvoj boljoj na koju naiđe u iteraciji, nakon čega se petlja prekida (`break`). Ovo je pojednostavljenje u odnosu na klasični FA gdje bi se uzele u obzir sve svjetlije krijesnice i udaljenosti do njih.
        * **Dodatni nasumični pomak (Alpha faktor)**:
          * Neovisno o tome je li se krijesnica pomaknula prema svjetlijoj, s vjerojatnošću `alpha`, na `current_solution` (koje je ili originalno ili rezultat prethodnog pomaka) se primjenjuje još jedan `perform_random_swap`.
          * Ako se nasumični pomak ne dogodi (vjerojatnost `1-alpha`), rješenje ostaje nepromijenjeno od prethodnog koraka.
        * Modificirano rješenje (`final_solution`) dodaje se u `new_population`.
      * **Ažuriranje populacije**: `population` postaje `new_population`, i fitnessi se ponovno izračunavaju za sva rješenja u novoj populaciji.
      * Povremeno ispisuje napredak (trenutnu generaciju i najbolji fitness do sada).
  3.  **Završetak**:
      * Nakon svih generacija, još jednom provjerava je li najbolje rješenje u posljednjoj populaciji bolje od `best_solution_overall` i ažurira ako jest.
* **Povratna vrijednost**: Tuple koji sadrži:
  * `best_solution_overall` (list): Najbolji pronađeni raspored.
  * `best_fitness_overall` (float): Fitness najboljeg pronađenog rasporeda.
  * `best_fitness_history` (list): Lista najboljih fitnessa po generaciji.

#### 3.2.7. `plot_fitness(fitness_history)`

* **Svrha**: Crta grafikon koji prikazuje promjenu najboljeg fitnessa (ukupnog zadovoljstva) kroz generacije algoritma.
* **Parametri**:
  * `fitness_history` (list): Lista koja sadrži najbolju vrijednost fitnessa za svaku generaciju.
* **Ponašanje**: Koristi `matplotlib.pyplot` za generiranje linijskog grafa gdje je x-os generacija, a y-os najbolji fitness.
* **Povratna vrijednost**: Nema (prikazuje graf).



## 4. Primjer završnog izlaza

Generacija 10/1800, Najbolji fitness dosad: 5.00
Generacija 20/1800, Najbolji fitness dosad: 5.00
Generacija 30/1800, Najbolji fitness dosad: 6.00
Generacija 40/1800, Najbolji fitness dosad: 6.00
Generacija 50/1800, Najbolji fitness dosad: 6.00

...

Generacija 1790/1800, Najbolji fitness dosad: 8.00
Generacija 1800/1800, Najbolji fitness dosad: 8.00

Algoritam završen za 13.09 sekundi.

--- Najbolji pronađeni raspored ---
Ukupni fitness (zadovoljstvo): 8.00
Raspored po sobama (Gost1, Gost2):
  Soba 1: Gosti (0, 2) - Odnos: 1.0 (Prijatelji)
  Soba 2: Gosti (5, 17) - Odnos: 1.0 (Prijatelji)
  Soba 3: Gosti (9, 18) - Odnos: 1.0 (Prijatelji)
  Soba 4: Gosti (1, 6) - Odnos: 0.0 (Neutralni)
  Soba 5: Gosti (13, 15) - Odnos: 1.0 (Prijatelji)
  Soba 6: Gosti (12, 14) - Odnos: 1.0 (Prijatelji)
  Soba 7: Gosti (4, 19) - Odnos: 1.0 (Prijatelji)
  Soba 8: Gosti (7, 16) - Odnos: 0.0 (Neutralni)
  Soba 9: Gosti (8, 11) - Odnos: 1.0 (Prijatelji)
  Soba 10: Gosti (3, 10) - Odnos: 1.0 (Prijatelji)

![graf](/home/Kova/Desktop/graf.png)

## 5. Dependencies

- `numpy`
- `matplotlib`
- `csv`
- `random`
- `time`
