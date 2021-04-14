# Natalia
私用のDiscord Botです。

[discord.py](https://discordpy.readthedocs.io/ja/latest/index.html)によるフレームワーク[discord.ext.commands](https://discordpy.readthedocs.io/ja/latest/ext/commands/index.html)をフル活用しています。

## 機能
```
!help

AmongUs:
  mover     リアクションを押してほしいナ！
Hello:
  hello     
YouTube:
  superchat センキュー・スパチャ♪ ┗(┓卍^o^)卍ﾄﾞｩﾙﾙﾙﾙﾙﾙ↑↑
No Category:
  help      Shows this message
ソーシャルディスタンス:
  team      チーム分けをするヨ！
麻雀:
  今日の役  タンヤオ！って言えばいいのカ？
```

## Developers
### Start container
```
# Set DISCORD_TOKEN or create .env

docker-compose up -d --build
# launch codeserver at http://localhost:8080
# or
docker-compose up -d app

docker-compose exec app bash

# in container
python natalia.py
```

Thanks! @max-koara, @Sonochy

### Start local
```
# Set DISCORD_TOKEN

pip install poetry
poetry install
poetry run python natalia.py
```

### Branch Rule
developブランチにPR送ってください

- master
- develop
  - release (--> master, develop)
  - feature (--> develop)
