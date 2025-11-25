// Logique de l'application frontend
const apiUrl = 'http://localhost:5000/api'; // URL de l'API backend
let token = null;

// ... (le reste du code JavaScript pour la logique du frontend)
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const authContainer = document.getElementById('auth-container');
    const notesContainer = document.getElementById('notes-container');
    const logoutBtn = document.getElementById('logout-btn');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch(`${apiUrl}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            if (response.ok) {
                const data = await response.json();
                token = data.token;
                authContainer.style.display = 'none';
                notesContainer.style.display = 'block';
                loadNotes();
            } else {
                alert('Échec de la connexion');
            }
        } catch (error) {
            console.error('Erreur de connexion:', error);
            alert('Une erreur est survenue lors de la connexion.');
        }
    });

    logoutBtn.addEventListener('click', () => {
        token = null;
        authContainer.style.display = 'block';
        notesContainer.style.display = 'none';
        document.getElementById('notes-list').innerHTML = '';
    });

    // Le reste de la logique pour charger et ajouter des notes...
});

async function loadNotes() {
    // ...
}
