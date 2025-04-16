import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

# โหลด Token จาก .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# กำหนด Intents และสร้าง Bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# View + Button สำหรับรับ Role
class RoleView(discord.ui.View):
    def __init__(self, role_id, button_text):
        super().__init__(timeout=None)
        self.role_id = role_id
        self.button_text = button_text
        self.add_item(self.RoleButton(label=self.button_text))

    class RoleButton(discord.ui.Button):
        def __init__(self, label):
            super().__init__(label=label, style=discord.ButtonStyle.success)

        async def callback(self, interaction: discord.Interaction):
            role = interaction.guild.get_role(self.view.role_id)
            if role is None:
                await interaction.response.send_message("❌ ไม่พบ Role นี้ในเซิร์ฟเวอร์", ephemeral=True)
                return
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(f"🧹 ลบ Role `{role.name}` เรียบร้อยแล้ว", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"✅ ได้รับ Role `{role.name}` แล้ว", ephemeral=True)

# คำสั่ง Slash: /setup
@bot.tree.command(name="setup", description="สร้างปุ่มกดรับ Role สำหรับสมาชิก")
@app_commands.describe(
    text="หัวข้อหลักของ Embed",
    description="รายละเอียดเนื้อหา",
    color="รหัสสี Hex เช่น #ff3333",
    image="ลิงก์รูปภาพหรือ GIF",
    button="ข้อความบนปุ่ม",
    addrole="ID ของ Role ที่ต้องการให้ผู้ใช้รับ"
)
async def setup(
    interaction: discord.Interaction,
    text: str,
    description: str,
    color: str,
    image: str,
    button: str,
    addrole: str
):
    # ✅ ตรวจสอบว่าเป็นเจ้าของเซิร์ฟเวอร์เท่านั้น
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ คำสั่งนี้ใช้ได้เฉพาะเจ้าของเซิร์ฟเวอร์เท่านั้น!", ephemeral=True)
        return

    try:
        role_id = int(addrole)
        color_int = int(color.replace("#", ""), 16)
    except:
        await interaction.response.send_message("❌ ตรวจสอบว่าใส่ `Role ID` และ `Color` ถูกต้อง (เช่น #ff0000)", ephemeral=True)
        return

    # สร้าง Embed
    embed = discord.Embed(
        title=f"# {text}",
        description=f"> {description}\n\n```md\n- กดปุ่มด้านล่างเพื่อรับ Role\n```",
        color=color_int
    )

    if image.startswith("http://") or image.startswith("https://"):
        embed.set_image(url=image)

    embed.set_footer(text=f"สร้างโดย: {interaction.user.name}", icon_url=interaction.user.avatar.url)


    # ส่ง Embed + ปุ่ม
    view = RoleView(role_id=role_id, button_text=button)
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ สร้างปุ่มกดรับ Role เรียบร้อยแล้ว", ephemeral=True)

# เมื่อบอทออนไลน์
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ บอทออนไลน์: {bot.user}")

# รันบอท
bot.run(TOKEN)
