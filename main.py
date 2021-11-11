import discord
from discord.ext import commands
from discord.http import Route
import uuid

bot = commands.Bot(command_prefix='p!')
bot.poll_data = {}


def make_buttons(tag, data):
    splited_data = [data[i * 5:(i + 1) * 5] for i in range((len(data) + 5 - 1) // 5 )]
    components = []
    for i in splited_data:
        buttons = []

        for j in i:
            buttons.append({
                'type': 2,
                'style': 2,
                'custom_id': f'{tag}.{j["id"]}',
                'label': j['name']
            })

        components.append({
            'type': 1,
            'components': buttons
        })
    return components


@bot.command('poll')
async def poll(ctx, title, *names):
    poll_id = uuid.uuid4().hex

    data = []
    bot.poll_data[poll_id] = {
        'title': title,
        'items': {}
    }

    for i in names:
        item_id = uuid.uuid4().hex
        bot.poll_data[poll_id]['items'][f'{poll_id}.{item_id}'] = {
            'name': i,
            'users': []
        }
        data.append({ 'name': i, 'id': item_id })

    embed = discord.Embed(
        title=title,
        description="\n".join(map(lambda x: f'`{x}` : 0 votes', names)),
        color=0x58D68D
    )
    embed.set_footer(text='Making polls now are more easy :D| Programmed by The Dark Side#3255')

    route = Route('POST', '/channels/{channel_id}/messages', channel_id=ctx.channel.id)
    await bot.http.request(route, json={
        'embed': embed.to_dict(),
        'components': make_buttons(poll_id, data)
    })


@bot.event
async def on_socket_response(msg):
    if msg['t'] != 'INTERACTION_CREATE': return
    full_id = msg['d']['data']['custom_id']
    poll_id = full_id.split('.')[0]
    if not bot.poll_data.get(poll_id): return
    data = bot.poll_data[poll_id]
    user_id = msg['d']['member']['user']['id']
    if user_id in data['items'][full_id]['users']:
        bot.poll_data[poll_id]['items'][full_id]['users'].remove(user_id)
    else:
        bot.poll_data[poll_id]['items'][full_id]['users'].append(user_id)
    
    embed = msg['d']['message']['embeds'][0]
    content = "\n".join(map(lambda x: f'`{data["items"][x]["name"]}` : {len(data["items"][x]["users"])}', data['items']))
    embed['description'] = content

    route = Route('PATCH', '/channels/{channel_id}/messages/{message_id}', channel_id=msg['d']['channel_id'], message_id=msg['d']['message']['id'])
    await bot.http.request(route, json={
        'embed': embed,
        'components': msg['d']['message']['components']
    })


bot.run('Yourtokenhere')

