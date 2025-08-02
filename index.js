import { Client, GatewayIntentBits, Collection, REST, Routes, Events } from 'discord.js';
import fs from 'fs';
import path from 'path';
import 'dotenv/config';

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

client.commands = new Collection();
client.sessions = new Map(); // Session per User

// Lade Commands
const commandsPath = './commands';
const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));
const commands = [];

for (const file of commandFiles) {
  const command = await import(`./commands/${file}`);
  client.commands.set(command.default.data.name, command.default);
  commands.push(command.default.data.toJSON());
}

// Registriere Commands
const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);
await rest.put(
  Routes.applicationGuildCommands(process.env.CLIENT_ID, process.env.GUILD_ID),
  { body: commands }
);

console.log('✅ Slash Commands registriert');

// Interaktionen
client.on(Events.InteractionCreate, async interaction => {
  if (interaction.isChatInputCommand()) {
    const command = client.commands.get(interaction.commandName);
    if (command) await command.execute(interaction, client);
  }

  // Modal-Handling
  else if (interaction.isModalSubmit()) {
    const session = client.sessions.get(interaction.user.id);
    if (!session) return;

    if (interaction.customId === 'addTextModal') {
      const text = interaction.fields.getTextInputValue('textcontent');
      session.components.push({
        type: 'text',
        content: text,
      });
      await interaction.reply({ content: '✅ Text hinzugefügt.', ephemeral: true });
    }

    if (interaction.customId === 'addFileModal') {
      const url = interaction.fields.getTextInputValue('fileurl');
      session.components.push({
        type: 'file',
        url,
      });
      await interaction.reply({ content: '✅ Datei hinzugefügt.', ephemeral: true });
    }
  }

  // Button-Handling
  else if (interaction.isButton()) {
    const session = client.sessions.get(interaction.user.id);
    if (!session) return;

    if (interaction.customId === 'add_text') {
      const { ModalBuilder, TextInputBuilder, TextInputStyle, ActionRowBuilder } = await import('discord.js');
      const modal = new ModalBuilder()
        .setCustomId('addTextModal')
        .setTitle('Text hinzufügen');

      const input = new TextInputBuilder()
        .setCustomId('textcontent')
        .setLabel('Textinhalt')
        .setStyle(TextInputStyle.Paragraph)
        .setRequired(true);

      const row = new ActionRowBuilder().addComponents(input);
      modal.addComponents(row);
      await interaction.showModal(modal);
    }

    if (interaction.customId === 'add_separator') {
      session.components.push({ type: 'separator' });
      await interaction.reply({ content: '➖ Separator hinzugefügt.', ephemeral: true });
    }

    if (interaction.customId === 'add_file') {
      const { ModalBuilder, TextInputBuilder, TextInputStyle, ActionRowBuilder } = await import('discord.js');
      const modal = new ModalBuilder()
        .setCustomId('addFileModal')
        .setTitle('Datei anhängen');

      const input = new TextInputBuilder()
        .setCustomId('fileurl')
        .setLabel('URL zu Datei')
        .setStyle(TextInputStyle.Short)
        .setRequired(true);

      const row = new ActionRowBuilder().addComponents(input);
      modal.addComponents(row);
      await interaction.showModal(modal);
    }

    if (interaction.customId === 'preview') {
      const { ContainerBuilder, TextDisplayBuilder, SeparatorBuilder, SeparatorSpacingSize, FileBuilder } = await import('discord.js');

      const container = new ContainerBuilder();

      for (const comp of session.components) {
        if (comp.type === 'text') {
          container.addTextDisplayComponents(
            new TextDisplayBuilder().setContent(comp.content)
          );
        } else if (comp.type === 'separator') {
          container.addSeparatorComponents(
            new SeparatorBuilder().setSpacing(SeparatorSpacingSize.Small).setDivider(true)
          );
        } else if (comp.type === 'file') {
          container.addFileComponents(
            new FileBuilder().setURL(comp.url)
          );
        }
      }

      await interaction.reply({
        content: '👁️ Vorschau deines Containers:',
        components: [container],
        ephemeral: true,
      });
    }

    if (interaction.customId === 'publish') {
      const { ContainerBuilder, TextDisplayBuilder, SeparatorBuilder, SeparatorSpacingSize, FileBuilder } = await import('discord.js');

      const container = new ContainerBuilder();

      for (const comp of session.components) {
        if (comp.type === 'text') {
          container.addTextDisplayComponents(
            new TextDisplayBuilder().setContent(comp.content)
          );
        } else if (comp.type === 'separator') {
          container.addSeparatorComponents(
            new SeparatorBuilder().setSpacing(SeparatorSpacingSize.Small).setDivider(true)
          );
        } else if (comp.type === 'file') {
          container.addFileComponents(
            new FileBuilder().setURL(comp.url)
          );
        }
      }

      await interaction.reply({
        content: '📦 Container veröffentlicht:',
        components: [container],
      });

      client.sessions.delete(interaction.user.id);
    }
  }
});

client.once('ready', () => {
  console.log(`🤖 Eingeloggt als ${client.user.tag}`);
});

client.login(process.env.DISCORD_TOKEN);
