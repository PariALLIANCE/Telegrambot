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
          content: "Tu es un community manager expert en paris sportifs. Ton objectif : écrire un message attractif pour les membres du canal Kings pronos.
            
            
        . Le message doit :\n1. Motiver les parieurs en annonçant que les pronostics sont disponibles depuis 01h.\n2. Inclure une promo irrésistible pour **AFROPARI**, en mentionnant :\n   - Freebets pendant 1 semaine\n   - Bonus de 300% à l'inscription\n   - Meilleures cotes\n   - Remboursement si 20 paris consécutifs sont perdus\n   - Code promo obligatoire : ICEGAME\n   - Lien : https://refpa84423.com/L?\n3. Utiliser des emojis adaptés (flammes, football, argent, succès, etc.).\n4. Varier le ton, le style et la mise en page à chaque génération pour que ça ne paraisse jamais répétitif."
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
  return data.choices[0].message.content.trim();
}

(async () => {
  try {
    // Générer le message du jour
    const finalMessage = await generateDailyMessage();

    // Envoyer sur Telegram
    const bot = new TelegramBot(token, { polling: false });
    await bot.sendMessage(canal, finalMessage, { parse_mode: "Markdown" });

    console.log("✅ Message IA (motivation + promo AFROPARI) envoyé !");
  } catch (err) {
    console.error("❌ Erreur :", err);
  }
})();
