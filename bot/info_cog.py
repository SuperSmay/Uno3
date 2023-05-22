import discord
from discord.ext import commands
import datetime  # type: ignore

import bot.global_variables as global_variables

class InfoCog(commands.Cog):

    def __init__(self, bot: discord.Bot):
        self.bot: discord.Bot = bot

    @commands.slash_command(name="info", description="Display some bot information")
    async def info_command(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(title="Bot Information")
        embed.add_field(name="Ping", value=f"{round(self.bot.latency*1000, 2)}ms")
        embed.add_field(name="Uptime", value=self.parse_duration((datetime.datetime.utcnow() - global_variables.start_time).total_seconds()))
        embed.add_field(name="Version", value=global_variables.version)
        embed.set_footer(text=f"@{self.bot.user.name if self.bot.user is not None else 'Unknown'} - {self.bot.user.id if self.bot.user is not None else 0}")

        await ctx.respond(embed=embed)





    # Once again, thanks Raya for this one
    def parse_duration(self, duration: float) -> str:
        """
        Converts a time in seconds to a string in the format hr:min:sec, or min:sec if less than one hour

        Args:
            duration (int): The time in seconds

        Returns:
            str: A string in the format hr:min:sec, or min:sec if less than one hour
        """

        #Divides everything into hours, minutes, and seconds
        hours = duration // 3600
        temp_time = duration % 3600 #Modulo takes the remainder of division, leaving the remaining minutes after all hours are taken out
        minutes = temp_time // 60
        seconds = round(temp_time % 60)

        #Formats time into a readable string
        new_time = ""
        if hours > 0: #Adds hours to string if hours are available; else this will just be blank
            new_time += str(hours) + ":"
        else: #If there are no hours, the place still needs to be held
            new_time += "00:"

        if minutes > 0:
            if minutes < 10: #Adds a 0 to one-digit times
                new_time += "0" + str(minutes) + ":"
            else:
                new_time += str(minutes) +":"
        else: #If there are no minutes, the place still needs to be held
            new_time += "00:"

        if seconds > 0:
            if seconds < 10: #Adds a 0 to one-digit times
                new_time += "0" + str(seconds)
            else:
                new_time += str(seconds)
        else:
            new_time += "00"

        return new_time



def setup(bot: discord.Bot):
    bot.add_cog(InfoCog(bot))