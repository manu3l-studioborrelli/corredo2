/**
 * Tiene allineato il pulsante "Ordina su WhatsApp" a cio' che il cliente
 * vede a schermo.
 *
 * Lo script non costruisce mai il messaggio. Fa tre sole cose:
 *
 *  1. appena il cliente tocca un'opzione, rende il pulsante inerte: da quel
 *     momento e finche' il server non risponde, l'href in pagina si riferisce
 *     a una variante che non e' piu' quella selezionata;
 *  2. al cambio variante Dawn ri-renderizza la sezione lato server e passa
 *     l'HTML nell'evento variantChange: da li' prendiamo il pulsante gia'
 *     costruito da Liquid per la variante giusta e sostituiamo il nostro,
 *     il che ripristina anche lo stato normale;
 *  3. quando cambia la quantita', sostituiamo il segnaposto nel modello.
 *
 * Cosi' il messaggio inviato e quello reso senza JavaScript nascono dallo
 * stesso identico codice Liquid e non possono divergere.
 *
 * Il punto 1 non e' una raffinatezza. Quando il cliente sceglie una
 * combinazione che non esiste come variante (per esempio Rosso e XL su un
 * prodotto che non li abbina), Dawn imbocca il ramo "if (!variant)" di
 * product-info.js ed esce con un return PRIMA di pubblicare variantChange.
 * Disabilita "Aggiungi al carrello" con la scritta "Non disponibile", ma
 * non tocca nulla di nostro: senza il punto 1 il pulsante verde resterebbe
 * attivo con il link della variante precedente, e in chat arriverebbe
 * l'ordine di un articolo diverso da quello mostrato a schermo. E' il
 * guasto contro cui mette in guardia la nota del §7.1.
 */
(function () {
  const CTA = '[data-whatsapp-cta]';
  const LINK = '[data-whatsapp-link]';
  const QUANTITA = '.quantity__input';
  const IN_ATTESA = 'data-in-attesa';

  /** Quantita' scelta dal cliente, con ripiego prudente su 1. */
  function quantitaScelta(ambito) {
    const campo = ambito && ambito.querySelector(QUANTITA);
    const n = parseInt(campo && campo.value, 10);
    return Number.isFinite(n) && n > 0 ? n : 1;
  }

  /** Riscrive l'href sostituendo il segnaposto della quantita'. */
  function applicaQuantita(cta) {
    // Se il pulsante e' in attesa, il modello si riferisce a una variante
    // che non e' piu' quella scelta: riscrivere l'href lo rimetterebbe
    // attivo con il link sbagliato.
    if (!cta || cta.hasAttribute(IN_ATTESA)) return;

    const modello = cta.dataset.modello;
    const segnaposto = cta.dataset.segnaposto;
    const link = cta.querySelector(LINK);
    if (!modello || !segnaposto || !link) return;

    const ambito = cta.closest('product-info') || document;
    link.href = modello.split(segnaposto).join(quantitaScelta(ambito));
  }

  /**
   * Rende il pulsante inerte finche' il server non conferma la variante.
   * Non tocca il testo: l'etichetta resta quella resa da Liquid, e la
   * spiegazione al cliente e' il "Non disponibile" che Dawn mette sul
   * pulsante del carrello, subito sopra.
   */
  function mettiInAttesa(cta) {
    if (!cta) return;
    const link = cta.querySelector(LINK);
    if (!link) return;

    cta.setAttribute(IN_ATTESA, '');
    link.removeAttribute('href');
    link.setAttribute('aria-disabled', 'true');
    link.setAttribute('tabindex', '-1');
  }

  /** L'elemento product-info che contiene il nodo indicato. */
  function sezioneDi(nodo) {
    return (nodo && nodo.closest && nodo.closest('product-info')) || document;
  }

  /** Il pulsante appartenente alla sezione indicata. */
  function ctaDellaSezione(sectionId) {
    const info = document.querySelector('product-info[data-section="' + sectionId + '"]');
    return (info || document).querySelector(CTA);
  }

  if (typeof subscribe === 'function' && typeof PUB_SUB_EVENTS !== 'undefined') {
    // 1. Il cliente ha toccato un'opzione. Da qui in poi l'href in pagina
    //    e' vecchio: lo spegniamo prima ancora di sapere come andra'.
    subscribe(PUB_SUB_EVENTS.optionValueSelectionChange, function (evento) {
      const dati = evento && evento.data;
      const nodo = (dati && dati.target) || (dati && dati.event && dati.event.target);
      mettiInAttesa(sezioneDi(nodo).querySelector(CTA));
    });

    // 2. Il server ha risposto con una variante valida: adottiamo il markup
    //    ri-renderizzato, che arriva senza lo stato di attesa.
    //    Se la variante non esiste questo evento non arriva mai, e il
    //    pulsante resta spento: e' il comportamento voluto.
    subscribe(PUB_SUB_EVENTS.variantChange, function (evento) {
      const dati = evento && evento.data;
      if (!dati || !dati.html) return;

      const attuale = ctaDellaSezione(dati.sectionId);
      const aggiornato = dati.html.querySelector(CTA);
      if (!attuale || !aggiornato) return;

      attuale.replaceWith(aggiornato);
      applicaQuantita(aggiornato);
    });
  }

  // 3. Cambio quantita'. Delegato sul documento perche' Dawn puo' sostituire
  //    il campo quantita' quando cambiano le regole della variante.
  function alCambioQuantita(evento) {
    const campo = evento.target;
    if (!campo || !campo.matches || !campo.matches(QUANTITA)) return;
    applicaQuantita(sezioneDi(campo).querySelector(CTA));
  }

  document.addEventListener('change', alCambioQuantita);
  document.addEventListener('input', alCambioQuantita);

  // Allineamento iniziale: il browser puo' ripristinare una quantita' diversa
  // da 1 quando si torna indietro nella cronologia. Lo script e' caricato con
  // defer, quindi DOMContentLoaded potrebbe essere gia' scattato: in quel caso
  // si allinea subito.
  function allineaTutti() {
    document.querySelectorAll(CTA).forEach(applicaQuantita);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', allineaTutti);
  } else {
    allineaTutti();
  }
})();
