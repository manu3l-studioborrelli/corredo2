@AGENTS.md

# Corredo 2 — Documento di progetto

**Studio Borrelli.com** · Manuel Borrelli, Michele Borrelli
Tema Shopify (Dawn) per Corredo 2 — e-commerce con doppio percorso d'acquisto.

|||
|-|-|
|Ultimo aggiornamento|2026-09-08|
|Stato progetto|Sviluppo — base Dawn in italiano, doppia CTA realizzata|
|Versione tema|0.2.0|
|Store di sviluppo|`corredo-2-bhrhuy2x.myshopify.com`|
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
|Tema base|**Dawn 16.0.0** (upstream `Shopify/dawn`)|Tema di riferimento, aggiornabile via `upstream`, adatto a un flusso Git|
|Runtime|Node 20 LTS o superiore (in uso: 24.14.0)|Requisito Shopify CLI|
|CLI|`@shopify/cli` più recente (in uso: 4.7.1)|`theme dev`, `theme check`, `theme push`, `theme pull`|
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

### Baseline di Theme Check

Dawn 16.0.0 non è pulito di suo: `shopify theme check` segnala **0 errori e 11 warning** ereditati, fra cui sei falsi positivi `UndefinedObject` su `section` dentro gli snippet e su `scheme_classes` nei layout. Il §9 chiede che non compaiano rilievi **nuovi**, non che il conteggio sia zero. Quando serve confrontare:

```bash
shopify theme check --output json > dopo.json
```

e si confrontano coppia regola/file con la baseline.

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

Tema base: **Dawn 16.0.0**, agganciato al remote `upstream` (`Shopify/dawn`). Il merge iniziale conserva `upstream/main` come genitore, quindi gli aggiornamenti si applicano con un normale `git merge upstream/main`.

### File custom

|File|Tipo|Scopo|Stato|
|-|-|-|-|
|`snippets/whatsapp-cta.liquid`|snippet|Costruisce il link `wa.me` e il messaggio precompilato. Unica fonte di verità del messaggio|fatto|
|`assets/whatsapp-cta.js`|script|Allinea il pulsante a variante e quantità. Non ricostruisce mai il messaggio|fatto|
|`assets/component-whatsapp-cta.css`|foglio di stile|Stili della CTA. Foglio dedicato come impone il §5|fatto|
|`assets/icon-whatsapp.svg`|icona|Glifo WhatsApp, `currentColor`|fatto|
|`.github/workflows/theme-check.yml`|CI|Esegue Theme Check a ogni push e PR|fatto|

### Modifiche a file Dawn

|File Dawn|Modifica|Motivo|Stato|
|-|-|-|-|
|`sections/main-product.liquid`|Blocco `whatsapp_cta` (limite 1) e relativo ramo `when`|Punto di innesto della CTA, §7.1|fatto|
|`templates/product.json`|Blocco attivo subito dopo `buy_buttons`; checkout accelerato spento|Le due CTA devono stare vicine e visibili insieme, e restare entrambe piene, §3|fatto|
|`config/settings_schema.json`|Gruppo «WhatsApp»: numero e due messaggi|Il §7.1 vuole il numero modificabile dall'editor|fatto|
|`locales/it.default.schema.json`|4 nomi di sezione accorciati sotto i 25 caratteri|Le traduzioni ufficiali Shopify sforavano il limite e producevano errori Theme Check|fatto|
|`templates/*.json`, `sections/header-group.json`|9 stringhe di vetrina tradotte|Restavano in inglese fuori da `locales`|fatto|
|`.github/`|Rimossa l'automazione del repository pubblico Shopify|`cla.yml` e `stale.yml` agirebbero contro di noi|fatto|

### Localizzazione

* Lingua predefinita del tema: **italiano**
* File attivi: `locales/it.default.json` e `locales/it.default.schema.json`
* L'inglese resta come lingua secondaria in `locales/en.json` e `locales/en.schema.json`
* Shopify ammette **un solo** file `*.default.json` per tipo: la lingua predefinita si cambia rinominando, non con un'impostazione
* La traduzione italiana di Dawn è completa: zero chiavi mancanti su 383 stringhe di vetrina e 1141 di editor
* Chiavi custom sotto lo spazio `whatsapp.*`, con nomi in inglese come tutte le altre di Dawn e valori in italiano

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

**Tre stati del pulsante, non due**

Vanno distinti, perché Dawn li tratta in modo diverso:

|Stato|Cosa vede il cliente|Come è ottenuto|
|-|-|-|
|Variante acquistabile|«Ordina su WhatsApp», messaggio d'ordine|Reso da Liquid|
|Variante esistente ma esaurita|«Chiedi su WhatsApp», messaggio «quando torna disponibile»|Reso da Liquid: la variante non è nulla, Dawn pubblica `variantChange` normalmente|
|Combinazione che **non esiste** come variante|Pulsante visibile ma inerte e attenuato|Lo script lo spegne al tocco sull'opzione e nessun evento lo riaccende|

Il terzo caso è il più insidioso. Se il cliente sceglie Rosso e poi XL su un prodotto che non abbina quei due valori, Dawn imbocca il ramo `if (!variant)` di `product-info.js` ed esce con un `return` **prima** di pubblicare `variantChange`. Disabilita «Aggiungi al carrello» con «Non disponibile», ma non tocca nulla di custom. Senza contromisura il pulsante WhatsApp resterebbe attivo con il link della variante precedente, e in chat arriverebbe l'ordine di un articolo diverso da quello a schermo: esattamente il guasto della nota qui sotto. Per questo lo script si aggancia anche a `optionValueSelectionChange`, che Dawn pubblica **prima** della richiesta al server, e spegne il pulsante in attesa di conferma. Chi tocca `assets/whatsapp-cta.js` non rimuova quell'aggancio.

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
* \[~] Repository con Dawn — repository e Dawn 16.0.0 a posto; restano il remote GitHub e il branch `staging` collegato a un tema non pubblicato
* \[~] Ambiente locale, Claude Code, plugin Shopify — Node e CLI a posto; il plugin MCP `shopify-ai-toolkit` **non è ancora collegato**
* \[x] Italiano come lingua predefinita del tema
* \[ ] Palette e caratteri da Fase 1 applicati alle impostazioni del tema
* \[ ] Struttura pagine secondo il prototipo Figma approvato
* \[x] Scheda prodotto con doppia CTA — da ricollaudare su dispositivi reali prima della consegna
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
|2026-09-08|Dawn 16.0.0 al posto dello Skeleton Theme che era stato clonato|Skeleton è un kit per sviluppatori: 3 snippet, nessun carrello, nessun selettore varianti, solo inglese. Dawn porta 39 snippet, 48 sezioni e la traduzione italiana ufficiale completa. A 1.500 € ricostruire un negozio da zero non sta nel preventivo|
|2026-09-08|Merge con `--allow-unrelated-histories` invece di ripartire da un clone|Tiene `upstream/main` come genitore: gli aggiornamenti Dawn si applicano con un normale `git merge`, come chiede il §4|
|2026-09-08|Il messaggio WhatsApp nasce **solo** dal Liquid|Dawn ri-renderizza la sezione lato server al cambio variante e passa l'HTML nell'evento. Prendendo il pulsante da lì, il messaggio inviato e quello reso senza JavaScript sono lo stesso codice e non possono divergere: è il guasto contro cui mette in guardia la nota del §7.1|
|2026-09-08|Quantità gestita con un segnaposto alfabetico dentro l'URL già codificato|`url_encode` lo attraversa immutato e lo script fa una sola sostituzione letterale. Evita un secondo codificatore in JavaScript, che diverge sempre su accenti e spazi|
|2026-09-08|Numero e messaggi come impostazioni **globali**, non del blocco|Il numero è uno solo per il negozio: va cambiato in un posto solo, non in ogni scheda prodotto|
|2026-09-08|Nessun valore predefinito nelle impostazioni WhatsApp|A campo vuoto lo snippet ripiega sulle stringhe di `locales`, così nessun testo italiano finisce scritto in chiaro fuori dai file di localizzazione (§3)|
|2026-09-08|Verde `#107C6E` invece del verde del marchio `#25D366`|Il verde WhatsApp su bianco dà circa 2,1:1 e non passa il WCAG AA imposto dal §3. Questo dà 5,1:1 restando riconoscibile|
|2026-09-08|Rimossa la cartella `.github` di Dawn|È l'automazione del repository pubblico Shopify: `cla.yml` chiederebbe di firmare il CLA a ogni PR e `stale.yml` chiuderebbe le nostre issue. Sostituita con il solo Theme Check|
|2026-09-08|Il pulsante WhatsApp si spegne al tocco sull'opzione e si riaccende solo con la risposta del server|Dawn non pubblica `variantChange` quando la combinazione scelta non esiste come variante: esce prima con un `return`. Spegnere in anticipo è l'unico modo per non lasciare in pagina un link che ordina l'articolo sbagliato. Lo stato si scioglie da sé quando la variante esiste, perché il markup ri-renderizzato arriva pulito. Se la richiesta al server fallisce il pulsante resta spento, che è il modo giusto di rompersi|
|2026-09-08|Disattivato il checkout accelerato (`show_dynamic_checkout: false`) sulla scheda prodotto|Con l'impostazione attiva Dawn assegna ad «Aggiungi al carrello» la classe `button--secondary`, che si riempie con il **colore di sfondo** dello schema: diventa un pulsante in outline mentre quello WhatsApp resta pieno. Il percorso WhatsApp dominava visivamente, che è esattamente il «subordinato all'altro» vietato dal §3. Spento anche perché al pubblico del §1 un terzo pulsante di pagamento accelerato aggiunge confusione. **Da confermare**: è un click nell'editor per riattivarlo, ma allora va rivisto anche il foglio di stile|

\---

## 12\. Aperto / da fare

### Da chiarire con il cliente

* \[ ] Numero WhatsApp definitivo da usare nella CTA (aziendale, non personale)
* \[ ] Costi e tempi di spedizione effettivi, e condizioni di reso, validati dai loro consulenti
* \[ ] Elenco definitivo dei prodotti da caricare e verifica che stiano nei 30 inclusi
* \[ ] Dominio: da acquistare 
* \[ ] Dati aziendali completi per le pagine legali

### Da decidere internamente

* \[~] Peso visivo relativo dei due pulsanti — stessa larghezza, stessa altezza (48 px), stesso corpo (16 px), entrambi **pieni**, colore diverso. La parità si regge anche sul checkout accelerato spento: se lo si riattiva, «Aggiungi al carrello» torna in outline e la parità salta. Da provare sul prototipo
* \[~] Comportamento della CTA WhatsApp su variante esaurita — realizzato, distinguendo i tre stati descritti nel §7.1. Su variante **esistente ma esaurita** il pulsante resta attivo e il messaggio diventa «quando torna disponibile»: su cinque ordini al giorno con negozio fisico quella richiesta vale. Su **combinazione inesistente** il pulsante si spegne. **Da confermare il primo caso**, il secondo non è opinabile
* \[~] Testo predefinito del messaggio WhatsApp — realizzato un default in `locales`, sovrascrivibile dall'editor. **Da confermare**
* \[ ] Corpo del testo di Dawn: `body` è a **15 px**, il §3 ne chiede 16 come minimo. Sui due pulsanti della scheda prodotto è già corretto, ma la scelta va presa per tutto il tema, insieme a palette e caratteri della Fase 1. Si può agire sull'impostazione «scala del corpo del testo» invece che sui CSS
* \[ ] Riabilitare `MatchingTranslations` in `.theme-check.yml`: Dawn la disattiva perché spedisce 25 lingue che restano indietro, ma a noi servono due lingue sole e la regola intercetterebbe le chiavi mancanti

### Setup ancora da completare

* \[ ] Remote GitHub e branch `staging` collegato a un tema non pubblicato (§5). Oggi il repository è solo locale
* \[ ] Collegare il plugin MCP `shopify-ai-toolkit`, che AGENTS.md dà per obbligatorio. Va autorizzato da una sessione interattiva
* \[ ] Impostare numero WhatsApp e messaggi dall'editor: senza numero il pulsante **non compare**, per scelta

### Emerso durante lo sviluppo, fuori perimetro

Annotare qui ciò che si scopre e che non va implementato ora, così è pronto per la valutazione delle Fasi 4 e 5.

* *(nessuna voce)*

\---

## 13\. Registro modifiche

Una riga per ogni intervento. Formato: data, area, cosa è cambiato, perché.

|Data|Area|Modifica|Motivo|
|-|-|-|-|
|2026-09-07|progetto|Creazione del documento di progetto|Avvio sviluppo dopo accettazione del preventivo|
|2026-09-08|repository|Inizializzato Git sullo stato di partenza|Il §5 descrive un flusso a branch, ma il repository non era versionato|
|2026-09-08|tema|Sostituito lo Skeleton Theme con Dawn 16.0.0|Era stato clonato il repository sbagliato: il §4 e il §11 stabiliscono Dawn|
|2026-09-08|localizzazione|Italiano come lingua predefinita, 4 nomi di sezione accorciati|Requisito del §6. Le traduzioni ufficiali sforavano il limite di 25 caratteri e producevano errori Theme Check|
|2026-09-08|repository|Rimossa l'automazione GitHub di Dawn, aggiunto il solo Theme Check|`cla.yml` e `stale.yml` avrebbero agito contro le nostre PR e issue|
|2026-09-08|scheda prodotto|Realizzata la doppia CTA «Ordina su WhatsApp» (§7.1)|Funzione centrale del progetto|
|2026-09-08|contenuti|Tradotte 9 stringhe di vetrina rimaste in inglese|Fuori da `locales`, il cliente le vedeva in inglese|
|2026-09-08|scheda prodotto|Correzioni da audit: nota portata a 16 px, checkout accelerato spento, altre 2 stringhe tradotte|Un esame indipendente ha trovato una violazione del corpo minimo, la parità dei pulsanti che non si realizzava e due stringhe inglesi che il primo controllo aveva perso|
|2026-09-08|scheda prodotto|Il pulsante WhatsApp si spegne su combinazione di opzioni inesistente|Dawn esce prima di pubblicare `variantChange`: il pulsante restava attivo con il link della variante precedente e avrebbe mandato in chat ordini sbagliati. È il guasto previsto dalla nota del §7.1, trovato da due lenti indipendenti e confermato da due scettici|



