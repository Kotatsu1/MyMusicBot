import discord
from discord.ext import commands
import subprocess
import os
from controllers.silero import sound_ai
from controllers.stt import recognition

class AiView(discord.ui.View):

    def __init__(self, ctx, ai_listen, ai_stop):
        super().__init__()
        self.ctx = ctx
        self.ai_listen = ai_listen
        self.ai_stop = ai_stop

    @discord.ui.button(label="Start recording", style=discord.ButtonStyle.green)
    async def button_start(self, button, interaction: discord.Interaction):
        await interaction.response.send_message('Started recording')
        await self.ai_listen(self.ctx)

    @discord.ui.button(label="Stop recording", style=discord.ButtonStyle.red)
    async def button_end(self, button, interaction: discord.Interaction):
        await interaction.response.send_message('Stopped recording')
        await self.ai_stop(self.ctx)


class ai_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="ai")
    async def ai(self, ctx):
        view = AiView(ctx, self.ai_listen, self.ai_stop)
        await ctx.send(view=view)


    async def ai_listen(self, ctx):
        if ctx.voice_client:
            ctx.voice_client.start_recording(discord.sinks.WaveSink(), self.callback, ctx)
        else:
            await ctx.send("not in a voice channel!")


    async def ai_stop(self, ctx):
        ctx.voice_client.stop_recording()


    async def get_answer(self, ctx, text):
        vc = ctx.message.author.voice.channel
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice == None:
            await vc.connect()
        try:
            link = sound_ai(text)
            ctx.voice_client.play(discord.FFmpegPCMAudio(source=link))
        except Exception as ex:
            await ctx.send(ex)


    async def callback(self, sink: discord.sinks, ctx):
        for user_id, audio in sink.audio_data.items():
            if user_id == ctx.author.id:
                audio: discord.sinks.core.AudioData = audio
                
                if os.path.exists('pregenearted_sounds/mono.wav'):
                    os.remove('pregenearted_sounds/mono.wav')
                with open('pregenearted_sounds/stereo.wav', "wb") as f:
                    f.write(audio.file.getvalue())

                subprocess.call(["ffmpeg", "-loglevel", "panic", "-i", 'pregenearted_sounds/stereo.wav', "-map_channel", "0.0.0", 'pregenearted_sounds/mono.wav'])

                text = recognition()
                ctx.voice_client.play(discord.FFmpegPCMAudio(source='pregenearted_sounds/on_ready.wav'))
                await self.get_answer(ctx, text)
                

def setup(bot):
    bot.add_cog(ai_cog(bot))