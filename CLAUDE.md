@AGENTS.md

# Corredo 2 — Documento di progetto

**Studio Borrelli.com** · Manuel Borrelli, Michele Borrelli
Tema Shopify (Dawn) per Corredo 2 — e-commerce con doppio percorso d'acquisto.

|||
|-|-|
|Ultimo aggiornamento|2026-09-07|
|Stato progetto|Setup ambiente|
|Versione tema|0.1.0|
|Store di sviluppo|`corredo2-dev.myshopify.com`|
|Store di produzione|non ancora creato (trasferimento a fine progetto)|

\---

## 0\. Come si usa e si aggiorna questo documento

Questo file è **sia il contesto operativo per Claude Code sia il documento tecnico del progetto**. Non è una descrizione una tantum: descrive lo stato attuale del codice, e se il codice cambia e il documento no, il documento diventa dannoso perché induce in errore.

### Protocollo di aggiornamento — obbligatorio

Al termine di ogni intervento che modifichi il comportamento del sito, aggiorna **nello stesso commit** che contiene la modifica:

1. **§6 Architettura del tema** — se hai aggiunto, rinominato o eliminato file custom
2. **§7 Specifiche funzionali** — se hai cambiato il comportamento di una funzione documentata
3. **§11 Decisioni** — se hai preso una decisione tecnica non ovvia, con la motivazione
4. **§12 Aperto / da fare** — spunta ciò che hai chiuso, aggiungi ciò che hai scoperto
5. **§13 Registro modifiche** — una riga, sempre
6. L'intestazione in cima: data e, se pertinente, stato e versione

Non serve aggiornare per refactor puramente interni che non cambiano né file né comportamento. In dubbio, aggiorna: il costo di una riga in più è nullo, il costo di un documento disallineato è un'ora persa.

### Quando questo file diventa troppo lungo

Quando §13 supera un centinaio di righe, spostalo in `docs/CHANGELOG.md` e lascia qui solo le ultime dieci voci più un rimando. Questo file deve restare leggibile in una sola lettura.

\---

## 1\. Contesto commerciale

Corredo 2 è un'attività al dettaglio con punto vendita fisico. Vende prodotti con varianti (colore, misura) e riceve **circa 5 ordini al giorno**, con scontrino medio intorno ai **20 €** e un margine di circa **10 € per ordine, per un profitto di circa la metà del margine**.

Gli ordini arrivano oggi **via WhatsApp**, gestiti manualmente in chat. Questo canale funziona, genera la totalità del fatturato e **non va sostituito**.

Il pubblico ha **bassa alfabetizzazione digitale**. È il vincolo progettuale più importante del progetto: una parte rilevante dei clienti non completa un checkout con carta su un sito che non conosce, e si blocca davanti a interfacce che diamo per scontate.

### Tesi strategica

Il sito **estende** il flusso WhatsApp esistente, non lo rimpiazza. Fa tre cose che oggi non sono possibili:

1. mostra le varianti in modo leggibile, cosa che il catalogo WhatsApp non sa fare;
2. fa arrivare in chat richieste già complete, riducendo il tempo per ordine;
3. sblocca i tag prodotto su Instagram, che nello Spazio economico europeo richiedono un dominio verificato e rimandano comunque a un sito.

Ogni scelta di interfaccia va valutata contro questa tesi. Se una modifica rende il sito più elegante ma sposta il cliente meno esperto fuori dal percorso WhatsApp, è una modifica sbagliata.

### Soglia economica dichiarata al cliente

L'investimento del primo anno si ripaga con **circa 285 ordini in dodici mesi**, cioè meno di un ordine aggiuntivo al giorno. È il parametro concordato in preventivo e va tenuto presente quando si valuta se una funzione vale il tempo che costa.

\---

## 2\. Perimetro contrattuale

Il cliente ha accettato **tre fasi su cinque**. Le altre saranno valutate a sito pubblicato.

### In perimetro

|Fase|Contenuto|Nota|
|-|-|-|
|1 (ridotta)|Identità visiva|Il cliente **usa il proprio logo esistente**. La fase copre solo normalizzazione file, palette e caratteri|
|2|Prototipo Figma navigabile|Layout approvato prima dello sviluppo|
|3|Sviluppo sito Shopify|Tema, doppia CTA, spedizioni, pagamenti, pagine legali, banner cookie, catalogo Meta, formazione e affiancamento|

Corrispettivo complessivo **1.500 €** in tre tranche.

### Confine sottile da rispettare

Il **catalogo Meta e la verifica del dominio sono in perimetro** (Fase 3), perché servono ad abilitare i tag prodotto su Instagram. 

Allo stesso modo, il **banner cookie va installato e configurato** in Fase 3, ma **non deve avere alcuno script di tracciamento collegato**, perché quegli script appartengono alla Fase 4. Il banner nasce già predisposto e resta inerte fino ad allora.

### Limiti quantitativi del contratto

* Caricamento fino a **30 prodotti** con varianti. Oltre: 4 € cadauno, fuori preventivo
* **Due giri di revisione** inclusi prima della pubblicazione
* **30 giorni** di correzione malfunzionamenti dopo il lancio
* Le **fotografie sono fornite dal cliente**. Non è previsto servizio fotografico
* Le **descrizioni prodotto** sono fornite dal cliente, anche grezze, e le sistemiamo noi. La stesura integrale ex novo è a listino (12 €/scheda)

\---

## 3\. Vincoli di progettazione

Derivano dal punto 1 e valgono per ogni intervento sull'interfaccia.

* **I due percorsi d'acquisto hanno pari dignità.** Nessuno dei due va nascosto, messo in secondo piano o subordinato all'altro
* **Mobile prima di tutto.** Il traffico arriva da Instagram e WhatsApp: si progetta a 360 px e si adatta in su
* **Aree di tocco generose**, minimo 44 × 44 px, con spaziatura sufficiente a evitare tocchi accidentali
* **Testo leggibile senza zoom**: corpo minimo 16 px, contrasto conforme a WCAG AA
* **Niente gergo.** "Ordina su WhatsApp", non "Richiedi preventivo". "Ritiro in negozio", non "Click \& Collect"
* **Prezzo, disponibilità e modalità di consegna visibili senza aprire nulla**
* **Nessun dark pattern**: niente conto alla rovescia finto, niente scarsità inventata, niente iscrizione preselezionata
* **Ogni stringa passa da `locales/it.json`.** Mai testo scritto in chiaro nel Liquid
* Se il JavaScript non parte, la scheda prodotto deve restare **usabile**: prezzo leggibile, entrambi i pulsanti funzionanti sulla prima variante disponibile

\---

## 4\. Stack e ambiente

|Componente|Scelta|Motivo|
|-|-|-|
|Piattaforma|Shopify, piano Basic|Checkout affidabile, varianti native, catalogo Meta integrato, hosting incluso|
|Tema base|Dawn (upstream `Shopify/dawn`)|Tema di riferimento, aggiornabile via `upstream`, adatto a un flusso Git|
|Runtime|Node 20 LTS o superiore|Requisito Shopify CLI|
|CLI|`@shopify/cli` più recente|`theme dev`, `theme check`, `theme push`, `theme pull`|
|Versionamento|Git + GitHub, integrazione nativa Shopify|Sincronizzazione bidirezionale branch ↔ tema|
|Assistenza AI|Claude Code + plugin `shopify-ai-toolkit`|Documentazione Shopify aggiornata invece di Liquid a memoria|

Nessun build step. Niente bundler, niente framework CSS, niente `package.json` per il tema. Dawn è pensato per funzionare senza compilazione e l'integrazione GitHub di Shopify si aspetta i file del tema **nella root del repository**. Introdurre una pipeline di build significa dover mantenere un branch di deploy separato: non ne vale il costo su questo progetto.

### Comandi

```bash
shopify theme dev -e dev        # server locale, hot reload, tema temporaneo invisibile
shopify theme check             # linter, da eseguire prima di ogni commit
shopify theme pull -e dev       # recupera le modifiche fatte dall'editor Shopify
shopify theme push --unpublished  # carica come tema non pubblicato per anteprima
```

`shopify.theme.toml` definisce gli ambienti. Non contiene segreti e va versionato.

\---

## 5\. Repository e flusso di lavoro

L'integrazione GitHub di Shopify collega **un branch a un tema** e sincronizza **nei due sensi**: i commit sul branch aggiornano il tema, e le modifiche fatte dall'editor di Shopify tornano indietro come commit sul branch.

|Branch|Tema collegato|Uso|
|-|-|-|
|`main`|tema live|**Non collegato fino al go-live**|
|`staging`|tema non pubblicato "Anteprima"|Anteprima per cliente e revisioni|
|`feat/<nome>`|nessuno|Lavoro locale, merge su `staging` via PR|

### Regole

* Prima di iniziare a lavorare su un branch collegato: `shopify theme pull`. L'editor potrebbe aver committato nel frattempo
* Un branch, un tema. Mai due branch sullo stesso tema
* Il tema live non è collegato ad alcun branch finché il sito non è pubblicato e approvato
* Commit in italiano, imperativo, con prefisso di area: `scheda prodotto: aggiorna messaggio WhatsApp al cambio variante`

### File da non toccare mai a mano

|File|Perché|
|-|-|
|`config/settings\\\_data.json`|Contiene le impostazioni che il cliente modifica dall'editor. In conflitto vince sempre la versione che arriva da Shopify|
|`assets/\\\*.css` di Dawn non modificati|Sovrascritti dagli aggiornamenti upstream. Le personalizzazioni vanno in un foglio dedicato|

`.gitignore`: `node\\\_modules`, `.shopify`, `.DS\\\_Store`, `\\\*.log`

\---

## 6\. Architettura del tema

> Da aggiornare a ogni aggiunta, rinomina o eliminazione di file custom.

### File custom

|File|Tipo|Scopo|Stato|
|-|-|-|-|
|—|—|Nessun file custom ancora creato|—|

### Modifiche a file Dawn

|File Dawn|Modifica|Motivo|Stato|
|-|-|-|-|
|—|—|—|—|

### Localizzazione

* Lingua predefinita del tema: **italiano**
* File attivo: `locales/it.json`
* `locales/en.default.json` di Dawn: da sostituire come default all'inizio del lavoro, non a fine progetto

\---

## 7\. Specifiche funzionali

### 7.1 Doppia CTA sulla scheda prodotto

È la funzione centrale del progetto e l'unica realmente su misura.

**Comportamento**

Ogni scheda prodotto espone due pulsanti, entrambi visibili senza scorrimento aggiuntivo su schermo mobile:

1. **Aggiungi al carrello** — percorso standard, checkout Shopify, con spedizione o ritiro in negozio
2. **Ordina su WhatsApp** — apre la conversazione con messaggio precompilato

**Costruzione del link**

```
https://wa.me/<numero\\\_internazionale\\\_senza\\\_+>?text=<messaggio\\\_urlencoded>
```

Il messaggio precompilato deve contenere:

* nome del prodotto
* **variante attualmente selezionata**
* quantità selezionata
* URL della scheda prodotto

**Requisiti tecnici**

* Numero di telefono e modello del messaggio esposti come **impostazioni dello schema**, modificabili dall'editor senza intervento dello Studio
* Implementata come snippet richiamato da un blocco della sezione prodotto, non come link scritto a mano nel template
* Il messaggio si **aggiorna via JavaScript al cambio variante**, agganciandosi all'evento di cambio variante del tema
* Con JavaScript disattivato, il link punta comunque a un messaggio valido costruito su `product.selected\\\_or\\\_first\\\_available\\\_variant`
* Il testo del messaggio va codificato per URL, comprese le lettere accentate

**Criteri di accettazione**

* \[ ] Cambiando variante venti volte di seguito, il messaggio riflette sempre la variante mostrata a schermo
* \[ ] Cambiando quantità, il messaggio si aggiorna
* \[ ] Con JavaScript disattivato il link funziona sulla prima variante disponibile
* \[ ] Le lettere accentate arrivano corrette nella chat, non come caratteri illeggibili
* \[ ] Su variante esaurita il comportamento è definito e coerente con quello di "Aggiungi al carrello"
* \[ ] Testato su iOS Safari e Android Chrome, sia con WhatsApp installato sia senza
* \[ ] Il numero è modificabile dall'editor senza toccare il codice

> \\\*\\\*Nota.\\\*\\\* Il disallineamento tra variante mostrata e variante nel messaggio è il guasto più probabile dell'intero progetto e produrrebbe ordini sbagliati in chat. Va verificato a mano prima di ogni consegna al cliente, non solo alla prima implementazione.

### 7.2 Consegna e ritiro

Spedizione e ritiro in negozio sono entrambi attivi. Le condizioni, i tempi e i costi effettivi sono forniti dal cliente e validati dai suoi consulenti.

### 7.3 Pagine legali e banner cookie

Predisposte su modelli professionali: privacy, cookie, condizioni di vendita, resi e recesso, spedizioni. **Il contenuto è soggetto a verifica da parte dei consulenti del cliente**: lo Studio non presta consulenza legale né fiscale e questo è scritto in preventivo.

Il banner cookie è installato e configurato ma **non collegato ad alcuno script di tracciamento** finché non viene attivata la Fase 4.

\---

## 8\. Identità visiva

Il cliente **conserva il proprio logo**. La Fase 1 è ridotta alla normalizzazione dei file e alla definizione di palette e caratteri.

|Elemento|Valore|Stato|
|-|-|-|
|Logo|fornito dal cliente|da normalizzare in vettoriale|
|Colore primario|—|da definire|
|Colore secondario|—|da definire|
|Colore di sfondo|—|da definire|
|Carattere titoli|—|da definire, licenza commerciale obbligatoria|
|Carattere testo|—|da definire, licenza commerciale obbligatoria|

\---

## 9\. Regole per Claude Code

### Fai sempre

* Consulta la documentazione Shopify tramite MCP prima di usare tag o filtri Liquid di cui non sei certo: le API cambiano e la sintassi ricordata a memoria produce codice deprecato
* Esegui `shopify theme check` prima di proporre un commit
* Metti ogni stringa di interfaccia in `locales/it.json`
* Verifica la resa a 360 px prima di dichiarare finita una modifica all'interfaccia
* Aggiorna questo documento secondo il protocollo in §0

### Definizione di "fatto"

Un intervento è concluso quando: il codice funziona sul server locale, `theme check` non segnala errori nuovi, la resa è verificata su viewport mobile, le stringhe sono localizzate, questo documento è aggiornato e il commit contiene entrambe le cose.

\---

## 10\. Sequenza di lavoro

* \[x] Partner account e development store
* \[ ] Repository con Dawn, `staging` collegato a un tema non pubblicato
* \[ ] Ambiente locale, Claude Code, plugin Shopify
* \[ ] Italiano come lingua predefinita del tema
* \[ ] Palette e caratteri da Fase 1 applicati alle impostazioni del tema
* \[ ] Struttura pagine secondo il prototipo Figma approvato
* \[ ] Scheda prodotto con doppia CTA
* \[ ] Configurazione spedizioni e ritiro in negozio
* \[ ] Metodi di pagamento
* \[ ] Pagine legali e banner cookie
* \[ ] Caricamento prodotti (fino a 30)
* \[ ] Catalogo Meta e verifica dominio
* \[ ] Collaudo su dispositivi reali
* \[ ] Due giri di revisione con il cliente
* \[ ] Formazione (90 min) e materiali per il personale
* \[ ] Trasferimento store al cliente, scelta piano, dominio
* \[ ] Collegamento `main` al tema live e pubblicazione
* \[ ] Due sessioni di affiancamento operativo sugli ordini reali

\---

## 11\. Decisioni

Registro delle scelte non ovvie, con la motivazione. Serve a non ridiscutere a distanza di mesi cose già decise, e a spiegarle a chi arriva dopo.

|Data|Decisione|Motivo|
|-|-|-|
|2026-07|Sito con doppia CTA anziché solo WhatsApp|Il catalogo WhatsApp non gestisce le varianti; ogni combinazione sarebbe un articolo separato|
|2026-07|Nessun chatbot|A 5 ordini al giorno l'automazione costa più del lavoro che sostituisce|
|2026-07|Instagram Shopping richiede il sito|Nello Spazio economico europeo i tag prodotto rimandano al sito e richiedono dominio verificato|
|2026-09|Shopify anziché piattaforma autogestita|Hosting, sicurezza e aggiornamenti inclusi: nessun canone di manutenzione tecnica separato|
|2026-09|Dawn anziché tema a pagamento|I temi premium sono pesanti, i loro aggiornamenti sovrascrivono le personalizzazioni e mal si conciliano con un flusso Git|
|2026-09|Sviluppo su development store, trasferimento a fine progetto|Il cliente non paga l'abbonamento durante i due mesi di sviluppo|
|2026-09|Nessun build step nel tema|L'integrazione GitHub vuole i file del tema nella root; una pipeline imporrebbe un branch di deploy separato|

\---

## 12\. Aperto / da fare

### Da chiarire con il cliente

* \[ ] Numero WhatsApp definitivo da usare nella CTA (aziendale, non personale)
* \[ ] Costi e tempi di spedizione effettivi, e condizioni di reso, validati dai loro consulenti
* \[ ] Elenco definitivo dei prodotti da caricare e verifica che stiano nei 30 inclusi
* \[ ] Dominio: da acquistare 
* \[ ] Dati aziendali completi per le pagine legali

### Da decidere internamente

* \[ ] Peso visivo relativo dei due pulsanti: pari dignità è il vincolo, la resa concreta va provata sul prototipo
* \[ ] Comportamento della CTA WhatsApp su variante esaurita
* \[ ] Testo predefinito del messaggio WhatsApp

### Emerso durante lo sviluppo, fuori perimetro

Annotare qui ciò che si scopre e che non va implementato ora, così è pronto per la valutazione delle Fasi 4 e 5.

* *(nessuna voce)*

\---

## 13\. Registro modifiche

Una riga per ogni intervento. Formato: data, area, cosa è cambiato, perché.

|Data|Area|Modifica|Motivo|
|-|-|-|-|
|2026-09-07|progetto|Creazione del documento di progetto|Avvio sviluppo dopo accettazione del preventivo|



