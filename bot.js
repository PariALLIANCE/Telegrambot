const TelegramBot = require('node-telegram-bot-api');

// Import dynamique de node-fetch (solution ESM)
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

// Tokens depuis GitHub Secrets
const token = process.env.TELEGRAM_BOT_TOKEN;
const groqApiKey = process.env.GROQ_API_KEY;

// Canal Telegram
const canal = '@PariALLIANCE';

// Fonction qui génère un message complet (motivation + promo AFROPARI)
async function generateDailyMessage() {
  // Date du jour formatée
  const today = new Date();
  const day = today.getDate();
  const month = today.toLocaleString('fr-FR', { month: 'long' });
  const year = today.getFullYear();
  const formattedDate = `${day} ${month} ${year}`;

  const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${groqApiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: "meta-llama/llama-4-maverick-17b-128e-instruct",
      messages: [
        {
          role: "system",
          content: `Tu es un community manager expert en paris sportifs. Ton objectif : écrire un message attractif pour les membres du canal Kings pronos.
Le message doit : 
1. Inclure une promo irrésistible pour **AFROPARI**, en mentionnant :
   - Freebets pendant 1 semaine
   - Bonus de 300% à l'inscription
   - Meilleures cotes
   - Remboursement si 20 paris consécutifs sont perdus
   - Code promo obligatoire : ICEGAME
   - Lien : https://refpa84423.com/L?
2. Utiliser des emojis adaptés (flammes, football, argent, succès, etc.).
3. Varier le ton, le style et la mise en page à chaque génération pour que ça ne paraisse jamais répétitif.
4. Mentionner la date du jour : ${formattedDate}`
        },
        {
          role: "user",
          content: "Génère le message du jour complet."
        }
      ],
      temperature: 0.9,
      max_tokens: 300
    })
  });

  const data = await response.json();

  // Gestion d'erreur si l'API ne renvoie pas de choix
  if (!data.choices || !data.choices[0] || !data.choices[0].message) {
    console.error("❌ Réponse API Groq invalide :", data);
    return `🔥 Message du jour (${formattedDate}) : Rejoins Pari ALLIANCE pour profiter de tous les bonus et avantages AFROPARI ! 💸⚽️`;
  }

  return data.choices[0].message.content.trim();
}

(async () => {
  try {
    // Générer le message du jour
    const finalMessage = await generateDailyMessage();

    // Envoyer sur Telegram
    const bot = new TelegramBot(token, { polling: false });
    await bot.sendMessage(canal, finalMessage, { parse_mode: "Markdown" });

    console.log("✅ Message IA (promo AFROPARI avec date) envoyé !");
  } catch (err) {
    console.error("❌ Erreur :", err);
  }
})();
