# Capitolul 2: Stadiul Cunoașterii (State of the Art)

## 2.1. Introducere în testarea software și generarea automată

Asigurarea calității reprezintă o etapă critică în ciclul de viață al dezvoltării software (Software Development Life Cycle - SDLC). Pe măsură ce sistemele informatice devin tot mai complexe, riscul introducerii unor defecte ascunse crește exponențial, ceea ce face ca procesul de testare să fie nu doar o etapă de validare, ci o componentă fundamentală a ingineriei software.

### 2.1.1. Rolul și limitările testării unitare manuale

La baza strategiei de asigurare a calității stă testarea unitară (Unit Testing). Aceasta presupune izolarea și verificarea celor mai mici componente executabile ale unui program – de regulă, funcții sau metode individuale – pentru a demonstra că logica lor internă funcționează conform specificațiilor. Un test unitar valid verifică o singură rută de execuție, furnizând un set de date de intrare și comparând rezultatul obținut cu un rezultat așteptat.

Deși beneficiile testării unitare sunt bine documentate, abordarea tradițională, în care dezvoltatorii scriu manual aceste teste, prezintă limitări majore și este adesea predispusă la erori umane [1]:
* **Consum ridicat de resurse:** Scrierea exhaustivă a testelor unitare poate ocupa un procent semnificativ din timpul alocat dezvoltării.
* **Erori umane și bias-uri:** Programatorii au tendința de a scrie teste pentru scenariile de succes („happy paths”), omițând adesea cazurile limită (edge cases).
* **Mentenanță dificilă:** Odată cu evoluția codului sursă, suita de teste scrise manual trebuie actualizată constant.

Aceste provocări duc frecvent la o acoperire a codului (code coverage) insuficientă, lăsând zone vulnerabile neexplorate în aplicația finală.

### 2.1.2. Evoluția către generarea automată a testelor

Pentru a depăși blocajele impuse de testarea manuală, industria și mediul academic și-au îndreptat atenția către automatizare. Obiectivul acestui domeniu este de a utiliza algoritmi capabili să analizeze codul sursă și să sintetizeze automat atât datele de intrare, cât și aserțiunile corespunzătoare. Trecerea la generarea automată promite reducerea efortului manual și maximizarea acoperirii codului, explorând tehnici variate de la algoritmi euristici până la metode formale [2].

---

## 2.2. Tehnici utilizate în generarea automată a testelor

Pentru a automatiza procesul de creare a cazurilor de test, au fost dezvoltate o serie de tehnici fundamentale, care variază de la generarea de date complet aleatoare până la analiza profundă a structurii interne a codului.

### 2.2.1. Generarea aleatoare și Fuzzing-ul
Cea mai simplă formă de generare a testelor este testarea aleatoare. O evoluție a acestei tehnici este **Fuzzing-ul**, o metodă care implică furnizarea de date de intrare invalide, neașteptate sau complet aleatoare către un program.
* **Avantaje:** Este o tehnică rapidă, ușor de implementat și eficientă în descoperirea vulnerabilităților de securitate sau a excepțiilor neapărate (crashes).
* **Dezavantaje:** Limitarea majoră constă în probabilitatea extrem de scăzută de a genera date care să satisfacă instrucțiuni condiționale complexe (ex: egalități stricte), ducând la o acoperire slabă a codului.

### 2.2.2. Testarea bazată pe căutare (Search-Based Software Testing - SBST)
Pentru a depăși ineficiența generării aleatoare, tehnicile bazate pe căutare formulează generarea testelor ca pe o problemă de optimizare, folosind adesea algoritmi genetici. Un instrument reprezentativ din această categorie este EvoSuite [3]. Algoritmul folosește o funcție de fitness care măsoară cât de aproape este un test de a acoperi o anumită ramură de cod, ghidând căutarea către soluția optimă. Cu toate acestea, algoritmii pot rămâne blocați în minime locale și au dificultăți în rezolvarea constrângerilor matematice complexe.

### 2.2.3. Execuția Simbolică (Symbolic Execution)
Execuția simbolică reprezintă o tehnică de analiză fundamentală pentru generarea de teste white-box. În loc să ruleze programul cu valori concrete, folosește simboluri. Pe măsură ce programul avansează, instrumentul construiește o *condiție de cale* (path condition). La finalul fiecărei căi, formula logică este trimisă către un rezolvitor SMT pentru a genera datele concrete. Instrumente cunoscute includ KLEE [4]. Principalul obstacol rămâne *explozia spațiului de stări*, moment în care instrumentele formale bazate pe modele abstracte devin necesare.

---

## 2.3. Testarea bazată pe modele (Model-Based Testing)

Pe măsură ce limitele testării directe pe codul sursă devin evidente, paradigma Model-Based Testing (MBT) oferă o alternativă robustă.

### 2.3.1. Principiul de funcționare
Procesul de testare implică crearea unui model abstract, formal sau semi-formal, care descrie comportamentul așteptat al software-ului. Acest model acționează ca un oracol absolut [5]. Din acest model, un generator extrage cazuri de test abstracte care sunt ulterior transformate în teste concrete, executabile pe implementarea reală.

### 2.3.2. Tipuri de modele și avantaje
Modelele utilizate sunt, în general, sisteme de tranziție (Mașini cu Stări Finite, specificații algebrice). Principalul avantaj al MBT este detectarea erorilor de design încă din faza de specificare. Principala provocare o reprezintă expertiza matematică necesară pentru a construi un model formal corect. Combinarea MBT cu instrumente puternice de analiză a stărilor oferă o soluție robustă pentru generarea testelor cu acoperire garantată.

---

## 2.4. Metode formale și logica de rescriere

În contrast cu tehnicile empirice, metodele formale abordează verificarea software-ului dintr-o perspectivă matematică, utilizând sisteme logice pentru a garanta corectitudinea în raport cu o specificație.

### 2.4.1. Logica de rescriere (Rewriting Logic)
Introdusă de José Meseguer [6], logica de rescriere s-a impus ca un cadru unificator pentru modelarea sistemelor concurente și a limbajelor de programare. Stările sistemului sunt reprezentate ca termeni algebrici, iar evoluția este descrisă prin reguli de rescriere care modelează tranziții de stare locale.

### 2.4.2. Limbajul și sistemul Maude
Maude este un limbaj de specificare declarativ care implementează nativ logica ecuațională și logica de rescriere. Acesta permite definirea clară a:
1.  **Semanticii statice:** Prin ecuații, pentru evaluarea funcțiilor matematice deterministe.
2.  **Semanticii dinamice:** Prin reguli de rescriere, care definesc modul în care instrucțiunile modifică starea globală a mașinii abstracte (memorie, stivă).

### 2.4.3. Utilizarea Maude în generarea de teste
O specificație Maude fiind un model executabil, poate fi supusă explorării exhaustive a spațiului de stări. O direcție modernă utilizează capacitățile avansate ale Maude pentru a executa simbolic programele. Prin înlocuirea valorilor concrete cu variabile simbolice, instrumentul deduce constrângerile matematice necesare atingerii unei ramuri de cod. Lucrările lui Riesco au demonstrat aplicabilitatea directă a mecanismului de *narrowing* din Maude pentru generarea automată a cazurilor de test pe module funcționale [7]. De asemenea, succesul unor proiecte precum K Framework demonstrează viabilitatea acestei abordări pentru analiza riguroasă a codului [8].

### 2.4.4. Prezentarea soluțiilor software consacrate în domeniu
Pentru a contextualiza corect direcția propusă în această lucrare, este esențială trecerea în revistă a câtorva instrumente software majore bazate pe tehnicile descrise anterior:

* **EvoSuite (bazat pe algoritmi euristici):** Detaliat de Fraser și Arcuri [3], EvoSuite este un instrument dedicat limbajului Java care generează automat suite de teste JUnit, folosind algoritmi genetici pentru a maximiza acoperirea codului. Deși popular, întâmpină dificultăți în rezolvarea blocurilor decizionale cu constrângeri logice severe.
* **KLEE (bazat pe execuție simbolică):** Dezvoltat de Cadar et al. [4], KLEE este un motor de execuție simbolică care operează pe codul intermediar LLVM. Acesta a demonstrat capabilități remarcabile în găsirea erorilor critice prin construirea de ecuații matematice și rezolvarea lor cu SMT solvers, limitarea sa fiind explozia spațiului de stări în cazul programelor complexe.
* **K Framework (bazat pe logica de rescriere):** Prezentat de Roșu și Șerbănuță [8], este o platformă semantică fundamentată pe logica de rescriere. Utilizatorii definesc sintaxa și semantica unui limbaj, iar framework-ul generează automat unelte de analiză. Succesul său demonstrează că mașinile de stări bazate pe rescriere sunt ideale pentru analiza riguroasă a codului.
* **Maude Test-Case Generator:** În lucrarea sa [7], Adrián Riesco propune un instrument nativ în Maude care automatizează generarea de teste white-box folosind *narrowing*. O distincție importantă față de prezenta teză este că soluția lui Riesco generează teste pentru a valida module funcționale scrise direct în Maude. În contrast, prezenta lucrare propune utilizarea motorului Maude ca un mediu intermediar pentru a analiza și genera teste pentru un limbaj de programare extern, imperativ.

---

## 2.5. Analiză comparativă

Tabelul de mai jos sintetizează avantajele și limitările abordărilor analizate:

| Tehnica de generare | Avantaje principale | Dezavantaje și Limitări | Rigoare / Acoperire |
| :--- | :--- | :--- | :--- |
| **Fuzzing / Random Testing** | Rapidă; excelentă pentru găsirea excepțiilor neapărate (crashes). | Ineficientă pe instrucțiuni condiționale stricte. | Scăzută (fără garanții). |
| **Search-Based (SBST)** | Ghidează inteligent căutarea testelor; acoperire structurală bună. | Se poate bloca în minime locale; rezolvă greu constrângeri complexe. | Medie-Ridicată. |
| **Execuție Simbolică** | Fundament matematic; forțează atingerea ramurilor (SMT solvers). | Explozia spațiului de stări; scalabilitate redusă pe bucle. | Ridicată. |
| **Model-Based formal (Maude)** | Abstractizare logică; explorare exhaustivă a stărilor; detectează defecte de design. | Necesită expertiză pentru scrierea specificației formale. | Foarte Ridicată. |

---

## 2.6. Identificarea scopului și contribuția tezei

Analizând stadiul actual al cunoașterii, se observă un decalaj între rigoarea analizei formale și pragmatismul ingineriei software curente. Instrumentele capabile de explorare simbolică sunt adesea greu de integrat în suitele de testare obișnuite.

**Scopul principal al acestei teze** este explorarea, proiectarea și implementarea unui sistem punte: un generator de teste unitare fundamentat pe logica de rescriere (Maude). 

Contribuțiile majore propuse includ:
1.  **Modelarea formală:** Definirea semanticii operaționale (stare, memorie, stivă de control) în limbajul Maude pentru un subset specific de instrucțiuni (limbajul analizat).
2.  **Explorarea stărilor:** Utilizarea capacităților Maude pentru a parcurge ramurile de execuție, deducând datele de intrare și rezultatele așteptate (execuție simbolică).
3.  **Generarea codului de test:** Transpunerea automată a scenariilor izolate formal într-un format de test unitar executabil, validând practic implementarea inițială.

---

## Bibliografie

[1] P. Ammann și J. Offutt, *Introduction to Software Testing*, 2nd ed. Cambridge University Press, 2016.  
[2] S. Anand et al., "An Orchestrated Survey of Methodologies for Automated Software Test Case Generation," *Journal of Systems and Software*, vol. 86, no. 8, pp. 1978–2001, 2013.  
[3] G. Fraser și A. Arcuri, "EvoSuite: Automatic Test Suite Generation for Object-Oriented Software," în *Proc. of the 19th ACM SIGSOFT Symposium (ESEC/FSE)*, 2011, pp. 416–419.  
[4] C. Cadar, D. Dunbar, și D. Engler, "KLEE: Unassisted and Automatic Generation of High-Coverage Tests for Complex Systems Programs," în *8th USENIX Symposium (OSDI)*, 2008, pp. 209–224.  
[5] M. Utting și B. Legeard, *Practical Model-Based Testing: A Tools Approach*. Morgan Kaufmann, 2006.  
[6] J. Meseguer, "Conditional Rewriting Logic as a Unified Model of Concurrency," *Theoretical Computer Science*, vol. 96, no. 1, pp. 73–155, 1992.  
[7] A. Riesco, "Test-Case Generation for Maude Functional Modules," în *20th Int. Workshop on Algebraic Development Techniques*, Springer, 2012, pp. 287–301.  
[8] G. Roșu și T. F. Șerbănuță, "An Overview of the K Semantic Framework," *Journal of Logic and Algebraic Programming*, vol. 79, no. 6, pp. 397–434, 2010.