**Cloning from git to serv (first copy)**

1. execute
git clone https://github.com/arturfather/soccer_bot.git /root/my_bots/football_bot

2. enter username + token

Please mind gitignore list

============================================

**Activating venv_soccer**

1. activate venv soccer
 source /root/my_bots/football_bot/venv_soccer/bin/activate

2. change path
cd /root/my_bots/football_bot/


============================================


**Remove cached files so that they will be ignored in git ignore**

git rm --cached .\logs\ -r
git rm --cached .\jsons_data\ -r

============================================

**create  virtual env on WINDOWS and ACITVATE**

1. navigate to bot folder

2. execute
python -m venv venv_soccer

3. activate venv
.\venv_soccer\Scripts\activate

last argument is folder name, it might be any bot env like venv_volleyball, venv_soccer and so on


============================================

**create  virtual env on UBUNTU**

1. navigate to bot folder

python3 -m venv venv_soccer

last argument is folder name, it might be any bot env like venv_volleyball, venv_soccer and so on

============================================

**install requireremnts to VENV !**

pip install -r requirements.txt


============================================
