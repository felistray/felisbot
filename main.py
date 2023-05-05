import discord
from discord.ext import commands
from discord.utils import get
import random
import json
import os

from config import TOKEN

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
intents.members = True

# Создание экземпляра клиента Discord
client = commands.Bot(command_prefix='!', intents=intents, guild_subscriptions=True)


# Загрузка списка ответов из файла responses.json
with open('responses.json', 'r', encoding='utf-8') as file:
    responses = json.load(file)


# Список ключевых слов
hello_words = ["hello", "hi", "Привет", "привет", "Приветик", "Hello", "Hi", "драсьте", "привет как дела"]
bye_words = ["пока", "до свидания", "bye", "бай"]


# Поздравление с ролью за активность
async def send_congratulations(channel, member, role):
    await channel.send(f"Ого, поздравляю, {member.mention}! Ты теперь у нас {role.mention}")


#запуск бота
@client.event
async def on_ready():
    print(f' {client.user.name} теперь онлайн')



#рандомное предсказание
@client.command(name='предсказание')
async def predict(ctx, *, question=None):
    if question:
        response = random.choice(responses)
        await ctx.send(f'Вопрос: {question}\nОтвет: {response}')
    else:
        await ctx.send('Пожалуйста, задайте вопрос после команды !предсказание')



# Функция для получения случайного изображения пиццы
def get_random_pizza_image():
    folder_path = 'pizza_images'  #Путь к папке с изображениями пиццы
    file_names = os.listdir(folder_path)
    random_file = random.choice(file_names)
    file_path = os.path.join(folder_path, random_file)
    return file_path

@client.command(name='пицца')
async def pizza(ctx):
    pizza_image_path = get_random_pizza_image()
    pizza_image = discord.File(pizza_image_path)
    await ctx.send(file=pizza_image)


#приветствие новых пользователей
@client.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel is not None:
        await channel.send(f'Привет-привет, {member.mention}! Добро пожаловать к нам на тестирование!')




#ответ на сообщение
@client.event
async def on_message(message):
    global new_role_added
    if not message.author.bot and not message.content.startswith('!'):
        user_id = str(message.author.id)
        if not os.path.exists('activity.json'):
            data = {}
        else:
            with open('activity.json', 'r') as file:
                data = json.load(file)

        if user_id not in data:
            data[user_id] = 0

        data[user_id] += 1
        with open('activity.json', 'w') as file:
            json.dump(data, file, indent=4)

        # роль старожил
        if data[user_id] >= 10:
            role = get(message.guild.roles, name='Старожил')
            if role is not None and role not in message.author.roles:
                # Удаляем роль "Активный участник" при присвоении роли "Старожил"
                role2 = get(message.guild.roles, name='Активный участник')
                if role2 is not None and role2 in message.author.roles:
                    await message.author.remove_roles(role2)

                await message.author.add_roles(role)
                congratulations_channel = client.get_channel(1103737250308698142)
                if congratulations_channel is not None:
                    await send_congratulations(congratulations_channel, message.author, role)

        elif data[user_id] >=  5:
            role = get(message.guild.roles, name='Активный участник')
            if role is not None and role not in message.author.roles:
                # Проверяем наличие роли "Новичок" у участника
                role_newcomer = get(message.guild.roles, name='Новенький')
                if role_newcomer is not None and role_newcomer in message.author.roles:
                    await message.author.remove_roles(role_newcomer)

                await message.author.add_roles(role)
                congratulations_channel = client.get_channel(1103737250308698142)
                if congratulations_channel is not None:
                    await send_congratulations(congratulations_channel, message.author, role)


        # роль новичок
        if data[user_id] == 1:
            role = get(message.guild.roles, name='Новенький')
            if role is not None and role not in message.author.roles:
                role2 = get(message.guild.roles, name='Активный участник')
                if role2 is not None and role2 in message.author.roles:
                    await message.author.remove_roles(role2)

                await message.author.add_roles(role)
                congratulations_channel = client.get_channel(1103737250308698142)
                if congratulations_channel is not None:
                    await send_congratulations(congratulations_channel, message.author, role)

    # ответы на сообщения
    if message.author == client.user:
        return

    msg = message.content.lower()
    msg_list = msg.split()

    # приветствие
    find_hello_words = False
    for item in hello_words:
        if msg.find(item) >= 0:
            find_hello_words = True
    if find_hello_words:
        await message.channel.send(f' Приветики-пистолетики, {message.author.mention} !Я Паймон. Попробуй команду !помощь, чтобы увидеть, что я умею!')


    # прощание
    for item in bye_words:
        if item in msg_list:
            await message.channel.send(f'Уже уходишь? Ну досвидосики, {message.author.mention}')
            return

    await client.process_commands(message)


#выдача ролей по реакции
@client.event
async def on_raw_reaction_add(payload):
    guild = client.get_guild(payload.guild_id)
    member = await guild.fetch_member(payload.user_id)

    if payload.message_id == 1097416758220029972:
        if payload.emoji.name == '✨':
            print('успех!')
            role = get(guild.roles, id=1097436146058932275)
            print(member)
            await member.add_roles(role)
            print(f"{member.name} получает роль {role.name}")
            await guild.chunk()
            channel = client.get_channel(1072454367720001556)
            await channel.send(f"Ого, ничоси, {member.mention} теперь у нас {role.mention}!")

#команда проверки активности
@client.command(name='активность')
async def activity(ctx):
    user_id = str(ctx.author.id)
    with open('activity.json', 'r') as file:
        data = json.load(file)

    if user_id in data:
        points = data[user_id]
        message = f"{ctx.author.mention}, у тебя {points} баллов активности!"
        await ctx.send(message)

    else:
        await ctx.send("У тебя еще нет баллов активности.")


#команда помощи
@client.command()
async def помощь(ctx):
    role_newcomer = discord.utils.get(ctx.guild.roles, name='Новенький')
    role_active = discord.utils.get(ctx.guild.roles, name='Активный участник')
    role_veteran = discord.utils.get(ctx.guild.roles, name='Старожил')
    role_tester = discord.utils.get(ctx.guild.roles, name='тестировщик')

    channel_role = client.get_channel(1072454367720001556)

    await ctx.send(f"✨   Хэй-хэй! Вот информация о нашем сервере!:\n"
                   f"✨   За активность в чате ты можешь получить три разных роли:\n"
                   f"   {role_newcomer.mention} - для новых участников\n"
                   f"   {role_active.mention} - для тех, кто у нас уже некоторое время\n"
                   f"   {role_veteran.mention} - для старичков\n"
                   f"✨  Чтобы получить роль {role_tester.mention}, перейди в канал {channel_role.mention} и нажми на реакцию\n"
                   f"✨  Вот мой список команд: \n"
                   f"    !активность - проверяет твою активность в чате \n"
                   f"    !предсказание - задай вопрос после команды и получишь ответ \n"
                   f"    !пицца - а попробуй заказать себе пиццу? \n"
                   )

@client.command()
async def конецтеста(ctx):
    # Проверяем, что команда была вызвана автором сообщения
    if ctx.author == ctx.message.author:
        # Получаем роль "айтишник" по ее имени
        role_it = discord.utils.get(ctx.guild.roles, name='айтишник')

        # Получаем пользователя, которому нужно выдать роль
        user = ctx.guild.get_member(713770196585807872)

        # Проверяем, что роль и пользователь существуют
        if role_it is not None and user is not None:
            # Выдаем роль пользователю
            await user.add_roles(role_it)
            await ctx.send(f"Урааааа! Тестирование закончено! Давайте поздравим {user.mention}. Она успешно презентовала проект и получила роль {role_it.mention}")
        else:
            await ctx.send("Не удалось выдать роль айтишника. Проверьте наличие роли и правильность команды.")
    else:
        await ctx.send("Эту команду может выполнить только автор сообщения.")



@client.event
async def on_disconnect():
    save_chat_activity(chat_activity)


client.run(TOKEN)