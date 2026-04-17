# Introducere în testare și generare automată de teste

Activitatea de asigurare a calității (*Quality Assurance*) a devenit o componentă integrată și fundamentală a întregului ciclu de viată al dezvoltării software, datorită creșterii complexității soluțiilor software. Astfel, livrarea unor soluții software fiabile, securizte și performante depinde în mod explicit de rigoarea cu care se realizează întregul proces de testare.

În cadrul acestui proces, un rol important o are testarea unitară, fiind fundația pe care se vor contrui ulterior testele de integrare și cele de sistem. Ținta principală a testării unitare constă în izolarea și verificarea în mod independent cele mai mici componente executabile ale unui program. Se consideră că o componentă este corectă dacă pentru un set de date de intrare se produce rezultatul asteptat și modifica starea sistemului conform specificatiilor. fara să genereze efecte secundare nedorite.

Desi testarea unitara faciliteaza refactorizarea codului si depistarea din timp a erorilor, reducand astfel costurile de remediere în etapele ulterioare, abordarea clasică prezintă urmatoarele limitări: 
1. Consumul masiv de resurse si timp
2. Bias-uri de confimare si eventuale erori umane
3. Provocari de mentenantă
Pentru a depăși aceste blocaje, mediul academic și industria de software au inițiat o tranziție de la simpla execuție automată a testelor (facilitată de framework-uri precum JUnit, NUnit sau PyTest) către **generarea automată a acestora (Automated Test Case Generation)**
Diferența de paradigmă este majoră: în loc ca programatorul să scrie manual valorile de intrare și aserțiunile, se utilizează un instrument software specializat care analizează codul sursă, specificațiile sau un model abstract al programului. Acest instrument folosește algoritmi pentru a sintetiza automat datele de test necesare atingerii diverselor ramuri de execuție, deducând totodată rezultatele așteptate.
Obiectivele principale ale generării automate sunt:
- **Maximizarea acoperirii structurale (Structural Coverage):** Asigurarea că fiecare instrucțiune (statement coverage) și fiecare decizie logică (branch coverage) din cod a fost executată cel puțin o dată pe parcursul testării.
- **Optimizarea costurilor:** Reducerea timpului petrecut de ingineri în activități de testare repetitive, permițându-le să se concentreze pe arhitectură și pe logica de business.
- **Descoperirea defectelor profunde:** Prin generarea unor permutări de date pe care mintea umană nu le-ar concepe în mod natural, generatoarele automate sunt capabile să aducă la suprafață vulnerabilități ascunse sau blocaje neașteptate [2].
Pentru a atinge aceste obiective, au fost propuse multiple metodologii de-a lungul timpului, de la generatoare de date aleatoare, până la instrumente analitice complexe care utilizează raționamentul matematic, fiecare venind cu propriul set de avantaje și limitări.
# Tehnici utilizare în generarea automată de teste
Pentru a automatiza procesul de creare a cazurilor de test și a datelor de intrare aferente, literatura de specialitate propune o multitudine de tehnici fundamentale. Acestea pot fi clasificate în funcție de cantitatea de informații pe care algoritmul o deține despre codul sursă: de la abordări de tip _black-box_ (unde structura internă a programului este necunoscută), până la analize de tip _white-box_ (unde generatorul analizează direct instrucțiunile și fluxul de control). În continuare sunt detaliate cele mai proeminente trei direcții de cercetare din acest domeniu.

#### 2.2.1. Generarea aleatoare și Fuzzing-ul

Cea mai elementară metodă de a genera date de test este **testarea aleatoare (Random Testing)**, care presupune selectarea la întâmplare a valorilor de intrare din domeniul de definiție al variabilelor programului. Deși conceptual simplă, această abordare a evoluat semnificativ sub forma tehnicii cunoscute drept **Fuzzing**.

Fuzzing-ul este o metodă de testare automată care implică injectarea de date invalide, neașteptate sau pseudo-aleatoare în interfețele unui program, cu scopul principal de a monitoriza comportamentul sistemului la erori (de exemplu, blocaje, excepții neapărate sau scurgeri de memorie - _memory leaks_).

- **Avantaje:** Avantajul major al fuzzing-ului este viteza de execuție și ușurința în implementare. Deoarece nu necesită un model complex al aplicației sau o analiză profundă a codului, fuzzer-ele pot genera și rula milioane de teste pe secundă. Din acest motiv, tehnica a devenit un standard de facto în industria de securitate cibernetică pentru descoperirea vulnerabilităților critice.
    
- **Limitări:** Principala deficiență a testării aleatoare este incapacitatea de a atinge o acoperire a codului (code coverage) ridicată în prezența unor instrucțiuni condiționale specifice. De exemplu, pentru a depăși o condiție de tipul `if (x == 10000)`, probabilitatea ca un generator pur aleatoriu de numere întregi să selecteze exact valoarea `10000` este infinitezimală. Astfel, rute întregi de execuție rămân neexplorate, făcând tehnica ineficientă pentru generarea de teste unitare care să valideze logica fină de business.
    

#### 2.2.2. Testarea bazată pe căutare (Search-Based Software Testing - SBST)

Pentru a depăși caracterul "orb" al generării aleatoare, cercetătorii au formulat problema generării de teste ca pe o problemă de optimizare matematică. Această abordare poartă numele de **Search-Based Software Testing (SBST)** și folosește algoritmi meta-euristici, cum ar fi algoritmii genetici sau _simulated annealing_, pentru a ghida automat căutarea celor mai bune date de intrare [3].

Procesul SBST funcționează iterativ, mimând principiile evoluției naturale:

1. **Inițializarea:** Algoritmul generează o "populație" inițială de cazuri de test complet aleatoare.
    
2. **Evaluarea (Funcția de Fitness):** Fiecare test din populație este rulat, iar o _funcție de fitness_ îi calculează un scor. Acest scor măsoară cât de „aproape” a fost testul de a executa o anumită instrucțiune sau ramură (branch) din cod. De exemplu, pentru condiția `if (x == 10)`, un test cu `x = 12` va primi un scor de fitness mai bun decât un test cu `x = 100`, deoarece diferența (distanța) dintre variabile este mai mică.
    
3. **Evoluția:** Testele cu cele mai bune scoruri sunt selectate, combinate (încrucișare/crossover) și modificate minor (mutație) pentru a forma o nouă generație de teste, sperând că acestea vor depăși ramura dorită.
    

Un exponent major al acestei tehnici este instrumentul **EvoSuite** [3], care generează automat suite de teste JUnit pentru programe scrise în Java, reușind să obțină acoperiri ale codului superioare multor altor tehnici. Cu toate acestea, algoritmii euristici nu garantează găsirea soluției optime. Ei se pot bloca în minime locale și întâmpină dificultăți majore atunci când funcția de fitness nu oferă un ghidaj clar (de exemplu, în manipularea complexă a șirurilor de caractere sau a variabilelor booleene).

#### 2.2.3. Execuția Simbolică (Symbolic Execution)

Cea de-a treia tehnică, și cea mai riguroasă din punct de vedere matematic, este **execuția simbolică**. Spre deosebire de tehnicile anterioare, care execută programul cu valori concrete (de exemplu, `x = 5`), execuția simbolică evaluează programul atribuind variabilelor de intrare valori simbolice (de exemplu, `x = α`).

Pe măsură ce un motor de execuție simbolică parcurge instrucțiunile programului, acesta menține o stare simbolică și construiește o **condiție de cale (path condition - PC)**. Condiția de cale este o formulă logico-matematică ce cumulează toate constrângerile pe care variabilele de intrare trebuie să le respecte pentru ca execuția să urmeze o anumită rută în arborele de control al programului.

- La întâlnirea unei instrucțiuni decizionale (ex: un bloc `if`), motorul de execuție "bifurcă" explorarea: pe o ramură adaugă la PC condiția ca expresia să fie adevărată, iar pe cealaltă ramură adaugă negația acesteia.
    
- Când o cale de execuție se termină, formula logică rezultată este trimisă unui rezolvitor de teoreme de tip **SMT (Satisfiability Modulo Theories)**, cum ar fi Z3. Dacă formula este satisfiabilă, SMT solver-ul returnează valori concrete. Aceste valori garantează matematic că, dacă programul va fi rulat cu ele, va urma exact acea cale de execuție.
    

Un exemplu notabil este **KLEE** [4], un instrument capabil să genereze teste cu acoperire masivă pentru programe complexe scrise în C/C++, analizând codul intermediar LLVM.

Deși oferă garanții formale puternice pe care fuzzing-ul și SBST-ul nu le pot oferi, execuția simbolică se lovește de o problemă fundamentală de scalabilitate: **explozia spațiului de stări (path explosion problem)**. În prezența unor bucle (loops) care depind de date de intrare simbolice, numărul căilor posibile de execuție tinde spre infinit, epuizând rapid memoria și resursele de procesare. Tocmai din acest motiv, combinarea principiilor execuției simbolice cu medii formale riguroase de izolare a stărilor devine o direcție esențială de cercetare.
# Model-based Testing
Tehnicile de generare a testelor analizate anterior (fuzzing, SBST, execuție simbolică) se concentrează preponderent pe analiza directă a codului sursă, o abordare cunoscută sub denumirea de testare _white-box_. Deși eficiente în atingerea unei acoperiri structurale ridicate, aceste metode suferă de o limitare inerentă: ele presupun în mod implicit că logica implementată în cod este cea corectă. Prin urmare, o tehnică de analiză a codului nu poate detecta funcționalități omise (când programatorul a uitat să implementeze o cerință) sau erori fundamentale de design, deoarece instrumentul generează teste doar pentru ceea ce „vede” în implementare.

Pentru a adresa acest neajuns critic, o paradigmă alternativă și complementară a câștigat o tracțiune semnificativă în ingineria software: **Testarea bazată pe modele (Model-Based Testing - MBT)**.

Spre deosebire de tehnicile tradiționale, MBT mută atenția de la implementarea efectivă la specificațiile sistemului. Procesul central implică construirea unui model abstract, formal sau semi-formal, care descrie cu rigurozitate comportamentul așteptat al software-ului. Așa cum subliniază Utting și Legeard [5], în paradigma MBT, acest model matematic acționează ca un „oracol” absolut pentru sistem.

Fluxul de lucru într-un proces MBT clasic implică următoarele etape:

1. **Modelarea:** Inginerul de testare (sau dezvoltatorul) transcrie cerințele sistemului într-un model executabil.
    
2. **Generarea testelor abstracte:** Un instrument automat explorează modelul și, pe baza unor criterii predefinite, generează o suită de cazuri de test la nivel de model (abstracte). Aceste teste conțin pașii de execuție și rezultatele garantat corecte conform specificației [5].
    
3. **Concretizarea:** Deoarece testele abstracte nu pot fi rulate direct pe codul de producție, se utilizează un strat de adaptare (adapter) care translatează instrucțiunile din model în scripturi executabile specifice limbajului țintă (de exemplu, cod Java pentru JUnit sau C# pentru NUnit).
    
4. **Execuția pe SUT:** Testele concrete sunt rulate pe Sistemul sub Test (System Under Test - SUT), iar rezultatele obținute sunt comparate cu predicțiile modelului.
    

#### 2.3.2. Tipuri de modele și criterii de acoperire

Pentru a putea fi analizate automat, modelele utilizate în MBT trebuie să dețină o semantică clar definită. Cele mai frecvente formalisme includ:

- **Sisteme de tranziție a stărilor:** Precum Mașinile cu Stări Finite (FSM) sau Sistemele de Tranziție Etichetate (LTS), care reprezintă sistemul ca un graf orientat în care nodurile sunt stări, iar muchiile sunt acțiuni sau evenimente.
    
- **Specificații algebrice și axiomatice:** Sisteme bazate pe logică matematică și ecuații de rescriere, care definesc stările programului prin intermediul modificărilor aplicate structurilor de date fundamentale (memorie, registre, stivă de apeluri).
    

Spre deosebire de testarea pe cod, generarea testelor în MBT este ghidată de **criterii de acoperire a modelului** (model coverage). Astfel, generatorul poate fi instruit să creeze teste care garantează vizitarea fiecărei stări posibile (_State Coverage_), executarea fiecărei tranziții posibile între stări (_Transition Coverage_) sau parcurgerea unor rute complete de la o stare inițială la una finală (_Path Coverage_).

#### 2.3.3. Avantaje și limitări ale abordării MBT

Adoptarea testării bazate pe modele oferă beneficii substanțiale, în special în dezvoltarea sistemelor critice (safety-critical systems):

- **Detectarea defectelor de design:** Obligativitatea de a formaliza cerințele într-un model matematic forțează inginerii să clarifice ambiguitățile încă din etapele incipiente ale proiectului, identificând erorile de arhitectură înainte de scrierea propriu-zisă a codului de producție [5].
    
- **Independența de platformă și scalabilitatea mentenanței:** Dacă cerințele sistemului se modifică, inginerii trebuie să actualizeze doar modelul abstract. Noua suită de teste (care poate conține mii de cazuri) este regenerată automat. Mai mult, același model poate fi folosit pentru a genera teste pentru multiple implementări în limbaje diferite.
    

Cu toate acestea, obstacolul major în calea adoptării MBT la scară largă, dincolo de mediul academic sau sistemele aerospațiale, este **curba abruptă de învățare**. Construirea unui model care să capteze fidel stările memoriei și logica de control necesită o expertiză solidă în metode formale și logică matematică. De asemenea, la fel ca în cazul execuției simbolice, explorarea exhaustivă a modelelor de mari dimensiuni se lovește frecvent de „explozia spațiului de stări”.

Depășirea acestor limitări necesită utilizarea unor limbaje de specificare înalt optimizate, capabile să execute modele complexe și să gestioneze elegant evaluarea simbolică, domeniu în care logica de rescriere excelează.
# Metode formale și logica de rescriere
În contrast profund cu tehnicile empirice de testare – care, așa cum afirma celebrul informatician Edsger W. Dijkstra, pot demonstra doar prezența erorilor, dar niciodată absența lor – **metodele formale** abordează verificarea software-ului dintr-o perspectivă pur matematică. Acestea utilizează sisteme logice riguroase pentru a specifica, dezvolta și verifica formal comportamentul sistemelor informatice, oferind garanții de corectitudine în raport cu o specificație dată.

#### 2.4.1. Logica de rescriere (Rewriting Logic)

Printre multiplele formalisme disponibile în domeniul metodelor formale, **logica de rescriere (Rewriting Logic)**, introdusă și fundamentată teoretic de José Meseguer [6], s-a impus ca un cadru unificator și extrem de expresiv pentru modelarea sistemelor concurente, distribuite și a semanticii limbajelor de programare.

În logica de rescriere, stările unui sistem sunt reprezentate ca termeni algebrici (structuri de date definite riguros), iar evoluția sistemului – adică dinamica sa – este descrisă printr-un set de **reguli de rescriere**. Spre deosebire de ecuațiile matematice clasice, care denotă egalități statice și deterministe, regulile de rescriere descriu tranziții de stare locale și potențial nedeterministe [6]. Astfel, logica de rescriere este, în esența sa, o logică a schimbării și a concurenței.

#### 2.4.2. Limbajul și sistemul Maude

Pentru a transpune acest formalism matematic într-un instrument practic, a fost dezvoltat **Maude**, un limbaj de specificare declarativ, de înaltă performanță, care implementează nativ logica ecuațională și logica de rescriere. Datorită puterii sale de abstractizare, Maude permite definirea clară și separată a două aspecte fundamentale ale oricărui program sau mașini abstracte:

1. **Semantica statică (Evaluarea deterministă):** Prin intermediul ecuațiilor (declarate în sintaxa limbajului cu `eq` sau `ceq`), Maude simplifică expresiile și evaluează funcțiile matematice deterministe, reducând termenii la forma lor canonică. Aceste ecuații sunt folosite, de exemplu, pentru a defini operațiile de citire sau scriere într-o memorie abstractă.
    
2. **Semantica dinamică (Tranzițiile de stare):** Prin intermediul regulilor (declarate cu `rl` sau `crl`), Maude definește modul în care instrucțiunile unui program modifică starea globală a mașinii abstracte (de exemplu, modificarea stivei de apeluri sau a fluxului de control). Aceste tranziții modelează execuția efectivă a pașilor de program.
    

Această arhitectură face din Maude un instrument excelent pentru definirea semanticii operaționale a limbajelor de programare, oferind un mediu direct executabil pentru modele matematice complexe.

#### 2.4.3. Utilizarea Maude în generarea de teste

Deoarece o specificație Maude este un model executabil, aceasta poate fi supusă mai multor tipuri de analize formale, care stau la baza generării automate a cazurilor de test:

- **Explorarea spațiului de stări (State-space exploration):** Prin comenzi native de căutare (`search`), motorul Maude poate explora exhaustiv toate căile posibile de execuție dintr-un model nedeterminist, identificând stări specifice (de exemplu, stări finale de succes, excepții sau blocaje – _stuck states_).
    
- **Execuția simbolică și mecanismul de _Narrowing_:** O direcție modernă de cercetare utilizează capacitățile avansate ale Maude pentru a executa simbolic programele. Prin înlocuirea valorilor concrete cu variabile simbolice (abstracte), instrumentul deduce constrângerile matematice (condițiile de cale) necesare pentru a atinge o anumită ramură de cod.
    

Validitatea acestei abordări este susținută de literatura de specialitate. Lucrările lui Riesco [7] au demonstrat aplicabilitatea directă a mecanismului de _narrowing_ din Maude pentru generarea automată a cazurilor de test (white-box testing) pe module funcționale, confirmând eficiența logicii de rescriere în explorarea exhaustivă a stărilor programului și în deducerea oracolelor de test.

#### 2.4.4. Prezentarea soluțiilor software consacrate în domeniu

Pentru a contextualiza corect direcția propusă în această lucrare, este esențială trecerea în revistă a câtorva instrumente software majore dezvoltate în mediul academic și adoptate în industrie, bazate pe tehnicile descrise anterior:

- **EvoSuite:** Detaliat de Fraser și Arcuri [3], reprezintă standardul pentru testarea bazată pe căutare (SBST) în Java. Generează automat suite de teste JUnit folosind algoritmi genetici, însă întâmpină dificultăți în rezolvarea blocurilor decizionale cu constrângeri logice severe.
    
- **KLEE:** Dezvoltat de Cadar et al. [4], este un motor de execuție simbolică de referință care operează pe codul intermediar LLVM. Deși excelează în găsirea erorilor critice în programe C/C++ folosind rezolvitori SMT, este puternic limitat de explozia spațiului de stări în programele de mari dimensiuni.
    
- **K Framework:** Prezentat de Roșu și Șerbănuță [8], K Framework este o platformă semantică fundamentată inițial pe logica de rescriere (având rădăcini puternice în Maude). Utilizatorii definesc sintaxa și semantica unui limbaj, iar framework-ul generează automat parsere, interpretoare și verificatoare simbolice. Succesul acestui instrument demonstrează clar că mașinile de stări bazate pe rescriere sunt ideale pentru analiza riguroasă a codului [8].
    
- **Maude Test-Case Generator:** În lucrarea sa [7], Riesco propune un instrument nativ în Maude care automatizează generarea de teste folosind _narrowing_. O distincție fundamentală față de prezenta teză este că instrumentul lui Riesco generează teste exclusiv pentru a valida module funcționale scrise direct în limbajul Maude. În contrast, lucrarea de față propune utilizarea motorului Maude ca un backend formal pentru a analiza și a genera teste pentru un limbaj de programare extern, imperativ.
# Analiză comparativă 

Perfect! Am ajuns la punctul culminant al acestui capitol: **Secțiunile 2.5 și 2.6**. Aici tragem concluziile analizei noastre și, cel mai important, formulăm justificarea științifică pentru existența tezei tale.

Tabelul din secțiunea 2.5 va demonstra comisiei capacitatea ta de sinteză, iar secțiunea 2.6 va defini clar granițele și obiectivele proiectului tău.

Iată draftul detaliat pentru finalul capitolului:

---

### 2.5. Analiză comparativă

Pentru a poziționa corect utilitatea metodelor formale în ecosistemul generării automate de teste, este necesară o evaluare a tehnicilor curente prin prisma a trei metrici esențiale: eficiența descoperirii erorilor, rigoarea acoperirii (coverage) și provocările de implementare. Tabelul 2.1 sintetizează avantajele și limitările abordărilor analizate în secțiunile anterioare:

**Tabelul 2.1:** _Comparație între tehnicile de generare automată a testelor_

|Tehnica de generare|Avantaje principale|Dezavantaje și Limitări|Rigoare / Acoperire|
|---|---|---|---|
|**Fuzzing / Random Testing**|Viteză de execuție extrem de mare; excelentă pentru găsirea vulnerabilităților critice (crashes, excepții).|Ineficientă în depășirea instrucțiunilor condiționale stricte; nu poate valida logica fină de business.|Scăzută (pur statistică, fără garanții pe cod).|
|**Search-Based (SBST)** _(ex: EvoSuite)_|Ghidează inteligent căutarea testelor; acoperire structurală bună pentru limbaje orientate-obiect.|Se poate bloca în minime locale; rezolvă greu constrângeri logico-matematice complexe.|Medie-Ridicată (bazată pe euristici de fitness).|
|**Execuție Simbolică** _(ex: KLEE)_|Fundament matematic; forțează atingerea unor ramuri specifice prin rezolvarea condițiilor de cale cu SMT solvers.|Suferă de explozia spațiului de stări (_path explosion_); scalabilitate redusă pe bucle dependente de input.|Ridicată (garantează acoperirea matematică a rutei).|
|**Model-Based formal** _(ex: Maude)_|Permite abstractizarea la nivel de logică de rescriere; detectează defecte de design; explorare exhaustivă a stărilor.|Necesită expertiză avansată pentru scrierea modelului formal; distanță semantică față de codul executabil.|Foarte Ridicată (verificare exhaustivă pe model).|

Din această analiză reiese un aspect critic al ingineriei software moderne: deși instrumentele comerciale sau bazate pe euristici (precum EvoSuite) sunt extrem de eficiente pentru ciclurile de dezvoltare rapidă (Agile), ele sacrifică adesea rigoarea matematică. Pe de altă parte, instrumentele formale și execuția simbolică oferă garanții superioare de corectitudine, dar nivelul lor ridicat de abstractizare face adesea dificilă translatarea rezultatelor obținute înapoi în teste unitare direct utilizabile de către programatori în mediul lor de dezvoltare obișnuit.
# Identificarea scopului 

Analizând stadiul actual al cunoașterii (State of the Art), se observă existența unui decalaj (research gap) semnificativ între rigoarea analizei formale și pragmatismul ingineriei software de zi cu zi. Instrumentele capabile de explorare simbolică și model checking, cum este Maude, rămân adesea izolate în mediul academic sau în nișa sistemelor critice, rezultatele lor fiind greu de integrat nativ în suitele de testare obișnuite (ex: JUnit, PyTest) ale unor proiecte reale.

Pornind de la această premisă, **scopul principal al acestei teze de disertație** este explorarea, proiectarea și implementarea unui sistem punte: un generator de teste unitare fundamentat pe puterea logicii de rescriere.

Lucrarea de față propune utilizarea motorului Maude nu doar ca instrument de modelare teoretică, ci ca un „backend” de analiză capabil să deducă scenarii de testare pentru un limbaj de programare imperativ (denumit în cadrul acestei lucrări `VENUS`).

**Contribuțiile majore propuse și detaliate în capitolele următoare includ:**

1. **Modelarea formală a semanticii limbajului:** Definirea riguroasă a semanticii operaționale (stare, memorie, stivă de control, evaluarea expresiilor) în limbajul Maude pentru un subset specific de instrucțiuni imperative.
    
2. **Implementarea mecanismelor de explorare simbolică:** Extinderea modelului operațional standard pentru a suporta variabile simbolice. Utilizarea capacităților native Maude de a parcurge ramurile de execuție nedeterministe, construind condiții de cale și deducând datele de intrare și rezultatele așteptate (oracolul de test).
    
3. **Generarea efectivă a codului de test:** Crearea unui mecanism translatabil capabil să preia scenariile (căile de execuție) izolate formal de Maude și să le transpună automat într-un format de test unitar executabil într-un limbaj de programare țintă.
    

Prin această abordare integrată, teza își propune să demonstreze că metodele formale pot fi transformate din concepte pur teoretice în asistenți practici și robuști pentru automatizarea asigurării calității (QA) în dezvoltarea software.

**[1] P. Ammann și J. Offutt, _Introduction to Software Testing_, 2nd ed. Cambridge University Press, 2016.**

- **Tip:** Carte de referință.
    
- **Link oficial carte / Resurse:** [Site-ul oficial al autorilor (George Mason University)](https://cs.gmu.edu/~offutt/softwaretest/) - Aici găsești chiar și slide-uri și capitole rezumate gratuit.
    

**[2] S. Anand et al., „An Orchestrated Survey of Methodologies for Automated Software Test Case Generation,” _Journal of Systems and Software_, vol. 86, no. 8, pp. 1978–2001, 2013.**

- **Tip:** Articol tip "Survey" (un rezumat masiv a tot ce înseamnă generare de teste).
    
- **Link oficial (DOI):** [https://doi.org/10.1016/j.jss.2013.02.061](https://www.google.com/search?q=https://doi.org/10.1016/j.jss.2013.02.061)
    

**[3] G. Fraser și A. Arcuri, „EvoSuite: Automatic Test Suite Generation for Object-Oriented Software,” în _Proceedings of the 19th ACM SIGSOFT Symposium (ESEC/FSE)_, 2011, pp. 416–419.**

- **Tip:** Articol științific (prezentarea tool-ului EvoSuite).
    
- **Link oficial (ACM):** [https://dl.acm.org/doi/10.1145/2025113.2025179](https://dl.acm.org/doi/10.1145/2025113.2025179)
    
- **Site-ul tool-ului (cu documentație):** [https://www.evosuite.org/](https://www.evosuite.org/)
    

**[4] C. Cadar, D. Dunbar, și D. Engler, „KLEE: Unassisted and Automatic Generation of High-Coverage Tests for Complex Systems Programs,” în _8th USENIX Symposium (OSDI)_, 2008, pp. 209–224.**

- **Tip:** Articol științific (baza execuției simbolice moderne).
    
- **Link oficial (PDF Gratuit / Open Access):** [PDF pe site-ul conferinței USENIX](https://www.usenix.org/legacy/events/osdi08/tech/full_papers/cadar/cadar.pdf)
    

**[5] M. Utting și B. Legeard, _Practical Model-Based Testing: A Tools Approach_. Morgan Kaufmann / Elsevier, 2006.**

- **Tip:** Carte (biblia pentru Model-Based Testing).
    
- **Link oficial (ScienceDirect):** [https://www.sciencedirect.com/book/9780123725011/practical-model-based-testing](https://www.sciencedirect.com/book/9780123725011/practical-model-based-testing)
    

**[6] J. Meseguer, „Conditional Rewriting Logic as a Unified Model of Concurrency,” _Theoretical Computer Science_, vol. 96, no. 1, pp. 73–155, 1992.**

- **Tip:** Articolul fundamental (care a inventat logica de rescriere folosită în Maude).
    
- **Link oficial (DOI):** [https://doi.org/10.1016/0304-3975(92)90182-F](https://doi.org/10.1016/0304-3975\(92\)90182-F)
    

**[7] A. Riesco, „Test-Case Generation for Maude Functional Modules,” în _20th International Workshop on Algebraic Development Techniques_, Springer, 2012, pp. 287–301.**

- **Tip:** Articol științific (foarte asemănător cu ce vrei tu să faci, generare de teste cu Maude).
    
- **Link oficial (Springer):** [https://link.springer.com/chapter/10.1007/978-3-642-28412-0_16](https://link.springer.com/chapter/10.1007/978-3-642-28412-0_16)
    
- **Alternativă PDF:** Caută pe Google Scholar titlul exact; adesea autorul ține PDF-ul public pe pagina universității (UCM - Universidad Complutense de Madrid).
    

**[8] G. Roșu și T. F. Șerbănuță, „An Overview of the K Semantic Framework,” _Journal of Logic and Algebraic Programming_, vol. 79, no. 6, pp. 397–434, 2010.**

- **Tip:** Articol științific (prezentarea platformei K, strâns legată de Maude, dezvoltată de prof. Grigore Roșu).
    
- **Link oficial (DOI):** [https://doi.org/10.1016/j.jlap.2010.03.012](https://doi.org/10.1016/j.jlap.2010.03.012)
    
- **Site-ul K Framework:** [https://kframework.org/](https://kframework.org/)