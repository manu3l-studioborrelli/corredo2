# Contenuti delle pagine — pronti da incollare

Le pagine di Shopify **non sono file del tema**: si creano nell'admin. Questo file
raccoglie i testi già scritti, così il caricamento è un copia-incolla.

Registro: dare del tu, frasi corte, niente gergo (§3). Il pubblico del §1 ha bassa
alfabetizzazione digitale: ogni frase deve dire una cosa sola.

---

## 1. Policy legali — `Impostazioni → Policy`

**Non sono Pagine.** Stanno in `Impostazioni → Policy` e Shopify le collega da sé nel
footer: `sections/footer.liquid` cicla `shop.policies`, quindi **non vanno aggiunte al
menu del footer**, si duplicherebbero.

Shopify offre un generatore per ciascuna: `Impostazioni → Policy → Crea da modello`.

| Policy | Nota |
|-|-|
| Informativa sulla privacy | Genera da modello, poi inserisci i dati aziendali |
| Politica di rimborso | Deve riportare i **14 giorni** di recesso previsti dal Codice del consumo |
| Termini e condizioni | Genera da modello |
| Politica di spedizione | Tempi e costi reali, forniti dal cliente |

> **Il contenuto va verificato dai consulenti del cliente.** Lo Studio non presta
> consulenza legale né fiscale, ed è scritto in preventivo (§7.3). I modelli di
> Shopify sono un punto di partenza, non un parere.

L'**informativa cookie** è invece una **Pagina** normale, non una Policy: Shopify non
ne prevede una fra le quattro. Va creata come pagina e collegata dal banner cookie.

---

## 2. Come ordinare su WhatsApp

`Contenuti → Pagine → Aggiungi pagina`. Titolo: **Come ordinare su WhatsApp**

> È la pagina a più alto rendimento del progetto: è l'unica che difende la tesi del §1
> fuori dalla scheda prodotto. Mettila nel menu principale.

```
Ordinare da noi è semplice come mandare un messaggio.

## 1. Scegli quello che ti serve
Apri il prodotto che ti interessa. Se ci sono colori o misure, scegli quelli
giusti prima di andare avanti.

## 2. Tocca il pulsante verde
Sul prodotto trovi il pulsante "Ordina su WhatsApp". Toccalo.

## 3. Invia il messaggio già scritto
Ti si apre WhatsApp con il messaggio già pronto: c'è il nome del prodotto, il
colore, la misura e la quantità. Non devi scrivere niente, tocca solo invia.
Se vuoi aggiungere qualcosa, puoi farlo prima di inviare.

## 4. Ti rispondiamo noi
Ti risponde una persona del negozio, non un risponditore automatico.
Ti confermiamo la disponibilità e ci mettiamo d'accordo su pagamento e consegna.

---

## Preferisci non usare WhatsApp?

Su ogni prodotto c'è anche "Aggiungi al carrello": ordini dal sito, paghi online
e scegli se ricevere a casa o ritirare in negozio. I due modi valgono uguale,
scegli quello con cui ti trovi meglio.

## Domande frequenti

**Devo avere WhatsApp installato?**
No. Se non ce l'hai, il pulsante apre WhatsApp nel browser.

**Pago subito?**
No. Con WhatsApp ci accordiamo prima, poi decidi come pagare.

**Posso ritirare in negozio?**
Sì, e non paghi la spedizione. Diccelo nel messaggio.
```

---

## 3. Contatti

`Contenuti → Pagine`. Titolo: **Contatti** — template: **page.contact** (esiste già in Dawn,
monta anche il modulo di contatto).

```
Siamo un negozio vero e ci trovi qui.

**Indirizzo**
[via e numero]
[CAP] [città] ([provincia])

**Telefono e WhatsApp**
[numero]

**Orari**
Lunedì–Sabato, [orario]
Domenica chiuso

Se hai un dubbio su una misura o su un tessuto, scrivici: è il modo più veloce
per avere una risposta.
```

---

## 4. Il negozio

`Contenuti → Pagine`. Titolo: **Il negozio**. Serve **foto vere** del punto vendita: per il
cliente diffidente del §1 sono la prova che esisti.

```
Da [anno] vendiamo corredo, biancheria per la casa e abbigliamento a [città].

Chi entra da noi di solito cerca un consiglio prima di un prodotto: quale misura
per quel letto, quale tessuto per l'estate, cosa regalare per un matrimonio.
Quel consiglio continuiamo a darlo, anche da qui.

Il sito serve a farti vedere quello che abbiamo, con i colori e le misure scritti
chiari. Poi scegli tu: ordini online, oppure ci scrivi su WhatsApp come hai
sempre fatto.
```

---

## 5. Domande frequenti

> **Da fare per ultima, e solo con il cliente.** Le domande vere sono quelle che
> arrivano ogni giorno in chat. Una FAQ inventata da noi non serve a nessuno:
> chiedi al cliente le dieci domande che riceve più spesso, quelle sono il contenuto.

Struttura consigliata: ordini e pagamenti, spedizione e ritiro, misure e taglie,
cambi e resi.

---

## 6. Menu — `Contenuti → Menu`

**Menu principale: massimo cinque voci, tutte piatte.** I sottomenu a tendina sono la
prima cosa che si rompe su un telefono e il pubblico del §1 non li apre.

```
Lenzuola e biancheria    → collezione
Abbigliamento            → collezione
Intimo                   → collezione
Come ordinare            → pagina
Contatti                 → pagina
```

**Menu footer:**

```
Come ordinare   → pagina
Il negozio      → pagina
Contatti        → pagina
Cookie          → pagina
```

Le quattro policy legali **non** vanno qui: le aggiunge Shopify da sola.

---

## 7. Collezioni — `Prodotti → Collezioni`

**Quattro o cinque piene, non otto vuote.** Una collezione con due prodotti fa
sembrare il negozio più povero di quanto sia.

| Collezione | Condizione automatica |
|-|-|
| Lenzuola e biancheria | Tipo di prodotto = `Lenzuola` |
| Spugna e asciugamani | Tipo di prodotto = `Spugna` |
| Intimo uomo | Tipo di prodotto = `Intimo uomo` |
| Abbigliamento | Tipo di prodotto = `Abbigliamento uomo` |

Usa collezioni **automatiche** basate sul tipo di prodotto: si popolano da sole quando
carichi merce nuova, senza doverci tornare sopra.

Serve anche una collezione **ZZ Prova** (manuale) per i prodotti fittizi, così si
cancellano in blocco.
