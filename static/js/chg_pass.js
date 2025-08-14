chg_pass.js

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('btn_enviar_codigo');
    const estado = document.getElementById('estado-codigo');

    function validarEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    btn.addEventListener('click', async (ev) => {
        ev.preventDefault(); /* por si está dentro de un <form> */

        const correo = document.getElementById('correo').value.trim();
        const usuario = document.getElementById('usuario').value.trim();

        if (!validarEmail(correo)) {
            estado.textContent = 'Ingresa un correo válido.';
            estado.style.color = 'red';
            return;
        }

        btn.disabled = true;
        btn.textContent = 'Enviando...';
        estado.textContent = '';

        try {
            const res = await fetch('/enviar_codigo', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ correo, usuario })
            });

            const data = await res.json();
            if (res.ok) {
                estado.textContent = 'Código enviado. Revisa tu correo (vigencia 10 min).';
                estado.style.color = '#c8ffc8';

                let s = 60; // cooldown
                const tick = setInterval(() => {
                    s--;
                    btn.textContent = `Reenviar (${s})`;
                    if (s <= 0) {
                        clearInterval(tick);
                        btn.disabled = false;
                        btn.textContent = 'Reenviar código';
                    }
                }, 1000);
            } else {
                estado.textContent = data.error || 'No se pudo enviar el código.';
                estado.style.color = 'red';
                btn.disabled = false;
                btn.textContent = 'Enviar código';
            }
        } catch (err) {
            estado.textContent = 'Error de red al enviar el código.';
            estado.style.color = 'red';
            btn.disabled = false;
            btn.textContent = 'Enviar código';
        }
    });
});