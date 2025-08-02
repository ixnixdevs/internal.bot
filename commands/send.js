import { SlashCommandBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } from 'discord.js';

export default {
  data: new SlashCommandBuilder()
    .setName('send')
    .setDescription('Starte die Erstellung eines Containers'),

  async execute(interaction, client) {
    // Neue Session starten
    client.sessions.set(interaction.user.id, {
      userId: interaction.user.id,
      components: [],
    });

    const row1 = new ActionRowBuilder().addComponents(
      new ButtonBuilder().setCustomId('add_text').setLabel('➕ Text').setStyle(ButtonStyle.Primary),
      new ButtonBuilder().setCustomId('add_file').setLabel('📎 Datei').setStyle(ButtonStyle.Secondary),
      new ButtonBuilder().setCustomId('add_separator').setLabel('➖ Separator').setStyle(ButtonStyle.Secondary),
    );

    const row2 = new ActionRowBuilder().addComponents(
      new ButtonBuilder().setCustomId('preview').setLabel('👁️ Vorschau').setStyle(ButtonStyle.Success),
      new ButtonBuilder().setCustomId('publish').setLabel('✅ Veröffentlichen').setStyle(ButtonStyle.Danger),
    );

    await interaction.reply({
      content: '🛠 Erstelle deinen Container mit den folgenden Optionen:',
      components: [row1, row2],
      ephemeral: true,
    });
  },
};
