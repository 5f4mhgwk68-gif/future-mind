(function () {
  var script = document.currentScript;
  var url = script.getAttribute("data-url");
  var panel = document.getElementById("fm-chat");
  var body = document.getElementById("fm-body");
  var form = document.getElementById("fm-form");
  var input = document.getElementById("fm-input");
  var token = form.querySelector("[name=csrfmiddlewaretoken]").value;

  document.getElementById("fm-toggle").addEventListener("click", function () {
    panel.hidden = !panel.hidden;
    if (!panel.hidden) input.focus();
  });
  document.getElementById("fm-close").addEventListener("click", function () {
    panel.hidden = true;
  });

  function push(role, text) {
    var div = document.createElement("div");
    div.className = "msg " + role;
    div.textContent = text;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
  }

  function send(text) {
    if (!text.trim()) return;
    push("user", text);
    input.value = "";
    var data = new FormData();
    data.append("message", text);
    data.append("csrfmiddlewaretoken", token);
    fetch(url, { method: "POST", body: data, headers: { "X-CSRFToken": token } })
      .then(function (r) { return r.json(); })
      .then(function (d) { push("bot", d.reply); })
      .catch(function () { push("bot", "حصل خطأ في الاتصال، حاول مرة أخرى."); });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    send(input.value);
  });

  Array.prototype.forEach.call(document.querySelectorAll(".chat-quick button"), function (b) {
    b.addEventListener("click", function () { send(b.textContent); });
  });
})();
