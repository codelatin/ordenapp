(() => {
  'use strict';
  const byId = id => document.getElementById(id);
  const button = byId('notification-bell');
  if (!button) return;
  const panel = byId('notification-panel');
  const badge = byId('notification-badge');
  const label = byId('notification-summary');
  const items = byId('notification-items');
  const toast = byId('global-bulletin-toast');
  const endpoint = '/notificaciones/estado/';
  let socket = null;
  let delay = 1000;
  let reconnectTimer = null;
  let lastSnapshot = null;
  let active = true;

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function renderRows(target, recent, compact) {
    if (!target) return;
    target.replaceChildren();
    if (!recent.length) {
      target.append(el('p','notification-empty','No tienes comunicados recibidos todavía.'));
      return;
    }
    for (const record of recent) {
      const a = el('a', 'notification-row' + (record.confirmed ? ' confirmed' : (!record.read ? ' unread' : '')));
      a.href = record.url;
      const info = el('span','notification-row-text');
      info.append(el('strong','',record.title));
      info.append(el('small','', 'De ' + record.sender + ' · ' + (record.confirmed ? 'Confirmado' : (record.read ? 'Leído · por confirmar' : 'Sin leer'))));
      a.append(info, el('span','notification-row-arrow','↗'));
      target.append(a);
    }
  }
  function value(id, n) { const node = byId(id); if (node) node.textContent = String(n); }
  function render(snapshot) {
    lastSnapshot = snapshot;
    const pending = snapshot.unread_bulletins || 0;
    badge.textContent = pending > 99 ? '99+' : String(pending);
    badge.hidden = !pending;
    label.textContent = pending + ' sin leer · ' + snapshot.pending_confirmation + ' pendientes de confirmar';
    renderRows(items, snapshot.recent);
    value('dash-unread-bulletins', pending);
    value('dash-pending-confirm', snapshot.pending_confirmation);
    value('dash-pending-recipients', snapshot.recipient_confirmations_pending);
    renderRows(byId('dashboard-notification-list'), snapshot.recent);
  }
  async function refresh() {
    try {
      const resp = await fetch(endpoint, { credentials:'same-origin', cache:'no-store', headers:{'Accept':'application/json'} });
      if (resp.status === 401 || resp.status === 403 || resp.redirected) return;
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      render(await resp.json());
    } catch (e) {
      const status = byId('notification-connection');
      if (status) status.textContent = 'SIN SINCRONIZAR';
    }
  }
  function online(connected) {
    const status = byId('notification-connection');
    const dashboardStatus = byId('dash-live-status');
    if (status) status.textContent = connected ? 'EN LÍNEA' : 'RECONECTANDO';
    if (dashboardStatus) dashboardStatus.textContent = connected ? '● EN LÍNEA' : '○ RECONECTANDO';
  }
  function toastMessage(message) {
    if (!toast) return;
    toast.replaceChildren();
    toast.append(el('span','',message + ' '));
    const a = el('a','notification-toast-link','ABRIR COMUNICADOS ↗');
    a.href = '/comunicados/';
    toast.append(a);
    toast.hidden = false;
    // El usuario puede cerrar el aviso sin perder las notificaciones guardadas.
    let close = byId('notification-toast-close');
    if (!close) { close = el('button','notification-toast-close','×'); close.id='notification-toast-close'; close.type='button'; close.addEventListener('click', () => { toast.hidden=true; }); toast.append(close); }
    else toast.append(close);
  }
  function connect() {
    if (!active) return;
    const scheme = location.protocol === 'https:' ? 'wss:' : 'ws:';
    socket = new WebSocket(scheme + '//' + location.host + '/ws/bulletins/');
    socket.addEventListener('open', () => { delay = 1000; online(true); refresh(); });
    socket.addEventListener('message', event => {
      let data;
      try { data = JSON.parse(event.data); } catch (_) { return; }
      if (data.event === 'new_bulletin' || data.bulletin) {
        const title = (data.bulletin && data.bulletin.title) || 'Nuevo comunicado';
        toastMessage('Nuevo comunicado: ' + title);
      }
      if (data.event === 'new_bulletin' || data.event === 'bulletin_progress' || data.bulletin) refresh();
    });
    socket.addEventListener('close', () => {
      online(false);
      if (active) { clearTimeout(reconnectTimer); reconnectTimer = setTimeout(connect, delay); delay = Math.min(delay * 2, 15000); }
    });
    socket.addEventListener('error', () => socket.close());
  }
  button.addEventListener('click', () => {
    const show = panel.hidden;
    panel.hidden = !show;
    button.setAttribute('aria-expanded', String(show));
    if (show) refresh();
  });
  document.addEventListener('click', event => {
    if (panel.hidden || byId('notification-control').contains(event.target)) return;
    panel.hidden = true;
    button.setAttribute('aria-expanded','false');
  });
  document.addEventListener('visibilitychange', () => { if (!document.hidden) refresh(); });
  window.addEventListener('beforeunload', () => { active = false; clearTimeout(reconnectTimer); if (socket) socket.close(); });
  refresh();
  connect();
})();
