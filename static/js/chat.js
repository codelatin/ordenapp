const otherId = JSON.parse(document.getElementById('other-id').textContent);
const chat = document.getElementById('chat');
const form = document.getElementById('message-form');
const input = document.getElementById('message-input');
const send = document.getElementById('send');
const status = document.getElementById('status');
const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
const socket = new WebSocket(`${protocol}://${location.host}/ws/chat/${otherId}/`);
const currentId = Number(chat.dataset.currentUser);
function appendMessage(message) {
  if (document.querySelector(`[data-message-id="${message.id}"]`)) return;
  const div = document.createElement('div');
  div.dataset.messageId = message.id;
  div.className = 'bubble ' + (message.sender_id === currentId ? 'mine' : 'theirs');
  const name = document.createElement('small'); name.className = 'd-block fw-semibold'; name.textContent = message.sender;
  const body = document.createElement('span'); body.className = 'message-text'; body.textContent = message.body;
  div.append(name, body); chat.append(div); chat.scrollTop = chat.scrollHeight;
}
socket.onopen = () => { status.textContent = 'Conectado en tiempo real'; send.disabled = false; };
socket.onclose = () => { status.textContent = 'Conexión cerrada. Actualiza la página.'; send.disabled = true; };
socket.onerror = () => { status.textContent = 'Error de conexión WebSocket.'; };
socket.onmessage = event => { const data = JSON.parse(event.data); if(data.error) status.textContent = data.error; if(data.message) appendMessage(data.message); };
form.addEventListener('submit', event => {
  event.preventDefault(); const body = input.value.trim(); if (!body || socket.readyState !== WebSocket.OPEN) return;
  socket.send(JSON.stringify({body})); input.value = '';
});
chat.scrollTop = chat.scrollHeight;
