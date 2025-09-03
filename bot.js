const TelegramBot = require('node-telegram-bot-api');

// Le token vient de GitHub Secrets
const token = process.env.TELEGRAM_BOT_TOKEN;

// Ton canal (public ou privé)
const canal = '@PariALLIANCE';

// Créer le bot sans polling (juste envoi)
const bot = new TelegramBot(token, { polling: false });

// Messages à alterner
const messages = [
  "🔥 Salut la team Pari ALLIANCE ! 🔥\n\n⏰ Petit rappel matinal : les pronostics du jour sont dispo **depuis 01h**.\nFoncez dans l'application Pari Alliance pour booster vos gains ! 💸⚽️\nBonne chance 🍀🚀",
  "🚨 Hey parieurs ! Les pronostics sont déjà disponibles depuis 01h !\nNe perdez pas de temps, c’est le moment de miser avec Pari Alliance. 🎯💰",
  "🌟 Nouvelle journée, nouvelle chance ! Les pronostics sont en ligne depuis 01h.\nRejoignez-nous sur l'app Pari Alliance et faites vibrer vos paris ! ⚽🔥",
  "⏰ C’est l’heure du rappel ! Les pronostics du jour vous attendent dans l'application Pari Alliance.\nPrenez l’avance dès maintenant et jouez malin ! 💪🍀",
];

// Choisir le message du jour selon la date
const day = new Date().getDate();
const message = messages[day % messages.length];

// Envoyer le message
bot.sendMessage(canal, message, { parse_mode: 'Markdown' })
  .then(() => console.log('✅ Message du jour envoyé avec succès !'))
  .catch(console.error);
