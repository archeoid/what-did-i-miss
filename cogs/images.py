import discord

from discord.ext import commands
from services.api.all import *
from services.config import CONFIG

async def imgur_send(ctx, album_hash):
    download = not CONFIG["commands"]["images"]["link"]
    async with ctx.typing():
        gator = await get_image_from_album(album_hash, download)
        await send(ctx, gator, download)

async def send(ctx, f, download):
    if(download):
        await ctx.send(file=f)
    else:
        await ctx.send(f)

class Dog(commands.Cog):
    @commands.group(
        invoke_without_command=True,
        enabled = CONFIG["commands"]["dog"]["enabled"]
    )

    async def dog(self, ctx, gif=False):
        download = not CONFIG["commands"]["images"]["link"]
        async with ctx.typing():
            dog = await get_dog_image(gif, download)
            await send(ctx, dog, download)

    @dog.command(
        enabled = CONFIG["commands"]["dog"]["enabled"]
    )

    async def gif(self, ctx):
        await self.dog(ctx, True)

class Cat(commands.Cog):
    @commands.group(
        invoke_without_command=True,
        enabled = CONFIG["commands"]["cat"]["enabled"]
    )

    async def cat(self, ctx, gif=False):
        async with ctx.typing():
            cat = await get_cat_image(gif)
            await send(ctx, cat, True)

    @cat.command(
        enabled = CONFIG["commands"]["cat"]["enabled"]
    )

    async def gif(self, ctx):
        await self.cat(ctx, True)

class Gator(commands.Cog):
    @commands.group(
        invoke_without_command=True,
        enabled = CONFIG["commands"]["gator"]["enabled"],
        aliases = ["alligator"]
    )
    async def gator(self, ctx):
        "Post a gator pick, from an album provided by Gator#3220"
        await imgur_send(ctx, "cwnBW9Q")

    @gator.command(
        enabled = CONFIG["commands"]["gator"]["enabled"]
    )
    async def gif(self, ctx):
        await imgur_send(ctx, "lSQtPms")
