/**
 * Tiene allineato il pulsante "Ordina su WhatsApp" a cio' che il cliente
 * vede a schermo.
 *
 * Lo script non costruisce mai il messaggio. Fa due sole cose:
 *
 *  1. al cambio variante Dawn ri-renderizza la sezione lato server e passa
 *     l'HTML nell'evento variantChange: da li' prendiamo il pulsante gia'
 *     costruito da Liquid per la variante giusta e sostituiamo il nostro;
 *  2. quando cambia la quantita', sostituiamo il segnaposto nel modello.
 *
 * Cosi' il messaggio inviato e quello reso senza JavaScript nascono dallo
 * stesso identico codice Liquid e non possono divergere.
 */
(function () {
  const CTA = '[data-whatsapp-cta]';
  const LINK = '[data-whatsapp-link]';
  const QUANTITA = '.quantity__input';

  /** Quantita' scelta dal cliente, con ripiego prudente su 1. */
  function quantitaScelta(ambito) {
    const campo = ambito && ambito.querySelector(QUANTITA);
    const n = parseInt(campo && campo.value, 10);
    return Number.isFinite(n) && n > 0 ? n : 1;
  }

  /** Riscrive l'href sostituendo il segnaposto della quantita'. */
  function applicaQuantita(cta) {
    if (!cta) return;
    const modello = cta.dataset.modello;
    const segnaposto = cta.dataset.segnaposto;
    const link = cta.querySelector(LINK);
    if (!modello || !segnaposto || !link) return;

    const ambito = cta.closest('product-info') || document;
    link.href = modello.split(segnaposto).join(quantitaScelta(ambito));
  }

  /** Il pulsante appartenente alla sezione indicata. */
  function ctaDellaSezione(sectionId) {
    const info = document.querySelector(
      'product-info[data-section="' + sectionId + '"]'
    );
    return (info || document).querySelector(CTA);
  }

  // 1. Cambio variante: adottiamo il markup ri-renderizzato dal server.
  if (typeof subscribe === 'function' && typeof PUB_SUB_EVENTS !== 'undefined') {
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

  // 2. Cambio quantita'. Delegato sul documento perche' Dawn puo' sostituire
  //    il campo quantita' quando cambiano le regole della variante.
  function alCambioQuantita(evento) {
    const campo = evento.target;
    if (!campo || !campo.matches || !campo.matches(QUANTITA)) return;

    const ambito = campo.closest('product-info') || document;
    applicaQuantita(ambito.querySelector(CTA));
  }

  document.addEventListener('change', alCambioQuantita);
  document.addEventListener('input', alCambioQuantita);

  // 3. Allineamento iniziale: il browser puo' ripristinare una quantita'
  //    diversa da 1 quando si torna indietro nella cronologia.
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll(CTA).forEach(applicaQuantita);
  });
})();
